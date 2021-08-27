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
	

	bot.send_message(message.chat.id,text = 'sweet lets set some new goals http://goals.lak.nz')#,reply_markup=rm)

@bot.message_handler(commands=["l"])
def new_goals(message):
	bot.send_message(message.chat.id,text = 'here is a list of your goals')#,reply_markup=rm)
	bot.send_message(message.chat.id,text = 'http://goals.lak.nz')#,reply_markup=rm)
	bot.send_message(message.chat.id,text = 'which goal do you want to work on?')#,reply_markup=rm)



@bot.message_handler(commands=["mtc"])
def manictime(message):
	goal = f'''Goal \n7:30:00  -  sleep\n4:00:00  -  Programming\n3:30:30  -  Job Apply\n3:00:00  -  Uber    '''
	bot.send_message(message.chat.id,text =goal)
	get_manictime_yesterday(bot,message)
	get_manictime_today(bot,message)

@bot.message_handler(commands=["mtc7"])
def manictime(message):
	goal = f'''Goal \n 56h -  sleep\n 40hr  -  Programming\n 20hr - Job Apply/marketing to get money from programming\n   '''
	
	get_manictime_7days_total(bot,message,goal)


@bot.message_handler(commands=["mt"])
def mt(message):
	try:
		tag = message.text.split('/mt ')[1]
		get_report(tag,message,bot)
	except Exception as e:
		bot.send_message(message.chat.id,text=e)
		



@bot.message_handler(commands=["at"])
def authtoken(message):
	AUTH_TOKEN = message.text.split()[1]

	bot.send_message(message.chat.id,text=AUTH_TOKEN)



@bot.message_handler(commands=['x'])
def x_days(message):
	try:
		x = message.text.split("/x")[1]
		x = int(x)
		get_manictime_last_x_days(bot,message,x)
	except Exception as e:
		bot.send_message(message.chat.id,text= e)




@bot.message_handler(commands=['new'])
def new_tag(message):
	
	try:
		tag_name = message.text.split("/new")[1].strip().split(",")[0]
		notes = message.text.split(",")[1]	
		dto = datetime.now()+timedelta(hours=12) - timedelta(minutes=int(message.text.split(",")[2]))
		duration = int(message.text.split(",")[3]) *60
		create_activity_tag(user_tag=tag_name,notes= notes,datetimeObj=dto,duration=duration)
		bot.send_message(message.chat.id,text=f"{tag_name} tag made")
	except Exception as e:
		bot.send_message(message.chat.id,text= f"{e} tn nte ago durmin")
		
@bot.message_handler(content_types=['photo'])
def imgur_link(message):
	pass
	return
	m = message
	photo = m.photo[3]

	print (message)
	return






@bot.message_handler()
def conversation(message):
	# text = ""
	rm = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=False,row_width=1)
	if  message.text.lower() == 'hi':  
		text = 'Hi! :)'
		rm.add('how are you ?')
	elif 'how are you' in  message.text.lower() :
		text = 'Im good how about you?'
		rm.add('im good thanks','not good')
	elif 'thanks' in  message.text.lower() :
		text = ':)'
	elif 'not good' in  message.text.lower() :
		dto = datetime.now() +timedelta(hours=12) -timedelta(seconds=30)
		create_activity_tag("depression","said not good in telegram",datetimeObj=dto,duration=60)
		text = 'humm why ? what happened?'
	else:
		return

	bot.send_message(message.chat.id,text=text,reply_markup= rm)


def stsrt():
	try:
		bot.polling()
	except Exception as e :
		print(e)
		stsrt()


stsrt()