import telebot
# import os
# TOKEN = os.getenv('TOKEN')
TOKEN = "1937014541:AAEAMxaXzB0ZUmYJdzJ-0W25gPNnH50WFw4"

bot = telebot.TeleBot(TOKEN)
print('started')
@bot.message_handler(commands=['start'])
def send_welcome(message):	
	rm = telebot.types.ReplyKeyboardMarkup()
	rm.add("Im good","im not ok")
	print("re:",rm.to_json())
	print(message.text)
	bot.reply_to(message,text=f"Hi,{message.from_user.first_name} How are you?",reply_markup= rm)

@bot.message_handler(commands=['start'])
def send_welcome(message):	
	rm = telebot.types.ReplyKeyboardMarkup()
	rm.add("Im good","im not ok")
	print("re:",rm.to_json())
	print(message.text)
	bot.reply_to(message,text=f"Hi,{message.from_user.first_name} How are you?",reply_markup= rm)

bot.polling()
