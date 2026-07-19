import asyncio
import logging
import os
import signal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from tracker.models import Activity, Goal, KeyValuePair
from tracker.gap_filler import log_activity_gap_filled
from tracker.trajectory import get_trajectory

# Configure logging — level controlled by LOG_LEVEL env var
log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    level=getattr(logging, log_level, logging.INFO)
)
logger = logging.getLogger(__name__)
logger.info("Log level set to %s", log_level)

class Command(BaseCommand):
    help = 'Runs the Telegram bot'

    def handle(self, *args, **options):
        token = os.environ.get('TELEGRAM_BOT_API_KEY')
        if not token:
            self.stderr.write('TELEGRAM_BOT_API_KEY not found in environment variables')
            return

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.main(token))
        finally:
            loop.close()

    async def main(self, token):
        application = ApplicationBuilder().token(token).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("now", self.now))
        application.add_handler(CommandHandler("status", self.status))
        application.add_handler(CommandHandler("undo", self.undo))
        application.add_handler(CommandHandler("last", self.last))
        application.add_handler(CommandHandler("top", self.top))
        application.add_handler(CommandHandler("budget", self.budget))
        application.add_handler(CommandHandler("trajectory", self.trajectory))
        
        # Handler for text messages (treating them as /now or notes)
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))
        application.add_handler(CallbackQueryHandler(self.button_callback))

        # Log all non-command text updates for debugging
        async def log_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
            chat = update.effective_chat
            user = update.effective_user
            if update.message and update.message.text:
                logger.info("Received: chat_id=%s user=%s text=%s",
                            chat.id if chat else None,
                            user.username if user else None,
                            update.message.text)
            return
        application.add_handler(MessageHandler(filters.TEXT, log_update), group=-1)

        # Background job for periodic checks
        if application.job_queue:
            application.job_queue.run_repeating(self.periodic_check, interval=60, first=10)

        logger.info("Bot started")

        # Signal handling for graceful shutdown
        stop_future = asyncio.get_running_loop().create_future()
        for sig in (signal.SIGTERM, signal.SIGINT):
            try:
                asyncio.get_running_loop().add_signal_handler(
                    sig, lambda: stop_future.set_result(True)
                )
            except (NotImplementedError, ValueError):
                pass

        await application.initialize()
        await application.start()
        await application.updater.start_polling()

        try:
            await stop_future
        finally:
            await application.updater.stop()
            await application.stop()
            await application.shutdown()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        await asyncio.to_thread(self.seed_defaults, chat_id)
        await update.message.reply_text(
            f"Welcome to Waste No Time! Your Chat ID is {chat_id}.\n"
            "Default categories have been initialized.\n"
            "Use /now <tag> to start an activity.\n"
            "Type /help to see all commands."
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🧭 *Waste No Time Commands*\n\n"
            "/start - Initialize your account\n"
            "/now <tag>[, notes] - Start a new activity\n"
            "/last - Show recent activities\n"
            "/status - Show current activity status\n"
            "/top - Show top activities today\n"
            "/budget - Show time budgets vs actual\n"
            "/trajectory - Show trajectory forecast\n"
            "/undo - Undo last activity\n"
            "/settings - Configure check interval and on/off\n"
            "/key <key>, <value> - Set a key-value pair\n"
            "/help - Show this message\n\n"
            "Just type an activity name to start tracking it.",
            parse_mode='Markdown'
        )

    async def settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        logger.info("Settings command from chat_id=%s", chat_id)
        try:
            ci = await asyncio.to_thread(self.get_kv, chat_id, "ci") or "600"
            mt = await asyncio.to_thread(self.get_kv, chat_id, "mt") or "on"
            status_icon = "✅ ON" if mt == "on" else "❌ OFF"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"Check interval: {ci}s", callback_data="noop")],
                [
                    InlineKeyboardButton(f"10min", callback_data="key:ci:600"),
                    InlineKeyboardButton(f"15min", callback_data="key:ci:900"),
                    InlineKeyboardButton(f"30min", callback_data="key:ci:1800"),
                ],
                [
                    InlineKeyboardButton(f"⏸ Pause" if mt == "on" else "▶ Resume",
                                         callback_data="toggle:mt"),
                ],
            ])
            await update.message.reply_text(
                f"⚙️ *Settings*\n"
                f"Check interval: `{ci}s`\n"
                f"Periodic check: {status_icon}\n\n"
                f"The bot will ask what you're doing every {ci}s if check is on.",
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            logger.info("Settings sent to chat_id=%s (ci=%s, mt=%s)", chat_id, ci, mt)
        except Exception as e:
            logger.exception("Settings failed for chat_id=%s: %s", chat_id, e)

    async def key_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        text = " ".join(context.args)
        if not text:
            await update.message.reply_text(
                "Usage: /key <key>, <value>\n"
                "Example: /key ci, 900  (set check interval to 15 min)\n"
                "         /key mt, off  (disable periodic checks)"
            )
            return
        try:
            key = text.split(",")[0].strip()
            value = text.split(",")[1].strip()
            await asyncio.to_thread(self.set_kv, chat_id, key, value)
            await update.message.reply_text(f"✅ `{key}` = `{value}`", parse_mode='Markdown')
        except (IndexError, ValueError):
            # Get value
            key = text.split(",")[0].strip()
            val = await asyncio.to_thread(self.get_kv, chat_id, key)
            if val is not None:
                await update.message.reply_text(f"`{key}` = `{val}`", parse_mode='Markdown')
            else:
                await update.message.reply_text(f"Key `{key}` not found", parse_mode='Markdown')

    def seed_defaults(self, chat_id):
        # Seed default goals if they don't exist
        defaults = [
            ("Sleep", 8, "day"),
            ("Programming", 4, "day"),
            ("Exercise", 0.5, "day"),
            ("Reading", 1, "day"),
        ]
        for name, hours, period in defaults:
            Goal.objects.get_or_create(
                telegram_chat_id=chat_id,
                category=name,
                period=period,
                defaults={'target_hours': hours, 'name': f"{name} daily goal"}
            )
        
        # Set defaults
        self.set_kv(chat_id, "ci", "600")
        self.set_kv(chat_id, "mt", "on")

    async def now(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        text = " ".join(context.args)
        if not text:
            # If no args, show keyboard
            keyboard = await self.get_keyboard(chat_id)
            await update.message.reply_text("Choose an activity:", reply_markup=keyboard)
            return

        parts = text.split(',', 1)
        tag = parts[0].strip()
        notes = parts[1].strip() if len(parts) > 1 else None

        await self.log_now(chat_id, tag, notes, update)

    async def log_now(self, chat_id, tag, notes, update_or_query):
        # Rate limit check (10 seconds)
        last_called = await asyncio.to_thread(self.get_kv, chat_id, "last_called")
        now_ts = timezone.now().timestamp()
        if last_called and (now_ts - float(last_called)) < 10:
            msg = "Please wait at least 10 seconds between /now calls."
            if hasattr(update_or_query, 'message'):
                await update_or_query.message.reply_text(msg)
            else:
                await update_or_query.answer(msg, show_alert=True)
            return

        activity = await asyncio.to_thread(log_activity_gap_filled, chat_id, tag, notes)
        await asyncio.to_thread(self.set_kv, chat_id, "last_called", str(now_ts))
        
        today_total = await asyncio.to_thread(self.get_today_total, chat_id, tag)
        keyboard = await self.get_keyboard(chat_id)
        
        text = (f"Started: {tag}\n"
                f"Start time: {activity.start_time.strftime('%H:%M')}\n"
                f"Today's total: {today_total}\n\n"
                "In the present moment, there are no problems.")
        
        if hasattr(update_or_query, 'message') and update_or_query.message:
            await update_or_query.message.reply_text(text, reply_markup=keyboard)
        elif hasattr(update_or_query, 'edit_message_text'):
            await update_or_query.edit_message_text(text, reply_markup=keyboard)

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        last_activity = await asyncio.to_thread(
            lambda: Activity.objects.filter(telegram_chat_id=chat_id).order_by('-end_time').first()
        )
        if not last_activity:
            await update.message.reply_text("No activities recorded yet.")
            return

        await update.message.reply_text(
            f"Last activity: {last_activity.name}\n"
            f"Finished at: {last_activity.end_time.strftime('%H:%M')}\n"
            f"Duration: {last_activity.duration}"
        )

    async def undo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        last_activity = await asyncio.to_thread(
            lambda: Activity.objects.filter(telegram_chat_id=chat_id).order_by('-end_time').first()
        )
        if last_activity:
            name = last_activity.name
            await asyncio.to_thread(last_activity.delete)
            await update.message.reply_text(f"Deleted last activity: {name}")
        else:
            await update.message.reply_text("No activities to undo.")

    async def last(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        activities = await asyncio.to_thread(
            lambda: list(Activity.objects.filter(telegram_chat_id=chat_id).order_by('-end_time')[:10])
        )
        if not activities:
            await update.message.reply_text("No activities found.")
            return
        
        text = "Last 10 activities:\n"
        for act in activities:
            text += f"{act.start_time.strftime('%H:%M')} - {act.end_time.strftime('%H:%M')} : {act.name}\n"
        await update.message.reply_text(text)

    async def top(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        # Simple top categories for last 24h
        now = timezone.now()
        yesterday = now - timedelta(days=1)
        activities = await asyncio.to_thread(
            lambda: list(Activity.objects.filter(telegram_chat_id=chat_id, start_time__gte=yesterday))
        )
        
        totals = {}
        for act in activities:
            if act.duration:
                totals[act.name] = totals.get(act.name, timedelta()) + act.duration
        
        sorted_totals = sorted(totals.items(), key=lambda x: x[1], reverse=True)
        text = "Top activities (last 24h):\n"
        for tag, dur in sorted_totals:
            hours = dur.total_seconds() // 3600
            minutes = (dur.total_seconds() % 3600) // 60
            text += f"{tag}: {int(hours)}h {int(minutes)}m\n"
        
        await update.message.reply_text(text)

    async def budget(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        tag = " ".join(context.args)
        if not tag:
            await update.message.reply_text("Please specify a tag: /budget <tag>")
            return
        
        today_total = await asyncio.to_thread(self.get_today_total, chat_id, tag)
        # 7 days total
        now = timezone.now()
        last_week = now - timedelta(days=7)
        week_activities = await asyncio.to_thread(
            lambda: list(Activity.objects.filter(telegram_chat_id=chat_id, name=tag, start_time__gte=last_week))
        )
        week_dur = timedelta()
        for act in week_activities:
            if act.duration:
                week_dur += act.duration
        
        week_hours = week_dur.total_seconds() // 3600
        week_minutes = (week_dur.total_seconds() % 3600) // 60
        
        await update.message.reply_text(
            f"Budget for {tag}:\n"
            f"Today: {today_total}\n"
            f"Last 7 days: {int(week_hours)}h {int(week_minutes)}m"
        )

    async def trajectory(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        category = " ".join(context.args)
        if not category:
            # If no category, show for all active categories
            categories = await asyncio.to_thread(
                lambda: list(Activity.objects.filter(telegram_chat_id=chat_id).values_list('name', flat=True).distinct())
            )
            if not categories:
                await update.message.reply_text("No activities recorded yet.")
                return
            
            text = "Trajectory Summary (Monthly):\n\n"
            for cat in categories:
                traj = await asyncio.to_thread(get_trajectory, chat_id, cat, 'month')
                text += f"*{cat}*\n"
                text += f"Actual: {traj['actual_so_far_hours']:.1f}h / Forecast: {traj['forecast_total_hours']:.1f}h\n"
                text += f"Goal: {traj['goal_target_hours']:.1f}h / Status: {traj['status']}\n\n"
            
            await update.message.reply_text(text, parse_mode='Markdown')
            return

        traj = await asyncio.to_thread(get_trajectory, chat_id, category, 'month')
        text = (f"Trajectory for *{category}*:\n"
                f"Actual so far: {traj['actual_so_far_hours']:.2f}h\n"
                f"Recent daily pace: {traj['recent_pace_hours']:.2f}h/day\n"
                f"Forecasted total: {traj['forecast_total_hours']:.2f}h\n"
                f"Goal target: {traj['goal_target_hours']:.2f}h\n"
                f"Forecast gap: {traj['forecast_gap_hours']:.2f}h\n"
                f"Required daily pace: {traj['required_daily_pace_hours']:.2f}h/day\n"
                f"Status: {traj['status']}")
        
        await update.message.reply_text(text, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Treat plain text as /now command
        context.args = update.message.text.split()
        await self.now(update, context)

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        data = query.data
        chat_id = update.effective_chat.id
        if data == "noop":
            return
        if data.startswith("now:"):
            tag = data.split(":", 1)[1]
            await self.log_now(chat_id, tag, None, query)
        elif data.startswith("key:"):
            parts = data.split(":")
            key = parts[1]
            value = parts[2]
            await asyncio.to_thread(self.set_kv, chat_id, key, value)
            await query.message.reply_text(f"✅ `{key}` set to `{value}`", parse_mode='Markdown')
        elif data.startswith("toggle:"):
            key = data.split(":", 1)[1]
            current = await asyncio.to_thread(self.get_kv, chat_id, key) or "on"
            new_val = "off" if current == "on" else "on"
            await asyncio.to_thread(self.set_kv, chat_id, key, new_val)
            status = "✅ ON" if new_val == "on" else "❌ OFF"
            await query.message.reply_text(f"Periodic check: {status}", parse_mode='Markdown')

    async def get_keyboard(self, chat_id):
        recent_activities = await asyncio.to_thread(
            lambda: list(Activity.objects.filter(telegram_chat_id=chat_id)
                         .order_by('-end_time')
                         .values_list('name', flat=True))
        )
        
        unique_tags = []
        for tag in recent_activities:
            if tag not in unique_tags:
                unique_tags.append(tag)
            if len(unique_tags) >= 6:
                break
        
        if not unique_tags:
            unique_tags = ["Programming", "Sleep", "Exercise", "Reading", "Food", "Family"]

        keyboard = []
        for i in range(0, len(unique_tags), 2):
            row = [InlineKeyboardButton(unique_tags[i], callback_data=f"now:{unique_tags[i]}")]
            if i + 1 < len(unique_tags):
                row.append(InlineKeyboardButton(unique_tags[i+1], callback_data=f"now:{unique_tags[i+1]}"))
            keyboard.append(row)
        
        return InlineKeyboardMarkup(keyboard)

    async def periodic_check(self, context: ContextTypes.DEFAULT_TYPE):
        chat_ids = await asyncio.to_thread(
            lambda: list(Activity.objects.values_list('telegram_chat_id', flat=True).distinct())
        )
        
        for chat_id in chat_ids:
            if not chat_id: continue
            
            # Skip if user has disabled periodic checks
            mt = await asyncio.to_thread(self.get_kv, chat_id, "mt") or "on"
            if mt != "on":
                continue
            
            last_called = await asyncio.to_thread(self.get_kv, chat_id, "last_called")
            ci = await asyncio.to_thread(self.get_kv, chat_id, "ci") or "600"
            
            now_ts = timezone.now().timestamp()
            if last_called and (now_ts - float(last_called)) > int(ci):
                keyboard = await self.get_keyboard(chat_id)
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text="What are you doing now?\nIn the present moment, there are no problems.",
                        reply_markup=keyboard
                    )
                    await asyncio.to_thread(self.set_kv, chat_id, "last_called", str(now_ts))
                except Exception as e:
                    logger.error(f"Failed to send periodic check to {chat_id}: {e}")

    def get_today_total(self, chat_id, tag):
        now = timezone.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        activities = Activity.objects.filter(
            telegram_chat_id=chat_id,
            name=tag,
            start_time__gte=start_of_day
        )
        total_duration = timedelta()
        for act in activities:
            if act.duration:
                total_duration += act.duration
        
        hours = total_duration.total_seconds() // 3600
        minutes = (total_duration.total_seconds() % 3600) // 60
        return f"{int(hours)}h {int(minutes)}m"

    def get_kv(self, chat_id, key):
        try:
            return KeyValuePair.objects.get(telegram_chat_id=chat_id, key=key).value
        except KeyValuePair.DoesNotExist:
            return None

    def set_kv(self, chat_id, key, value):
        KeyValuePair.objects.update_or_create(
            telegram_chat_id=chat_id, key=key, defaults={'value': value}
        )
