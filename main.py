import telebot
from manictime import *
from goals import *
import logging
import json
from datetime import datetime,timedelta,timezone
import schedule
import time
import threading
from assistant import *
from calendarfile import get_calendar_html

CHECKINTERVAL=30
activities_markup = [
	'/now driving',
	'/now uber',
	'/now walking',
	'/now exercise',
	'/key ci, 0',
	'/key ci, 1',
	'/key mt, on',
	'/key mt, off',
	'/key ci, 20',
	'/now ctek',
	'/now cleaning',
	'/now linux',
	'/top 24*7',
	'/top 24',
	'/now programming',
	'/now doing phone',
	'/now goal setting',
	"/now sleep",
	"/now pre sleep",
	"/now food",
	'/now Trying or setting up',
	'/now fliss',
	'/now plantme',
	'/now writing',
	'/now reading',
	'/now udemy',
	'/now bio',
	'/now manictime',
	'/now thinking',
	'/now family',
	'/now ecl',
	'/now YouTube',
	'/now shopping',
	'/now data',
	'/now money',
	'/now sick',


]
# import os
# TOKEN = os.getenv('TOKEN')
TOKEN = "1937014541:AAEAMxaXzB0ZUmYJdzJ-0W25gPNnH50WFw4" # main
#TOKEN = "5061167346:AAECJdb_-U9jQorMiJRsITRJBRyf-53Ctv4" # conversation bot
bot = telebot.TeleBot(TOKEN)
print('started')
rm = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
@bot.message_handler(commands=['start'])
def send_welcome(message):
	
	rm.__init__()
	rm.add("/n add new goal(s)","/l list out my goals", "/manictime today vs yesterday manictime" )
	
	
	print(message.text)
	bot.send_message(LAKSHAY_CID,text=f"Hi,{message.from_user.first_name} Welcome - please choose from the following options",reply_markup= rm)
@bot.message_handler(commands=["n"])
def new_goals(message):
	

	bot.send_message(LAKSHAY_CID,text = 'sweet lets set some new goals http://goals.lak.nz')#,reply_markup=rm)

@bot.message_handler(commands=["l"])
def new_goals(message):
	bot.send_message(LAKSHAY_CID,text = 'here is a list of your goals')#,reply_markup=rm)
	bot.send_message(LAKSHAY_CID,text = 'http://goals.lak.nz')#,reply_markup=rm)
	bot.send_message(LAKSHAY_CID,text = 'which goal do you want to work on?')#,reply_markup=rm)


def modify_add_checkbox(text):
	new_text = """<head><meta name='viewport' content='width=device-width, initial-scale=1.0'></head> 
<style>
body{color:white; background-color:black;}
</style>
<body> <pre>"""
	for line in text.split('\n'):
		new_text += line + "<input type='checkbox'>"
		new_text+= '<textarea></textarea>'+"\n"
	new_text += "</pre>"
	return new_text

@bot.message_handler(commands=["top"])
def manictime(message):
	days= float(eval(message.text.split('/top')[1])/24)
	text = get_top_for_days(days)
	bot.send_message(LAKSHAY_CID,text=text)
	modified_text=modify_add_checkbox(text)
	url = f'https://api.telegram.org/bot{TOKEN}/sendDocument'
	files = {'document': (f'top-{getNow()}.html', modified_text)}
	response = requests.post(url, files=files,data={"chat_id":LAKSHAY_CID})
	
def get_evening_text(days):
	now = getNow()
	today = now - timedelta(hours = now.hour, minutes = now.minute) - timedelta(days=(int(days)-1))
	today_morning = today + timedelta(hours=8)
	yesterday_eve = today_morning - timedelta(hours=15)
	from_time = yesterday_eve
	to_time = today_morning
	return get_activities_for_awareness(to_time,from_time)

@bot.message_handler(commands=["evening"])
def manictime(message):
	try: days= message.text.split('/evening')[1] 
	except: days = 1
	text = get_evening_text(days)
	bot.send_message(LAKSHAY_CID,text=text)

@bot.message_handler(commands=["eveningcsv"])
def manictime(message):
	try: 
		days= message.text.split('/eveningcsv')[1] 
		if days == '':
			days = 1
	except: days = 1
	csv_string = "day,top1,top2,top3\n"
	for x in range (0,int(days)):
		csv_string += str(x) + "," + convert_to_csv(get_evening_text(x))
	url = f'https://api.telegram.org/bot{TOKEN}/sendDocument'
	files = {'document': (f'eveningcsv-{getNow()}.csv', csv_string)}
	response = requests.post(url, files=files,data={"chat_id":LAKSHAY_CID})


