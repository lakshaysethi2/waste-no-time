import telebot
from fpdf import FPDF
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
import random
from manictime_dash import get_json_object
import sentry_sdk

# keep tags in this array in lower case
array_of_tags_for_which_notes_are_required = ['plantme','fliss', 'trying or setting up','doing phone','food',
'writing',
'shopping',
'job',
'programming',
'linux',
'sick',
]
CHECKINTERVAL=10
the_activities_markup = [
	'/key mt, on',
	'/key mt, off',
	'/key ci, 1',
	'/key ci, 10',
	'/key ci, 2',
	'/key ci, 20',
	'/key ci, 0',
	'/key ci, 5',
	'/now reading',
	'/now job',
	'/now writing',
	'/now cleaning',
	'/now walking',
	'/now exercise',
	'/now driving',
	'/now uber',
	'/now programming',
	'/now linux',
	'/now doing phone',
	'/now goal setting',
	"/now sleep",
	"/now eye candy",
	"/now food",
	'/now Trying or setting up',
	'/now other people',
	'/now plantme',
	'/now udemy',
	'/top 24',
	'/top 24*7',
	'/top 24*30',
	'/top 24*90',
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
	'/unlockdash',
	'/lockdash',


]
import os
TOKEN = os.getenv('TELEGRAM_BOT_API_KEY')
bot = telebot.TeleBot(TOKEN)
print('started')
rm = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)

@bot.message_handler(commands=['start'])
def send_welcome(message):
	rm.__init__()
	rm.add("/n add new goal(s)","/l list out my goals", "/manictime today vs yesterday manictime" )
	print(message.text)
	bot.send_message(message.chat.id,text=f"Hi,{message.from_user.first_name} {message.from_user.last_name} Welcome -  Thanks for checking out my Goals App Bot , it is not ready for public use yet, but you can still use my goals app website at https://goals.lak.nz to set and achieve your goals -Lakshay")
	bot.send_message(LAKSHAY_CID,text=f"Hi,{message.from_user.first_name} {message.from_user.last_name} Welcome -  Thanks for checking out my Goals App Bot , it is not ready for public use yet, but you can still use my goals app website at https://goals.lak.nz to set and achieve your goals \n -Lakshay {message.text} {message.chat.id}")

@bot.message_handler(commands=["n"])
def new_goals(message):
	

	bot.send_message(LAKSHAY_CID,text = 'sweet lets set some new goals http://goals.lak.nz')#,reply_markup=rm)

@bot.message_handler(commands=["l"])
def new_goals(message):
	bot.send_message(LAKSHAY_CID,text = 'here is a list of your goals')#,reply_markup=rm)
	bot.send_message(LAKSHAY_CID,text = 'http://goals.lak.nz')#,reply_markup=rm)
	bot.send_message(LAKSHAY_CID,text = 'which goal do you want to work on?')#,reply_markup=rm)


def modify_add_checkbox(text):
	new_text = """ 
<style>
body{
	color:white; background-color:black;
}
textarea{
	background-color: #2b3030;
}
.checkboxRed { background-color:red; display: inline; }
.checkboxGreen { background-color:green; display: inline; }
</style>
<pre>"""
	for line in text.split('\n'):
		new_text += "<div class='activity'>" +line + "<div class='checkboxgreen'><input type='checkbox'></div>"+ "<div class='checkboxRed'><input  type='checkbox'></div>" 
		new_text+= '<textarea></textarea></div>'+"\n"
	new_text += "</pre>"
	return new_text

def add_pie_chart(text):
	activitie_names=[]
	activitie_hours=[]
	colors=[]
	for line in text.split('\n'):
		if  '- -' in line:
			line_elements= line.split('-')
			hours=str(line_elements[3])
			activity=line_elements[4]
			activitie_names.append(activity)
			activitie_hours.append(hours)
			r = lambda: random.randint(0,255)
			colors.append(f'#%02X%02X%02X' % (r(),r(),r()))
	donut_text = f'''   <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.js"></script>
		<canvas id="myChart" style="min-height:30rem"></canvas>
  
	<script>  
	const data = {{
	  	labels: {activitie_names},
		datasets: [{{
			label: 'top acts',
			data: {activitie_hours},
			backgroundColor: {colors},
			hoverOffset: 4
		}}]
	}};
	const config = {{
  	type: 'doughnut',
  	data: data,
	}};
    let myChart = new Chart("myChart", config);
	</script>'''
	donut_text +='<pre>'
	for line in text.split('\n'):
		if  '- -' in line:
			line_elements= line.split('-')
			hours=str(line_elements[3])
			donut_text += f"<div class='activity' style='height:{hours.strip()}rem; border:solid 2px; overflow:hidden' >" +line + "<div class='checkboxgreen'><input type='checkbox'></div>"+ "<div class='checkboxRed'><input  type='checkbox'></div>" 
			donut_text+= '</div>'+"\n"
	donut_text += "</pre>"
	return donut_text

