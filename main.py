import telebot
from manictime import *
# import os
# TOKEN = os.getenv('TOKEN')
TOKEN = "1937014541:AAEAMxaXzB0ZUmYJdzJ-0W25gPNnH50WFw4"

bot = telebot.TeleBot(TOKEN)
print('started')
rm = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
rm.add("/n add new goal(s)","/l list out my goals", "/manictime today vs yesterday manictime" )
@bot.message_handler(commands=['start'])
def send_welcome(message):	
	
	
	print(message.text)
	bot.send_message(message.chat.id,text=f"Hi,{message.from_user.first_name} Welcome - please choose from the following options",reply_markup= rm)
@bot.message_handler(commands=["n"])
def new_goals(message):
	

	bot.send_message(message.chat.id,text = 'sweet lets set some new goals')#,reply_markup=rm)

@bot.message_handler(commands=["manictime"])
def manictime(message):
	get_manictime_yesterday(bot,message)
	get_manictime_today(bot,message)
	

@bot.message_handler(commands=["at"])
def authtoken(message):
	AUTH_TOKEN = message.text.split()[1]

	bot.send_message(message.chat.id,text=AUTH_TOKEN)



@bot.message_handler()
def didnotrecognize(message):
	text = "I did not recognize that - please select from the following options"
	
	bot.send_message(message.chat.id,text=text)




bot.polling()