@bot.message_handler(commands=["summary"])
def summary(message):
	try:
		months = int(message.text.split('/summary')[1])
		html_string =  get_summary_monthly_html(months)
	except:
		html_string =  summary_top()
	url = f'https://api.telegram.org/bot{TOKEN}/sendDocument'
	files = {'document': (f'summary-{getNow()}.html', html_string)}
	response = requests.post(url, files=files,data={"chat_id":LAKSHAY_CID})

@bot.message_handler(commands=["ss"])
def simple_summary(message):	
	"""Message handler for generating simple summary in months"""
	months = int(message.text.split('/ss')[1])
	html_string =  get_summary_monthly_html(months,simple_summary_wanted=True)
	
	url = f'https://api.telegram.org/bot{TOKEN}/sendDocument'
	files = {'document': (f'SIMPLE-summary-{getNow()}.html', html_string)}
	response = requests.post(url, files=files,data={"chat_id":LAKSHAY_CID})

@bot.message_handler(commands=["sscsv"])
def simple_summary(message):	
	"""CSV simple summary in months"""
	months = int(message.text.split('/sscsv')[1])
	csv_string = "month,top1,top2,top3\n"
	for x in range (0,int(months)):
		csv_string += str(x) + "," + convert_to_csv(get_top_activities_for_month(x))
	url = f'https://api.telegram.org/bot{TOKEN}/sendDocument'
	files = {'document': (f'monthlycsv-{getNow()}.csv', csv_string)}
	response = requests.post(url, files=files,data={"chat_id":LAKSHAY_CID})

@bot.message_handler(commands=["mtc"])
def manictime(message):
	goal = f'''Goal \n7:30:00  -  sleep\n4:00:00  -  Programming\n3:30:30  -  Job Apply\n3:00:00  -  Uber    '''
	bot.send_message(LAKSHAY_CID,text =goal)
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
		logging.exception('Caught an error')
		bot.send_message(LAKSHAY_CID,text=e)
		


@bot.message_handler(func=lambda message: True, content_types=['audio', 'photo', 'voice', 'video', 'document', 'location', 'contact', ])
def default_command(message):
	if message.chat.id == -1001792881544:
		link = f'https://t.me/c/1792881544/{message.id}'
		bot.send_message(-1001792881544, f"here is your link:\n\n {link}")

database = {}

db.connect()
def updateDatabase(database=database):
	try:
		for pair in KeyValuePair.select():
			database[f'{pair.key}']=pair.value
	except OperationalError:
		db.create_tables([KeyValuePair])
		for pair in KeyValuePair.select():
			database[f'{pair.key}']=pair.value
updateDatabase()




def get_value(key):
	updateDatabase()
	try:
		return database[f'{key}']
	except:
		return None
     


def set_value(key,value):
	text = "new created"
	try:
		# TODO fix this shit, it FUBAR but still fix it !
		kvp= KeyValuePair.get(key = str(key))
		kvp.value = str(value)
		kvp.save()
		text = "updated"
	except Exception as e:
		logging.exception('Caught an error')
		kvp= KeyValuePair(key=key,value=value) 
		kvp.save()
	
	updateDatabase()
	return (f'{text} {key}',database[f'{key}'])

@bot.message_handler(commands=['append'])
def keyappendvalue(message):
	text = ""
	try:
		key = message.text.split('/append')[1].split(',')[0].strip()
		value = message.text.split('/append')[1].split(',')[1].strip()
		value = str(get_value(key)) +'\n'+value
		text ='append successful\n'+ str(set_value(key, value))
	except IndexError as e:
		text = 'syntax is /append key, text to append'
	except KeyError:
		text = 'can not append as key not created yet'

	bot.send_message(LAKSHAY_CID,text=text)

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
	rm.add('thanks')
	for key in database.keys():
		rm.add('/key '+str(key))
	bot.send_message(LAKSHAY_CID,text=text,reply_markup=rm)




@bot.message_handler(commands=['del'])
def delkeyvalue(message):
	if LAKSHAY_CID == LAKSHAY_CID:
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
	








@bot.message_handler(commands=['basics'])
def basics(message):
	take_care_of_basics()






@bot.message_handler(commands=["at"])
def authtoken(message):
	AUTH_TOKEN = message.text.split()[1]

	bot.send_message(LAKSHAY_CID,text=AUTH_TOKEN)



