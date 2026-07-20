import asyncio
import io
import logging
import os
import random
import signal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
import pytz

from tracker.models import Activity, Goal, KeyValuePair
from tracker.gap_filler import log_activity_gap_filled
from tracker.trajectory import get_trajectory

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Configure logging — level controlled by LOG_LEVEL env var
log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    level=getattr(logging, log_level, logging.INFO)
)
logger = logging.getLogger(__name__)
logger.info("Log level set to %s", log_level)

def human_interval(seconds):
    """Convert seconds to a human-friendly label."""
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    return f"{minutes} min"


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
        application.add_handler(CommandHandler("settings", self.settings))
        application.add_handler(CommandHandler("tz", self.tz_command))
        application.add_handler(CommandHandler("key", self.key_command))
        
        # Handler for text messages (treating them as /now or notes)
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))
        application.add_handler(CallbackQueryHandler(self.button_callback))

        # Background job for periodic checks
        if application.job_queue:
            application.job_queue.run_repeating(self.periodic_check, interval=10, first=10)

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
            "Type /help to see all commands.",
            reply_markup=ReplyKeyboardRemove()
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
            "/settings - Configure check interval and timezone\n"
            "/tz <zone> - Set your timezone (e.g. Pacific/Auckland)\n"
            "/key <key>, <value> - Set a key-value pair (ci: 15–600s)\n"
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
            tz_name = await asyncio.to_thread(self.get_kv, chat_id, "tz") or "UTC"
            status_icon = "✅ ON" if mt == "on" else "❌ OFF"
            ci_int = int(ci)
            ci_label = human_interval(ci_int)
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("15s", callback_data="key:ci:15"),
                    InlineKeyboardButton("30s", callback_data="key:ci:30"),
                    InlineKeyboardButton("1 min", callback_data="key:ci:60"),
                ],
                [
                    InlineKeyboardButton("2 min", callback_data="key:ci:120"),
                    InlineKeyboardButton("5 min", callback_data="key:ci:300"),
                    InlineKeyboardButton("10 min", callback_data="key:ci:600"),
                ],
                [
                    InlineKeyboardButton("⏸ Pause checks" if mt == "on" else "▶ Resume checks",
                                         callback_data="toggle:mt"),
                ],
                [
                    InlineKeyboardButton("UTC", callback_data="key:tz:UTC"),
                    InlineKeyboardButton("Pacific/Auckland", callback_data="key:tz:Pacific/Auckland"),
                ],
                [
                    InlineKeyboardButton("America/New_York", callback_data="key:tz:America/New_York"),
                    InlineKeyboardButton("Europe/London", callback_data="key:tz:Europe/London"),
                ],
                [
                    InlineKeyboardButton("Asia/Tokyo", callback_data="key:tz:Asia/Tokyo"),
                    InlineKeyboardButton("Australia/Sydney", callback_data="key:tz:Australia/Sydney"),
                ],
            ])
            await update.message.reply_text(
                f"⚙️ *Settings*\n\n"
                f"• Check interval: `{ci}s` ({ci_label})\n"
                f"• Periodic check: {status_icon}\n"
                f"• Timezone: `{tz_name}`\n\n"
                f"Or set a custom value with `/key ci, <seconds>`\n"
                f"Set timezone with `/tz <zone>`\n"
                f"Range: 15–600 seconds",
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            logger.info("Settings sent to chat_id=%s (ci=%s, mt=%s, tz=%s)", chat_id, ci, mt, tz_name)
        except Exception as e:
            logger.exception("Settings failed for chat_id=%s: %s", chat_id, e)

    async def tz_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set the user's timezone, e.g. /tz Pacific/Auckland"""
        chat_id = update.effective_chat.id
        text = " ".join(context.args)
        if not text:
            current = await asyncio.to_thread(self.get_kv, chat_id, "tz") or "UTC"
            await update.message.reply_text(
                f"Your current timezone is `{current}`.\n"
                f"Usage: `/tz <zone>`\n"
                f"Example: `/tz Pacific/Auckland`\n"
                f"Use `/settings` to pick from common timezones.",
                parse_mode='Markdown'
            )
            return

        zone = text.strip()
        # Validate timezone with pytz
        if zone not in pytz.all_timezones:
            await update.message.reply_text(
                f"❌ Unknown timezone `{zone}`.\n"
                f"Use a valid timezone like `Pacific/Auckland`, `UTC`, `America/New_York`.\n"
                f"See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones",
                parse_mode='Markdown'
            )
            return

        await asyncio.to_thread(self.set_kv, chat_id, "tz", zone)
        tz = pytz.timezone(zone)
        now_utc = timezone.now()
        now_local = now_utc.astimezone(tz)
        abbr = now_local.strftime('%Z')
        await update.message.reply_text(
            f"✅ Timezone set to `{zone}` (`{abbr}`).\n"
            f"Current local time: {now_local.strftime('%H:%M %Z')}",
            parse_mode='Markdown'
        )

    async def key_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        text = " ".join(context.args)
        if not text:
            await update.message.reply_text(
                "Usage: /key <key>, <value>\n"
                "Example: /key ci, 300  (set check interval, range 15–600s)\n"
                "         /key mt, off  (disable periodic checks)"
            )
            return
        try:
            key = text.split(",")[0].strip()
            value = text.split(",")[1].strip()
            if key == "ci":
                ci_int = int(value)
                if ci_int < 15:
                    ci_int = 15
                    await update.message.reply_text(
                        f"⚠️ `ci` clamped to `15` (minimum allowed)",
                        parse_mode='Markdown'
                    )
                elif ci_int > 600:
                    ci_int = 600
                    await update.message.reply_text(
                        f"⚠️ `ci` clamped to `600` (maximum allowed)",
                        parse_mode='Markdown'
                    )
                value = str(ci_int)
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
        # Rate limit check (10 seconds) — check last actual Activity, not bot reminder time
        last_activity = await asyncio.to_thread(
            lambda: Activity.objects.filter(telegram_chat_id=chat_id).order_by('-start_time').first()
        )
        now_ts = timezone.now().timestamp()
        if last_activity and last_activity.start_time and (now_ts - last_activity.start_time.timestamp()) < 10:
            msg = "Please wait at least 10 seconds between entries."
            if hasattr(update_or_query, 'answer'):
                await update_or_query.answer(msg, show_alert=True)
            else:
                await update_or_query.message.reply_text(msg)
            return

        activity = await asyncio.to_thread(log_activity_gap_filled, chat_id, tag, notes)
        await asyncio.to_thread(self.set_kv, chat_id, "last_called", str(now_ts))
        
        today_total = await asyncio.to_thread(self.get_today_total, chat_id, tag)
        
        start_str = await self._format_time(activity.start_time, chat_id)
        text = (f"✅ Started: {tag}\n"
                f"Start time: {start_str}\n"
                f"Today's total: {today_total}\n\n"
                "In the present moment, there are no problems.")
        
        # Reply cleanly without re-showing the activity keyboard, keeping the original prompt intact
        if hasattr(update_or_query, 'message') and update_or_query.message:
            await update_or_query.message.reply_text(text)

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        last_activity = await asyncio.to_thread(
            lambda: Activity.objects.filter(telegram_chat_id=chat_id).order_by('-end_time').first()
        )
        if not last_activity:
            await update.message.reply_text("No activities recorded yet.")
            return

        finished_str = await self._format_time(last_activity.end_time, chat_id)
        await update.message.reply_text(
            f"Last activity: {last_activity.name}\n"
            f"Finished at: {finished_str}\n"
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
            start_str = await self._format_time(act.start_time, chat_id)
            end_str = await self._format_time(act.end_time, chat_id)
            text += f"{start_str} - {end_str} : {act.name}\n"
        await update.message.reply_text(text)

    def _make_donut_chart(self, totals, days_label):
        """Render a doughnut chart to a bytes buffer."""
        if not totals:
            return None
        labels = [name for name, dur in totals]
        sizes = [dur.total_seconds() / 3600 for name, dur in totals]  # hours
        colors = [f'#{random.randrange(0x40, 0xBF):02X}{random.randrange(0x40, 0xBF):02X}{random.randrange(0x40, 0xBF):02X}' for _ in labels]

        fig, ax = plt.subplots(figsize=(5, 4))
        wedges, texts, autotexts = ax.pie(
            sizes, labels=None, autopct='%1.0f%%',
            startangle=90, pctdistance=0.75,
            colors=colors, wedgeprops={'linewidth': 1, 'edgecolor': 'white'}
        )
        # Draw centre hole for doughnut
        centre = plt.Circle((0, 0), 0.50, fc='white', linewidth=0)
        ax.add_artist(centre)
        ax.axis('equal')
        ax.set_title(f'Top activities — {days_label}', fontsize=12, pad=12)
        ax.legend(wedges, [f'{l} ({s:.1f}h)' for l, s in zip(labels, sizes)],
                  loc='upper left', bbox_to_anchor=(1, 0.9), fontsize=9)

        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf

    async def top(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        # Determine time range from args (default 24h)
        args = context.args
        if args and args[0].isdigit():
            days = int(args[0])
        else:
            days = 1
        now = timezone.now()
        since = now - timedelta(days=days)
        
        activities = await asyncio.to_thread(
            lambda: list(Activity.objects.filter(telegram_chat_id=chat_id, start_time__gte=since))
        )
        
        totals = {}
        for act in activities:
            if act.duration:
                totals[act.name] = totals.get(act.name, timedelta()) + act.duration
        
        sorted_totals = sorted(totals.items(), key=lambda x: x[1], reverse=True)
        
        tz_name = await asyncio.to_thread(self.get_kv, chat_id, "tz") or "UTC"
        try:
            tz_label = pytz.timezone(tz_name).localize(timezone.now()).strftime('%Z')
        except Exception:
            tz_label = "UTC"
        days_label = f"last {days}d ({tz_label})" if days > 1 else f"last 24h ({tz_label})"
        text = f"Top activities ({days_label}):\n"
        for tag, dur in sorted_totals:
            hours = dur.total_seconds() // 3600
            minutes = (dur.total_seconds() % 3600) // 60
            text += f"{tag}: {int(hours)}h {int(minutes)}m\n"
        
        # Generate and send doughnut chart
        buf = await asyncio.to_thread(self._make_donut_chart, sorted_totals, days_label)
        if buf:
            await update.message.reply_photo(photo=buf, caption=text)
        else:
            await update.message.reply_text("No activities found for this period.")

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
        if data.startswith("nav:"):
            page = int(data.split(":", 1)[1])
            keyboard = await self.get_keyboard(chat_id, page)
            await query.edit_message_reply_markup(reply_markup=keyboard)
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
            await query.message.reply_text(
                f"*Periodic check:* {status}\n\n"
                f"{'I will remind you to check in.' if new_val == 'on' else 'No more reminders until you turn it back on.'}",
                parse_mode='Markdown'
            )

    async def get_keyboard(self, chat_id, page=0, per_page=6):
        recent_activities = await asyncio.to_thread(
            lambda: list(Activity.objects.filter(telegram_chat_id=chat_id)
                         .order_by('-end_time')
                         .values_list('name', flat=True))
        )
        
        unique_tags = []
        for tag in recent_activities:
            if tag not in unique_tags:
                unique_tags.append(tag)
        
        if not unique_tags:
            unique_tags = ["Programming", "Sleep", "Exercise", "Reading", "Food", "Family"]
        
        total_pages = max(1, (len(unique_tags) + per_page - 1) // per_page)
        page = max(0, min(page, total_pages - 1))
        start = page * per_page
        end = start + per_page
        page_tags = unique_tags[start:end]
        
        keyboard = []
        for i in range(0, len(page_tags), 2):
            row = [InlineKeyboardButton(page_tags[i], callback_data=f"now:{page_tags[i]}")]
            if i + 1 < len(page_tags):
                row.append(InlineKeyboardButton(page_tags[i+1], callback_data=f"now:{page_tags[i+1]}"))
            keyboard.append(row)
        
        # Navigation row
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("<", callback_data=f"nav:{page - 1}"))
        nav_row.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="noop"))
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton(">", callback_data=f"nav:{page + 1}"))
        keyboard.append(nav_row)
        
        return InlineKeyboardMarkup(keyboard)

    async def periodic_check(self, context: ContextTypes.DEFAULT_TYPE):
        chat_ids = await asyncio.to_thread(
            lambda: list(
                set(
                    list(Activity.objects.values_list('telegram_chat_id', flat=True).distinct())
                    + list(KeyValuePair.objects.values_list('telegram_chat_id', flat=True).distinct())
                )
            )
        )
        
        for chat_id in chat_ids:
            if not chat_id: continue
            
            # Skip if user has disabled periodic checks
            mt = await asyncio.to_thread(self.get_kv, chat_id, "mt") or "on"
            if mt != "on":
                continue
            
            last_called = await asyncio.to_thread(self.get_kv, chat_id, "last_called")
            ci = await asyncio.to_thread(self.get_kv, chat_id, "ci") or "600"
            ci_val = max(15, min(600, int(ci)))

            now_ts = timezone.now().timestamp()
            if not last_called or (now_ts - float(last_called)) > ci_val:
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

    async def _format_time(self, dt, chat_id):
        """Convert a UTC datetime to the user's timezone and format with abbreviation.

        Returns a string like "14:30 NZST" or "02:15 UTC".
        """
        if dt is None:
            return None
        tz_name = await asyncio.to_thread(self.get_kv, chat_id, "tz") or "UTC"
        try:
            tz = pytz.timezone(tz_name)
        except Exception:
            tz = pytz.UTC
        # dt is naive or UTC-aware; make it timezone-aware in UTC first
        if timezone.is_naive(dt):
            utc_dt = pytz.UTC.localize(dt)
        else:
            utc_dt = dt.astimezone(pytz.UTC)
        local_dt = utc_dt.astimezone(tz)
        return local_dt.strftime('%H:%M %Z')

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
