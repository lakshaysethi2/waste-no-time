import telebot
import time

TOKEN2 = os.environ.get('TELEGRAM_BOT_API_KEY')
bot2 = telebot.TeleBot(TOKEN2)

@bot2.message_handler(commands=['start'])
def send_welcome(message):
	bot2.send_message(message.chat.id,text=f"hi prefix your message with /s and i will say what ever you prefix with /s \n example\n /s how are you?")


@bot2.message_handler(commands=['s'])
def say_this(message):
    text = message.text.split('/s')[1]
    bot2.delete_message(message.chat.id, message.id)
    if text !='':
        bot2.send_message(message.chat.id,text=text )


def start_convo_bot():
    try:
        print('started')
        bot2.polling()
    except Exception as e :
        print(e)
        print('restarting')
        time.sleep(5)

while 1:
    start_convo_bot()