@bot.message_handler(commands=['x'])
def x_days(message):
	try:
		x = message.text.split("/x")[1]
		x = int(x)
		text = get_manictime_last_x_days(x)
		bot.send_message(LAKSHAY_CID,text = text)
	except Exception as e:
		logging.exception('Caught an error')
		bot.send_message(LAKSHAY_CID,text= e)



@bot.message_handler(commands=['calendar'])
def last(message):
	hours = message.text.split("/calendar")[1]
	now = getNow()
	date = f'{now.day}-{now.month}-{now.hour}-{now.minute}'
	html_string = get_calendar_html(hours=hours)
	url = f'https://api.telegram.org/bot{TOKEN}/sendDocument'
	files = {'document': (f'{date}-calendar.html', html_string)}
	response = requests.post(url, files=files,data={"chat_id":LAKSHAY_CID})
	# response.text




@bot.message_handler(commands=['last'])
def last(message):
	text = 'from - to - activity\n'
	notes_needed = False
	try:
		if message.text.split("/last")[1]:
			notes_needed = True
	except Exception as e:
		pass
	text += getLastfewHours(notes_needed)
	bot.send_message(LAKSHAY_CID,text= text)




@bot.message_handler(commands=['new'])
def new_tag(message):
	
	try:
		tag_name = message.text.split("/new")[1].strip().split(",")[0]
		notes = message.text.split(",")[1]
		now = getNow()	
		dto = now - timedelta(minutes=int(message.text.split(",")[2]))
		duration = int(message.text.split(",")[3]) *60
		if create_activity_tag(user_tag=tag_name,notes= notes,datetimeObj=dto,duration=duration):
			bot.send_message(LAKSHAY_CID,text=f"{tag_name} tag made",disable_notification=True)
		else:
			bot.send_message(LAKSHAY_CID,text=f"Error please try again",disable_notification=True)
	except Exception as e:
		logging.exception('Caught an error')
		bot.send_message(LAKSHAY_CID,text= f"{e} tn nte ago durmin")
		

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
		today = datetime(year=now.year,month=now.month,day=now.day,hour=0,minute=0,second=0) 
		text += f'{tag_name}: ' +str( round(get_report_for_tag(f'{tag_name}',today,now)[0].seconds/3600,2))
		text += "\n"
		text += "Yesterday:\n"
		
		text += f'{tag_name}: ' + str(round(get_report_for_tag(f'{tag_name}',today-timedelta(days=1),today)[0].seconds/3600,2))
		text += "\n"
		text += "last 7 days :\n"
		
		text += f'{tag_name}: ' + str(round(get_report_for_tag(f'{tag_name}',today-timedelta(days=7),now)[0].seconds/3600,2))
		
		
		bot.send_message(LAKSHAY_CID,text=text)
	except Exception as e:
		logging.exception('Caught an error')
		bot.send_message(LAKSHAY_CID,text= f"{e} ")
		

@bot.message_handler(commands=['s'])
def say_this(message):
	bot.send_message(LAKSHAY_CID,text=message.text.split('/s')[1])
	bot.delete_message(LAKSHAY_CID, message.id)

def set_reply_markup_last_used(message):
	last_used=message.text
	last_to_last_used=get_value("last_used")
	last_to_last_to_last_used=get_value("last_to_last_used")
	last_to_last_to_last_to_last_used=get_value("last_to_last_to_last_used")
	if last_used != last_to_last_used and last_used != last_to_last_to_last_used and last_to_last_used != last_to_last_to_last_to_last_used:
		set_value('last_to_last_used', last_to_last_used)
		set_value('last_to_last_to_last_used', last_to_last_to_last_used)
		set_value('last_to_last_to_last_to_last_used', last_to_last_to_last_to_last_used)
		set_value('last_used', last_used)

@bot.message_handler(commands=['now'])
def now(message):
	set_reply_markup_last_used(message)

	tag = message.text.split('now')[1].split(',')[0]
	a=message.text.split('now')[1].split(',')
	notes=''
	if len(a)>1:
		notes = a[1]
		notes+= get_formated_time(getNow())
	dto = getNow()
	if LAKSHAY_CID == message.chat.id:
		if notes !='':
			pass
		else:
			notes=""
		if create_activity_tag(tag,notes,datetimeObj=dto,duration=4):
			bot.send_message(LAKSHAY_CID,text=f'{tag} tag made',disable_notification=True)
			fixmt(message)
			time_spent_on_tag = get_time_spent_today(tag)
			bot.send_message(LAKSHAY_CID,text=f'spent {time_spent_on_tag} \non {tag} today',disable_notification=True)
		else:
			bot.send_message(LAKSHAY_CID,text=f'Error occured with manictime please try again',disable_notification=True)
			create_activity_tag(tag,notes,datetimeObj=dto,duration=1)
		

