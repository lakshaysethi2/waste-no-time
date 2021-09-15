import telebot
from manictime import *

from datetime import datetime,timedelta,timezone
import schedule
import time
import threading
CHECKINTERVAL=2
activities_markup = [
	'programming',
	'doing phone',
	"/now sleep",
	"/now pre sleep",
	"/now food",
	'/now Trying or setting up',
	'/now fliss',
	'/now writing',
	'/now bio',
	'/now manictime',
	'/now thinking',


]
# import os
# TOKEN = os.getenv('TOKEN')
TOKEN = "1937014541:AAEAMxaXzB0ZUmYJdzJ-0W25gPNnH50WFw4"
bot = telebot.TeleBot(TOKEN)
print('started')
rm = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
@bot.message_handler(commands=['start'])
def send_welcome(message):
	
	rm.__init__()
	rm.add("/n add new goal(s)","/l list out my goals", "/manictime today vs yesterday manictime" )
	
	
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


@bot.message_handler(commands=["top"])
def manictime(message):
	days= int(message.text.split('/top')[1])
	get_top_for_days(bot,days)
	
	
	

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
		



database = {}
db.connect()

def updateDatabase(database=database):
	for pair in KeyValuePair.select():
		database[f'{pair.key}']=pair.value
	




def get_value(key):
	updateDatabase()
	return database[f'{key}']
     


def set_value(key,value):
	text = "new created"
	try:
		kvp= KeyValuePair.get(key = key)
		kvp.value = value
		kvp.save()
		text = "updated"
	except Exception as e:
		kvp= KeyValuePair(key=key,value=value) 
		kvp.save()
	
	updateDatabase()
	return (f'{text} {key}',database[f'{key}'])



@bot.message_handler(commands=['key'])
def keyvalue(message):
	
	text = ":P"
	try:
		key = message.text.split('/key')[1].split(',')[0].strip()
		value = message.text.split('/key')[1].split(',')[1].strip()
		text = str(set_value(key, value))
	except IndexError as e:
		try:
			text = str(get_value(key))
		except KeyError:
			text = 'not found'
	rm.__init__()
	for key in database.keys():
		rm.add('/key '+str(key))
	bot.send_message(LAKSHAY_CID,text=text,reply_markup=rm)




@bot.message_handler(commands=['del'])
def delkeyvalue(message):
	if message.chat.id == LAKSHAY_CID:
		text = 'deleating...'
		key = message.text.split('/del')[1].strip()
		try:
			to_del = KeyValuePair.get(key=key)
			to_del.delete_instance()
			text = 'deleated '+ key

		except Exception as e:
			text = str(e)+'can not delete what does not exist!\n duh!'
		updateDatabase()
		rm.__init__()
		for key in database.keys():
			rm.add('/key '+str(key))
		bot.send_message(LAKSHAY_CID,text=text,reply_markup=rm)
	













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
		now = getNow()	
		dto = now - timedelta(minutes=int(message.text.split(",")[2]))
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
		
		now = getNow()
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
	bot.send_message(message.chat.id,text=message.text.split('/s')[1])
	bot.delete_message(message.chat.id, message.id)


@bot.message_handler(commands=['now'])
def now(message):
	tag = message.text.split('now')[1].split(',')[0]
	a=message.text.split('now')[1].split(',')
	notes=''
	if len(a)>1:
		notes = a[1]
	dto = getNow() -timedelta(seconds=5)
	if message.chat.id == 1040271347:
		if notes !='':
			create_activity_tag(tag,notes,datetimeObj=dto,duration=4)
		else:
			create_activity_tag(tag,"made with /now ",datetimeObj=dto,duration=4)
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
	
	try:
		if database['mt'] == 'on':
			rm.__init__()
			for act in activities_markup:
				rm.add(act)
			now = datetime.utcnow() + timedelta(hours =12)
			to_time = now
			from_time = to_time - timedelta(minutes=CHECKINTERVAL)
			if there_is_no_tag(from_time, to_time):
				
				from_time_str = str(from_time).split(' ')[1].split(".")[0]
				to_time_str = str(to_time).split(' ')[1].split(".")[0]
				text = f'{from_time_str} to {to_time_str} \nno tag mate!\n\n what have you been VOTING for?'
				bot.send_message(LAKSHAY_CID,text=text,reply_markup=rm)
	except KeyError:
		set_value('mt', 'off')





@bot.message_handler(func=lambda m: True)
def conversation(message):
	text = "no handled"
	
	now = getNow() -timedelta(seconds=3)
	if  message.text.lower() == 'hi':  
		text = 'Hi! :)'
		rm.__init__()
		rm.add('how are you ?')
	elif 'how are you' in  message.text.lower() :
		text = 'Im good how about you?'
		rm.__init__()
		rm.add('im good thanks','not good')
	elif 'thanks' in  message.text.lower() :
		text = 'what have you been up to ?'
		rm.__init__()
		for activity in activities_markup:
			rm.add(activity)

	elif 'programming' ==  message.text.lower() :
		if message.chat.id == LAKSHAY_CID:
			create_activity_tag("programming","from telegram",datetimeObj=now,duration=6)
			text = "progamming tag made for now"
	elif 'doing phone' ==  message.text.lower() :
		if message.chat.id == LAKSHAY_CID:
			create_activity_tag("doing phone","from telegram",datetimeObj=now,duration=6)
			text = "doing phone tag made for now"
	elif 'not good' in  message.text.lower() :
		if message.chat.id == LAKSHAY_CID:
			create_activity_tag("depression","said not good in telegram",datetimeObj=now,duration=6)
		text = 'humm why ? what happened?'
		rm.__init__()
		rm.add('i feel like shit :(')
	
	elif 'shit' in  message.text.lower() :
		if message.chat.id == LAKSHAY_CID:
			create_activity_tag("depression","said not good in telegram",datetimeObj=now,duration=6)
		text = 'why ?'	
	else:
		return	
	
	bot.send_message(message.chat.id,text=text,reply_markup= rm)



def dailynotification():
	h = getNow().hour 
	m = getNow().minute
	if h == 21 and m == 00:
		bot.send_message(LAKSHAY_CID,text='shave bro')
		
	return

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
	bot.send_message(LAKSHAY_CID,text='starting..')

	try:
		stop_run_continuously = run_continuously()# Start the background thread
		# stop_run_continuously.set()# Stop the background thread
		schedule.every(CHECKINTERVAL).minutes.do(check)
		schedule.every(5).seconds.do(dailynotification)
		bot.polling()
	except Exception as e :
		bot.send_message(LAKSHAY_CID,text=str(e)+' restarting..')
		print(e)
		time.sleep(5)
		stsrt()



stsrt()