def make_pdf(text):
	pdf = FPDF('P','mm','A4')
	pdf.add_page()
	pdf.set_font('helvetica','',8)
	pdf.multi_cell(w=0,h=10,txt=text)
	pdf.output('top.pdf')
	return open('top.pdf','rb')

@bot.message_handler(commands=["top"])
def manictime_top(message):
	days= float(eval(message.text.split('/top')[1])/24)
	text = get_top_for_days(days)
	bot.send_message(LAKSHAY_CID,text=text)
	modified_text=modify_add_checkbox(text)
	modified_text=add_pie_chart(text)+'\n'+modified_text
	awesome_html = get_html_like_ss_for_top(text)
	url = f'https://api.telegram.org/bot{TOKEN}/sendDocument'
	files = {'document': (f'top-with-radio-{getNow()}.html', awesome_html)}
	response = requests.post(url, files=files,data={"chat_id":LAKSHAY_CID,"disable_notification":True})
	url = f'https://api.telegram.org/bot{TOKEN}/sendDocument'
	files = {'document': (f'top-{getNow()}.html', modified_text)}
	response = requests.post(url, files=files,data={"chat_id":LAKSHAY_CID,"disable_notification":True})
	pdf = make_pdf(text)
	files = {'document': (f'top-{getNow()}.pdf', pdf)}
	response = requests.post(url, files=files,data={"chat_id":LAKSHAY_CID,"disable_notification":True})
	return modified_text
	
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


def make_pdf_summary(html_string):
	pdf = FPDF('P','mm','A4')
	pdf.add_page()
	pdf.set_font('helvetica','',8)
	pdf.multi_cell(w=0,h=10,txt=html_string)
	pdf.output('summary.pdf')
	return open('summary.pdf','rb')

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
	pdf = make_pdf_summary(html_string)
	files = {'document': (f'summary-{getNow()}.pdf', pdf)}
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
	bot.send_message(LAKSHAY_CID,text=text,
		disable_notification=True,
		)




@bot.message_handler(commands=['del'])
def delkeyvalue(message):
	if message.chat_id == LAKSHAY_CID:
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
def last_as_text(message):
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
		

@bot.message_handler(commands=['lockdash'])
def lockdash(message):
	get_json_object(0)

@bot.message_handler(commands=['unlockdash'])
def unlockdash(message):
	get_json_object(1)

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
	true_last_used=message.split(",")[0]
	if true_last_used == get_value("last_useda"):
		return
	elif get_value("last_usedb") == true_last_used:
		set_value('last_usedb', get_value("last_useda"))
		set_value('last_useda', true_last_used)
	elif get_value("last_usedc") == true_last_used:
		set_value('last_usedc', get_value("last_useda"))
		set_value('last_useda', true_last_used)
	elif get_value("last_usedd") == true_last_used:
		set_value('last_usedd', get_value("last_useda"))
		set_value('last_useda', true_last_used)
	else:
		set_value('last_usedd', get_value("last_usedc"))
		set_value('last_usedc', get_value("last_usedb"))
		set_value('last_usedb', get_value("last_useda"))
		set_value('last_useda', true_last_used)

@bot.message_handler(commands=['now'])
def now(message):
	tag = message.text.split('now')[1].split(',')[0]
	a=message.text.split('now')[1].split(',')
	notes=''
	set_reply_markup_last_used("/now"+tag)

	if len(a)>1:
		notes = a[1]
		notes+= get_formated_time(getNow())
	if tag.lower().strip() in array_of_tags_for_which_notes_are_required:
		if notes == '':
			bot.send_message(LAKSHAY_CID,text=f'Wrn: Please provide notes')
			if str(get_value('strict_notes')) == 'yes':
				return False
	dto = getNow()
	if LAKSHAY_CID == message.chat.id:
		if notes !='':
			pass
		else:
			notes=""
		old_rm = get_value("current_rm")
		rm=get_reply_markup_for_now()
		if create_activity_tag(tag,notes,datetimeObj=dto,duration=4):
			sent_message_obj=bot.send_message(LAKSHAY_CID,text=f'{tag} tag made',disable_notification=True)
			fixmt(message,sent_message_obj)
			time_spent_on_tag = get_time_spent_today(tag)
			time_spent_text= f'spent {time_spent_on_tag} \non {tag} today'
			reply_markup = json.loads('{"inline_keyboard":[[]]}')
			ik = reply_markup.get('inline_keyboard')
			ik[0].append({'text': 'Attach photo', 'url': 'idk.lak.nz'})
			# ik[0].append({'text': 'high', 'callback_data': 'idk.lak.nz'})
			inline_keyboard = json.dumps(reply_markup)
			bot.edit_message_text(message_id=sent_message_obj.id,chat_id=LAKSHAY_CID,
				reply_markup=inline_keyboard,
				text= sent_message_obj.text+'\n'+time_spent_text)
			if old_rm != rm:
				text_content=f"{sent_message_obj.text}\n{time_spent_text}"
				bot.delete_message(LAKSHAY_CID, sent_message_obj.id)
				bot.send_message(LAKSHAY_CID,text=text_content,disable_notification=True,reply_markup=rm)
			return True
		else:
			bot.send_message(LAKSHAY_CID,text=f'Error occured with manictime please try again',disable_notification=True,reply_markup=rm)
			return create_activity_tag(tag,notes,datetimeObj=dto,duration=1)
	
		