@bot.message_handler(commands=['budget'])
def budget(message):
	tag = message.text.split('budget')[1]
	time_spent_on_tag = get_time_spent_today(tag)
	bot.send_message(LAKSHAY_CID,text=f'on {tag} \n spent {time_spent_on_tag} today')

@bot.message_handler(commands=['budgets'])
def budgets(message):
	tags_array = [
		'family',
		'food',
		'driving',
		'bio',
		'sleep',
		'ctek',
		'uber',
		'writing',
		'programming',
		'goal setting',
		
		


		 ]
	for tag in tags_array:
		sleep(5)
		message.text = f'/budget {tag}'
		budget(message)

def there_is_no_tag(from_time,to_time)->bool:
	"""returns true if thre is no tag in from time, to time , if tag is found returns false
	so can be used like if there_is_no_tag"""
	res_json  = getactivities_json(to_time,from_time)
	activities = res_json['activities']
	if len(activities)<1:
		return True
	return False
@bot.message_handler(commands=['fixmt'])
def fixmt(message):
	fix_manictime()
	text = "attempted fix all"
	bot.send_message(LAKSHAY_CID,text=text,disable_notification=True)


def get_reply_markup_for_now():
	rm.__init__()
	last_used = str(get_value('last_used'))
	last_to_last_used=str(get_value("last_to_last_used"))
	last_to_last_to_last_used=str(get_value("last_to_last_to_last_used"))
	last_to_last_to_last_to_last_used=str(get_value("last_to_last_to_last_to_last_used"))
	if last_used is not None and last_to_last_used is not None and last_to_last_to_last_used is not None and last_to_last_to_last_to_last_used is not None :
		rm.add(last_used)
		rm.add(last_to_last_used)
		rm.add(last_to_last_to_last_used)
		rm.add(last_to_last_to_last_to_last_used)
	for act in activities_markup:
		rm.add(act)
	return rm 

@bot.message_handler(commands=['check'])
def check(message = 'hi'):
	CHECKINTERVAL = int(database['ci'])

	if database['mt'] == 'on':
		rm = get_reply_markup_for_now()
		now = getNow()
		to_time = now
		from_time = to_time - timedelta(minutes=CHECKINTERVAL)
		if there_is_no_tag(from_time, to_time):
			
			from_time_str = str(from_time).split(' ')[1].split(".")[0]
			to_time_str = str(to_time).split(' ')[1].split(".")[0]
			text = f'{from_time_str} to {to_time_str} \nno tag mate!\n\n what have you been INVESTING in ?'
			bot.send_message(LAKSHAY_CID,text=text,reply_markup=rm)
	



@bot.message_handler(commands=['schedule'])
def schedule_event(message):
	"""expects event name as first argument and 
	%d-%m-%y-%H-%M as second argument
	creates an event and stores it in database as json string
	"""
	
	text = "name,%d-%m-%y-%H-%M"
	try:
		parced = message.text.split("/schedule")[1].split(",")
		event_name = parced[0]
		event_time = datetime.strptime(parced[1], '%d-%m-%y-%H-%M')
		event = {'event_name':event_name}
		event['timestamp'] = event_time.timestamp()
		try:
			events_array =json.loads( get_value('events'))
		except KeyError or ValueError:
			set_value('events',"[]")
			events_array =json.loads( get_value ('events'))
		events_array.append(event)
		set_value('events',json.dumps(events_array))
		text ="event created you can can check with /key events"
	except IndexError:
		pass
	except Exception as e:
		bot.send_message(LAKSHAY_CID,text=str(e))

	bot.send_message(LAKSHAY_CID,text=text)


@bot.message_handler(commands=['math'])
def math(message):
	exp = message.text.split('/math')[1]
	text = eval(exp)
	bot.send_message(LAKSHAY_CID,text=text)

@bot.message_handler(commands=['csv'])
def timesheet(message):
	[tag,days,*args] = message.text.split('/csv ')[1].split(",")
	csv_string = get_timesheet_csv(tag,days,*args)
	url = f'https://api.telegram.org/bot{TOKEN}/sendDocument'
	files = {'document': (f'{tag}-timesheet-csv-last-{int(days)}-days.csv', csv_string)}
	response = requests.post(url, files=files,data={"chat_id":LAKSHAY_CID})

