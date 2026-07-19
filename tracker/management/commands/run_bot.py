import os
import logging
import json
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from tracker.models import Activity, KeyValuePair
from tracker.gap_filler import create_activity_with_gap_filling, get_time_spent_today_seconds, format_duration

logger = logging.getLogger(__name__)

DEFAULT_TAGS = [
    'Programming', 'Writing', 'Reading', 'Walking', 'Exercise',
    'Driving', 'Uber', 'Linux', 'Food', 'Sleep', 'Bio', 'Goal setting'
]

def get_kv(user_id, key, default=''):
    kv, _ = KeyValuePair.objects.get_or_create(user_id=user_id, key=key, defaults={'value': default})
    return kv.value

def set_kv(user_id, key, value):
    kv, _ = KeyValuePair.objects.get_or_create(user_id=user_id, key=key)
    kv.value = str(value)
    kv.save()
    return kv.value

def get_last_used_array(user_id):
    raw = get_kv(user_id, 'last_used_array', '[]')
    try:
        arr = json.loads(raw)
        if isinstance(arr, list):
            return arr
    except Exception:
        pass
    return DEFAULT_TAGS[:5]

def add_last_used(user_id, tag):
    tag_clean = tag.strip()
    arr = get_last_used_array(user_id)
    if tag_clean in arr:
        arr.remove(tag_clean)
    arr.insert(0, tag_clean)
    if len(arr) > 20:
        arr.pop()
    set_kv(user_id, 'last_used_array', json.dumps(arr))

def get_reply_markup(user_id):
    last_used = get_last_used_array(user_id)
    keyboard = []
    keyboard.append([KeyboardButton('/now Programming'), KeyboardButton('/now Reading'), KeyboardButton('/now Writing')])
    row = []
    for tag in last_used[:6]:
        row.append(KeyboardButton(f'/now {tag}'))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([KeyboardButton('/status'), KeyboardButton('/last'), KeyboardButton('/undo')])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    name = update.effective_user.first_name or "there"
    text = f"Hi {name}! Welcome to Waste No Time.\nUse `/now <tag>, [notes]` to track your activities and stay on trajectory."
    await update.message.reply_text(text, reply_markup=get_reply_markup(user_id), parse_mode="Markdown")

async def now_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    text = update.message.text or ""
    parts = text.split('now', 1)
    if len(parts) < 2 or not parts[1].strip():
        await update.message.reply_text("Usage: `/now <tag>, <optional notes>`", parse_mode="Markdown")
        return

    args_str = parts[1].strip()
    sub_parts = args_str.split(',', 1)
    tag = sub_parts[0].strip()
    notes = sub_parts[1].strip() if len(sub_parts) > 1 else ""

    add_last_used(user_id, tag)
    create_activity_with_gap_filling(user_id, tag, notes=notes)
    spent_secs = get_time_spent_today_seconds(user_id, tag)
    spent_str = format_duration(spent_secs)

    reply_text = f"✅ Started **{tag}**\n⏱ Spent today: **{spent_str}**\n\n_In the present moment, there are no problems._"
    await update.message.reply_text(reply_text, reply_markup=get_reply_markup(user_id), parse_mode="Markdown")

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    now = timezone.now()
    create_activity_with_gap_filling(user_id, "Idle / Break", notes="Stopped activity", now=now)
    await update.message.reply_text("🛑 Activity stopped. Logged break.", reply_markup=get_reply_markup(user_id))

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    acts = Activity.objects.filter(user_id=user_id, end_time__gte=today_start)

    summary = {}
    for act in acts:
        st = max(act.start_time, today_start)
        dur = (act.end_time - st).total_seconds()
        if dur > 0:
            summary[act.name] = summary.get(act.name, 0) + dur

    text = "📊 **Today's Activity Summary:**\n"
    if not summary:
        text += "No activities logged today yet."
    else:
        sorted_acts = sorted(summary.items(), key=lambda x: x[1], reverse=True)
        for name, secs in sorted_acts:
            text += f"- **{name}**: {format_duration(secs)}\n"

    latest = Activity.objects.filter(user_id=user_id).first()
    if latest:
        text += f"\nLast activity: **{latest.name}** (ended {latest.end_time.strftime('%H:%M:%S')})"

    await update.message.reply_text(text, reply_markup=get_reply_markup(user_id), parse_mode="Markdown")

async def last_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    acts = Activity.objects.filter(user_id=user_id)[:10]
    text = "🕒 **Recent Activities:**\n"
    for act in acts:
        dur = format_duration((act.end_time - act.start_time).total_seconds())
        notes_str = f" (n: {act.notes})" if act.notes else ""
        text += f"• `{act.start_time.strftime('%H:%M')} - {act.end_time.strftime('%H:%M')}` [{dur}] **{act.name}**{notes_str}\n"
    if not acts:
        text += "No recent activities found."
    await update.message.reply_text(text, reply_markup=get_reply_markup(user_id), parse_mode="Markdown")

async def undo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    twenty_mins_ago = timezone.now() - timedelta(minutes=20)
    latest = Activity.objects.filter(user_id=user_id, created_at__gte=twenty_mins_ago).first()
    if latest:
        name = latest.name
        latest.delete()
        await update.message.reply_text(f"🗑 Deleted last activity: **{name}**", reply_markup=get_reply_markup(user_id), parse_mode="Markdown")
    else:
        await update.message.reply_text("Could not delete: no activity found within the last 20 minutes.", reply_markup=get_reply_markup(user_id))

async def key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    text = update.message.text or ""
    parts = text.split('key', 1)
    if len(parts) < 2 or not parts[1].strip():
        kvs = KeyValuePair.objects.filter(user_id=user_id)
        msg = "🔑 **Key-Value Store:**\n" + "\n".join([f"`{kv.key}` = {kv.value}" for kv in kvs]) or "No keys stored."
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    args = parts[1].strip().split(',', 1)
    key = args[0].strip()
    if len(args) > 1:
        val = args[1].strip()
        set_kv(user_id, key, val)
        await update.message.reply_text(f"Set `{key}` = `{val}`", parse_mode="Markdown")
    else:
        val = get_kv(user_id, key, "Not found")
        await update.message.reply_text(f"`{key}` = `{val}`", parse_mode="Markdown")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    if text.startswith('/'):
        return
    if len(text) < 40 and '\n' not in text:
        user_id = update.effective_chat.id
        tag = text.strip()
        add_last_used(user_id, tag)
        create_activity_with_gap_filling(user_id, tag)
        spent = format_duration(get_time_spent_today_seconds(user_id, tag))
        await update.message.reply_text(f"✅ Logged **{tag}** (Today: {spent})", reply_markup=get_reply_markup(user_id), parse_mode="Markdown")

class Command(BaseCommand):
    help = 'Run Telegram Bot daemon (python-telegram-bot v21+)'

    def handle(self, *args, **options):
        token = os.environ.get('TELEGRAM_BOT_API_KEY')
        if not token:
            self.stdout.write(self.style.ERROR('TELEGRAM_BOT_API_KEY environment variable is not set!'))
            return

        self.stdout.write(self.style.SUCCESS('Starting Telegram Bot...'))
        application = ApplicationBuilder().token(token).build()

        application.add_handler(CommandHandler('start', start_command))
        application.add_handler(CommandHandler('now', now_command))
        application.add_handler(CommandHandler('stop', stop_command))
        application.add_handler(CommandHandler('status', status_command))
        application.add_handler(CommandHandler('last', last_command))
        application.add_handler(CommandHandler('undo', undo_command))
        application.add_handler(CommandHandler('key', key_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

        application.run_polling()