@bot.message_handler(commands=['budget'])
def budget(message):
	tag = message.text.split('budget')[1]
	time_spent_on_tag = get_time_spent_today(tag)
	time_spent_on_tag_last_7days = get_time_spent_today(tag,7)
	bot.send_message(LAKSHAY_CID,text=f'on {tag} \n spent {time_spent_on_tag} today \n \
		and {time_spent_on_tag_last_7days} in the last 7 days')

@bot.message_handler(commands=['budgets'])
def budgets(message):
	tags_array = [
		#[tag,daily budget,weekly budget]
		['sleep',7*60,42*60],
		['family',20,180],
		['food',40,6*60],
		['trying or setting up',50,5*60],
		['driving',30,4*60],
		['bio',40,7*60],
		['ctek',0,0],
		['uber',0,0],
		['writing',0,0],
		['programming',0,0],
		['goal setting',0,0],
		['walking',0,0],
		['exercise',0,0],
		
		


		 ]
	for tag in tags_array:
		message.text = f'/budget {tag[0]}'
		if tag[1] !=0:
			daily = get_hours_from_time_delta(timedelta(minutes=tag[1]))
			weekly =get_hours_from_time_delta(timedelta(minutes=tag[2]))
			bot.send_message(LAKSHAY_CID, f'{tag[0]}: \n daily:{daily}\n weekly: {weekly}')
		budget(message)
		sleep(2)

def there_is_no_tag(from_time,to_time)->bool:
	"""returns true if thre is no tag in from time, to time , if tag is found returns false
	so can be used like if there_is_no_tag"""
	res_json  = getactivities_json(to_time,from_time)
	activities = res_json['activities']
	if len(activities)<1:
		return True
	return False
@bot.message_handler(commands=['fixmt'])
def fixmt(message,sent_message_obj=None):
	fix_manictime()
	text = "attempted fix all"
	if sent_message_obj is not None:
		bot.edit_message_text(text=sent_message_obj.text+'\n'+text,chat_id=LAKSHAY_CID,
			message_id=sent_message_obj.message_id)
	else:
		bot.send_message(LAKSHAY_CID,text=text,disable_notification=True)


def get_reply_markup_for_now():
	array_of_arrays = []
	small_array = []
	array_of_arrays.append([str(get_value('last_useda'))])
	array_of_arrays.append([str(get_value('last_usedb'))])
	array_of_arrays.append([str(get_value('last_usedc'))])
	array_of_arrays.append([str(get_value('last_usedd'))])
	array_of_arrays.append(['/key strict_notes, no'])
	for index,tag in enumerate(the_activities_markup):
		small_array.append(tag)
		if index%2 == 1:
			array_of_arrays.append(small_array)
			small_array = []
	if len(small_array)>0: array_of_arrays.append(small_array)
	assert array_of_arrays[0] == [str(get_value('last_useda'))]
	reply_markup = json.dumps({'keyboard':array_of_arrays})
	set_value("current_rm",reply_markup)
	return reply_markup

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
			text = f'{from_time_str} to {to_time_str} \nno tag mate!\n\n what have you been INVESTING your ATTENTION in ?\nhttps://goals.lak.nz'
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
		except (KeyError , ValueError):
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
def timesheet_html(message):
	[tag,days,*args] = message.text.split('/timesheet ')[1].split(",")	
	html_string = get_timesheet_html(tag,days,*args)
	url = f'https://api.telegram.org/bot{TOKEN}/sendDocument'
	files = {'document': (f'{tag}-timesheet-last-{int(days)}-days.html', html_string)}
	response = requests.post(url, files=files,data={"chat_id":LAKSHAY_CID})




@bot.message_handler(func=lambda m: True)
def conversation(message):
	rm=[]
	text = "no handled"
	now = getNow() -timedelta(seconds=3)
	if  message.text.lower() == 'hi':  
		text = 'Hi! :)'
	elif 'thanks' in  message.text.lower() :
		text = 'what have you been up to ?'
		rm = get_reply_markup_for_now()
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
	if get_value("last_useda") is None:
		set_value("last_useda", '/now manictime')
	if get_value("last_usedb") is None:
		set_value('last_usedb', "/now programming")
	if get_value("last_usedc") is None:
		set_value('last_usedc', "/now goal setting")
	if get_value("last_usedd") is None:
		set_value('last_usedd', "/now reading")
	set_value('strict_notes', "yes")
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

if __name__ == "__main__":
	sentry_sdk.init(
		dsn="https://1c5ee8adcfe1468b95718f124b970547@o4504297777004544.ingest.sentry.io/4504297778184192",
		traces_sample_rate=1.0
	)
	stsrt()
