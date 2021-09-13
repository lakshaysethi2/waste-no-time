import telebot
from manictime import *
from datetime import datetime,timedelta,timezone
import schedule
import time
import threading
# import os
# TOKEN = os.getenv('TOKEN')
TOKEN = "1937014541:AAEAMxaXzB0ZUmYJdzJ-0W25gPNnH50WFw4"
LAKSHAY_CID =1040271347
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
		

@bot.message_handler(commands=['stats'])
def new_tag(message):
	try:
		tag_name = message.text.split()[1]
	except Exception as e:
		tag_name = 'Programming'
		print(e)
	try:
		# tzinfo = timezone(timedelta(hours=12))
		now = datetime.now() +timedelta(hours=12)
		text = "stats:\n"
		text += "Today:\n"
		today = datetime(year=now.year,month=now.month,day=now.day,hour=0,minute=0,second=0) + timedelta(hours=12)
		text += f'{tag_name}: ' +str( round(get_report_for_tag(f'{tag_name}',today,now)[0].seconds/3600,2))
		text += "\n"
		text += "Yesterday:\n"
		
		text += f'{tag_name}: ' + str(round(get_report_for_tag(f'{tag_name}',today-timedelta(days=1),today)[0].seconds/3600,2))
		text += "\n"
		text += "last 7 days :\n"
		
		text += f'{tag_name}: ' + str(round(get_report_for_tag(f'{tag_name}',today-timedelta(days=7),now)[0].seconds/3600,2))
		
		
		bot.send_message(message.chat.id,text=text)
	except Exception as e:
		bot.send_message(message.chat.id,text= f"{e} ")
		

@bot.message_handler(commands=['s'])
def say_this(message):
	bot.send_message(message.chat.id,text=message.text.split('s')[1])


@bot.message_handler(commands=['now'])
def now(message):
	tag = message.text.split('now')[1].split(',')[0]
	notes = message.text.split('now')[1].split(',')[1]
	dto = datetime.now() +timedelta(hours=12) -timedelta(seconds=30)
	if message.chat.id == 1040271347:
		if notes !='':
			create_activity_tag(tag,notes,datetimeObj=dto,duration=60)
		else:
			create_activity_tag(tag,"made with /now ",datetimeObj=dto,duration=60)
		bot.send_message(message.chat.id,text=f'{tag} tag made')


def there_is_no_tag(from_time,to_time)->bool:
	"""returns true if thre is no tag in from time, to time , if tag is found returns false
	so can be used like if there_is_no_tag"""
	res_json  = getactivities_json(to_time,from_time)
	activities = res_json['activities']
	if len(activities)<1:
		return True
	return False


@bot.message_handler(commands=['check'])
def check(message = 'hi'):
	rm = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=False,row_width=1)
	rm.add('programming','doing phone',"/now sleep","/now pre sleep","/now food")
	now = datetime.utcnow() + timedelta(hours =12)
	to_time = now
	from_time = to_time - timedelta(minutes=15)
	if there_is_no_tag(from_time, to_time):
		
		from_time_str = str(from_time).split(' ')[1].split(".")[0]
		to_time_str = str(to_time).split(' ')[1].split(".")[0]
		text = f'{from_time_str} to {to_time_str} \nno tag mate!\n what have you been up to?'
		bot.send_message(LAKSHAY_CID,text=text,reply_markup=rm)
	





@bot.message_handler(func=lambda m: True)
def conversation(message):
	text = "no handled"
	rm = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=False,row_width=1)
	dto = datetime.now() +timedelta(hours=12) -timedelta(seconds=30)
	if  message.text.lower() == 'hi':  
		text = 'Hi! :)'
		rm.add('how are you ?')
	elif 'how are you' in  message.text.lower() :
		text = 'Im good how about you?'
		rm.add('im good thanks','not good')
	elif 'thanks' in  message.text.lower() :
		text = 'what have you been up to ?'
		rm.add('programming','doing phone',"/now sleep","/now pre sleep","/now food")
	elif 'programming' ==  message.text.lower() :
		if message.chat.id == LAKSHAY_CID:
			create_activity_tag("programming","from telegram",datetimeObj=dto,duration=60)
			text = "progamming tag made for now"
	elif 'doing phone' ==  message.text.lower() :
		if message.chat.id == LAKSHAY_CID:
			create_activity_tag("doing phone","from telegram",datetimeObj=dto,duration=60)
			text = "doing phone tag made for now"
	elif 'not good' in  message.text.lower() :
		if message.chat.id == LAKSHAY_CID:
			create_activity_tag("depression","said not good in telegram",datetimeObj=dto,duration=60)
		text = 'humm why ? what happened?'
	# rm.add(':)')
	bot.send_message(message.chat.id,text=text,reply_markup= rm)




		



def run_continuously(interval=5):
    cease_continuous_run = threading.Event()
    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)
    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def stsrt():
	try:
		stop_run_continuously = run_continuously()# Start the background thread
		# stop_run_continuously.set()# Stop the background thread
		schedule.every(15).minutes.do(check)
		bot.polling()
	except Exception as e :
		bot.send_message(LAKSHAY_CID,text=str(e)+' restarting..')
		print(e)
		stsrt()


stsrt()

 