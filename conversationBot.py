import telebot
import time

TOKEN2 = "1909326610:AAFh7rsp1dbD6XJ2IGmn5Og8ZfIuF6ZRmNk"
bot2 = telebot.TeleBot(TOKEN2)

@bot2.message_handler(commands=['start'])
def send_welcome(message):
	bot2.send_message(message.chat.id,text=f"hi prefix your message with /s and i will say what ever you prefix with /s \n example\n /s how are you?")

	

@bot2.message_handler(commands=['s'])
def say_this(message):
	bot2.send_message(message.chat.id,text=message.text.split('/s')[1])
	bot2.delete_message(message.chat.id, message.id)


def start_convo_bot():
    try:
        print('started')
        bot2.polling()
    except Exception as e :
    #bot2.send_message(LAKSHAY_CID,text=str(e)+' restarting..')
        print(e)
        print('restarting')
        time.sleep(5)
        start_convo_bot()



try: 
    start_convo_bot()
except Exception as e:
    print(type(e))
    start_convo_bot()