@bot.message_handler(commands=['timesheet'])
def timesheet(message):
	[tag,days,*args] = message.text.split('/timesheet ')[1].split(",")	
	html_string = get_timesheet_html(tag,days,*args)
	url = f'https://api.telegram.org/bot{TOKEN}/sendDocument'
	files = {'document': (f'{tag}-timesheet-last-{int(days)}-days.html', html_string)}
	response = requests.post(url, files=files,data={"chat_id":LAKSHAY_CID})




@bot.message_handler(func=lambda m: True)
def conversation(message):
	text = "no handled"
	
	now = getNow() -timedelta(seconds=3)
	if  message.text.lower() == 'hi':  
		text = 'Hi! :)'
		rm.__init__()
		rm.add('What Should I do now ?')
	elif 'What Should I do now'.lower() in  message.text.lower():
		text =  database['what should I do now']
		rm.__init__()
		rm.add('thanks')
	elif 'thanks' in  message.text.lower() :
		text = 'what have you been up to ?'
		get_reply_markup_for_now()

	elif 'programming' ==  message.text.lower() :
		if LAKSHAY_CID == LAKSHAY_CID:
			create_activity_tag("programming","from telegram",datetimeObj=now,duration=6)
			text = "progamming tag made for now"
	elif 'doing phone' ==  message.text.lower() :
		if LAKSHAY_CID == LAKSHAY_CID:
			create_activity_tag("doing phone","from telegram",datetimeObj=now,duration=6)
			text = "doing phone tag made for now"
	elif 'not good' in  message.text.lower() :
		if LAKSHAY_CID == LAKSHAY_CID:
			create_activity_tag("depression","said not good in telegram",datetimeObj=now,duration=6)
		text = 'humm why ? what happened?'
		rm.__init__()
		rm.add('i feel like shit :(')
	
	elif 'shit' in  message.text.lower() :
		if LAKSHAY_CID == LAKSHAY_CID:
			create_activity_tag("depression","said not good in telegram",datetimeObj=now,duration=6)
		text = 'why ?'	
	elif 'what are my goals' in message.text.lower() :
		goals_list = get_goals_list()
		text = 'here is a list of your goals \n' + goals_list 	
	
	else:
		return	
	
	bot.send_message(LAKSHAY_CID,text=text,reply_markup= rm)


def getMyevents():
	

	myevents_array = []
	try:
		events_str = database['events']
		myevents_array=  json.loads(events_str)
	except KeyError:
		pass
	return myevents_array

def dailynotification():
	now = getNow()
	for event in getMyevents():
		if is_in_future(event,now):
			if seconds_till_event(event,now) < 60:
				bot.send_message(LAKSHAY_CID,text=event['event_name'])
			# else:
			# 	bot.send_message(LAKSHAY_CID,text='error in daily notification')


		else:
			delete_event(event)
			
	h = now.hour 
	m = now.minute
	if h == 21 and m == 00:
		bot.send_message(LAKSHAY_CID,text='shave bro')
		
	return


def is_in_future(event,now):
	"""return true or false"""
	event_time = datetime.fromtimestamp(event['timestamp'])
	if event_time > now:
		return True
	return False


def seconds_till_event(event,now):
	"""returns int of seconds till event"""
	event_time = datetime.fromtimestamp(event['timestamp'])
	seconds_int = int((event_time-now).total_seconds())
	return seconds_int

def delete_event(event_to_delete):
	events_array = json.loads(get_value('events'))
	for index,event in enumerate(events_array):
		if event['event_name'] == event_to_delete['event_name']:
			events_array.pop(index)
	set_value('events', json.dumps(events_array))


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
	if get_value("last_used") is None:
		set_value("last_used", '/now manictime')
	if get_value("last_to_last_used") is None:
		set_value('last_to_last_used', "/now programming")
	if get_value("last_to_last_to_last_used") is None:
		set_value('last_to_last_to_last_used', "/now testing")
	if get_value("last_to_last_to_last_to_last_used") is None:
		set_value('last_to_last_to_last_to_last_used', "/now reading")
	
	if get_value('ci') is None:
		set_value("ci", '2')
	if get_value('mt') is None:
		set_value("mt", 'on')
	#bot.send_message(LAKSHAY_CID,text='starting..',disable_notification=True)
	rc = run_continuously()
	schedule.every(CHECKINTERVAL).seconds.do(check)
	#schedule.every(5).seconds.do(dailynotification)
	while 1:
		try:
			#telebot.apihelper.RETRY_ON_ERROR = True

			bot.polling()

		except Exception as e:
			logging.exception('Caught an error')
			print(e)
			time.sleep(1)
			bot.send_message(LAKSHAY_CID,text=str(e)+' restarting..')


stsrt()
