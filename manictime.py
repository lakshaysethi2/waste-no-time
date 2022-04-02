
from datetime import timezone
import re
from time import sleep
from operator import itemgetter
import math
SERVER_LINK = 'https://manictime.lak.nz'
AUTH_TOKEN = "5989585dc24846a6aaf2febe48e37879"
tags_timeline_id = ''
import requests
import json
from datetime import datetime,timedelta,timezone
LAKSHAY_CID =1040271347
from types import SimpleNamespace

try:
    from keyvalue import *
except:
    from .keyvalue import *

newzealnd = 12
headers = {
    'Accept': 'application/vnd.manictime.v2+json',
    'Authorization': f'Bearer {AUTH_TOKEN}',
}

def get_token(username,password):

    headers = {
        'Accept': 'application/vnd.manictime.v2+json',
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
    }

    data = {
    'grant_type': 'password',
    'username': username,
    'password': passsword,
    }

    resp=  requests.post(f'{SERVER_LINK}/api/token', headers=headers,data=data)
   # print (resp.text)

def getactivities_json(to_time,from_time):
    response = requests.get(f'{SERVER_LINK}/api/timelines', headers=headers)
    try:
        timelines = json.loads(response.text)
    except:
        sleep(10)
        timelines = json.loads(response.text)
    for timeline in timelines['timelines']:
        if timeline['timelineType']['typeName'] =="ManicTime/Tags":
            tags_timeline_id = timeline['timelineId']
    response = requests.get(f'{SERVER_LINK}/api/timelines/{tags_timeline_id}/activities?fromTime={from_time}&toTime={to_time}', headers=headers)
    res_json = json.loads(response.text)
    return res_json




def get_unique_activities(to_time,from_time,simple_summary_wanted=False):
    res_json = getactivities_json(to_time,from_time)
    unique_activities = []
    for activity in res_json['activities']:
        duration = datetime.fromisoformat(activity['endTime']) - datetime.fromisoformat(activity['startTime'])
        if activity['displayName'] not in str(unique_activities):
            ua = {'name':activity['displayName'],
            'totalTime':duration}
            unique_activities.append(ua)
        elif activity['displayName'] in str(unique_activities):
            for ua in unique_activities:
                if ua['name'] == activity['displayName']:
                    ua['totalTime'] += duration
    unique_activities = sorted(unique_activities, key=itemgetter('totalTime'), reverse=True)
    return unique_activities

def get_activities_for_awareness(to_time,from_time,simple_summary_wanted=False):
    interval_str = f'FROM {from_time.day}/{from_time.month}/{from_time.year}  TO {to_time.day}/{to_time.month}/{to_time.year}\n'
    unique_activities = get_unique_activities(to_time,from_time,simple_summary_wanted)
    total = timedelta(hours=0)
    for index,ua in enumerate(unique_activities):
        if index < 10:
            total += ua["totalTime"]
            if not simple_summary_wanted:
                interval_str += f'''{str(math.floor(ua["totalTime"].total_seconds()/3600)).split(":")[0]}h{str(ua["totalTime"]).split(":")[1]}m  -  {ua["name"] }\n'''
    total= round(total.total_seconds()/3600 ,2) 
    interval_str += '\ntop % - avg per day\n\n'
    for index,ua in enumerate(unique_activities):
        if index<6:
            dur_hours=round((ua["totalTime"].total_seconds()/get_total_seconds_between(from_time,to_time))*24,1)
            percent = round( (dur_hours/24)*100,2 )
            interval_str += f'{percent}% {dur_hours}hr - {ua["name"] }  \n'
    interval_str += f'total: {total}\n'
    return interval_str 
 
def get_total_seconds_between(from_t,to_t):
    return (from_t-to_t).total_seconds()

def get_manictime_yesterday(bot,message):
    now = getNow()
    today_started = now - timedelta(hours=now.hour) - timedelta(minutes=now.minute) -timedelta(seconds=61)
    to_time = today_started
    from_time = today_started -timedelta(days=1)
    text = "yesterday\n"+  get_activities_for_awareness(to_time,from_time)
    bot.send_message(LAKSHAY_CID,text=text)
    

def get_manictime_today(bot,message):
    now = getNow()
    today_started = now - timedelta(hours=now.hour) - timedelta(minutes=now.minute)
    to_time = now
    from_time = today_started
    
    text = 'today\n'+ get_activities_for_awareness(to_time,from_time)
    bot.send_message(LAKSHAY_CID,text=text)
   



def get_manictime_7days_total(bot,message,goal):
    now = getNow()
    
    to_time = now
    from_time = now - timedelta(hours=168)
    text = goal
    text += '\nlast 7 days \n'+ get_activities_for_awareness(to_time,from_time)
    bot.send_message(LAKSHAY_CID,text=text)
   

def get_top_for_days(days):
    seconds=int(24*60*60*days)
    now = getNow()
    to_time = now
    text = ""
    from_time = now - timedelta(seconds=seconds)
    text += f'\nlast {days} days top activities\n'+ get_activities_for_awareness(to_time,from_time)
    return text
    


def get_manictime_last_x_days(x):
    text = ""
    now = getNow()
    for a in range (0,x):
        day_start = datetime(now.year,now.month,now.day,0,0) - timedelta(days=a)
        day_end = day_start+timedelta(hours=24)
        from_time = day_start
        to_time = day_end
        text += f'{day_start.day}-{day_start.month}\n'+ get_activities_for_awareness(to_time,from_time)
    text += f'\n{23-getNow().hour}h{60-getNow().minute}m \n'
    return text

def get_report(tag,message,bot):
    to_time = getNow()
    from_time = to_time -timedelta(days=7)
    res_json = getactivities_json(to_time,from_time)
    text = ""
    for activity in res_json['activities']:
        if activity['displayName'].lower() == tag.lower():
            starttime = datetime.fromisoformat(activity['startTime'])
            endtime= datetime.fromisoformat(activity['endTime'])
            duration = endtime - starttime
            # date = starttime.date
            try: 
                notes = activity['textData'].split('Notes')[1]
            except Exception as e:
                notes =""
            text += f"""on: {starttime.date()} \n{starttime.hour}:{starttime.minute} \nduration:{duration}\nNotes:\n {notes} \n\n\n"""
            #  notes: {activity['notes']} 
    bot.send_message(LAKSHAY_CID,text)

def get_notes(activity):
    try:
        return activity['textData'].split("<")[2].split('Notes>')[1].strip()
    except KeyError:
        return ""

BOOTSTRAP_STRING='<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.6.1/css/bootstrap-grid.min.css" integrity="sha512-Xj2sd25G+JgJYwo0cvlGWXoUekbLg5WvW+VbItCMdXrDoZRWcS/d40ieFHu77vP0dF5PK+cX6TIp+DsPfZomhw==" crossorigin="anonymous" referrerpolicy="no-referrer" />'

def get_top_activities_for_month(which_month,simple_summary_wanted=False):
    now = getNow()
    if which_month == 0:
        from_time = now - timedelta(days=now.day)
        to_time = now
    elif which_month>0:
        to_time= now -timedelta(days=now.day) - (which_month-1)* timedelta(days=30)
        from_time = to_time - timedelta(days=30)
    return get_activities_for_awareness(to_time,from_time,simple_summary_wanted)

def get_summary_monthly_html(number_of_months,simple_summary_wanted=False):
    """gives a html with month to month extimates"""
    html = BOOTSTRAP_STRING
    html += "<div class='container'><div class='row'>"
    for x in range(0,number_of_months):
        html+="<pre class='col' style='border:solid black 2px;' >"
        html += get_top_activities_for_month(x,simple_summary_wanted)
        html += "</pre>"
    return html

def get_summary_monthly_csv(number_of_months,simple_summary_wanted=False):
    """gives a csv with month to month extimates"""
    csv = "from-to,top1,top2,top3,top4,top5,top6,top7,top8,top9,top10\n"
    list_of_fromtos = []
    # populate the list of from tos
    for x in range(0 , number_of_months):
        fromto={}
        fromto['name']= f"month {x}"
        fromto["list_of_acts"] =  re.findall ("m  -  .*",get_top_activities_for_month(x,simple_summary_wanted))
        list_of_fromtos.append(fromto)

    for fromto in list_of_fromtos:
        csv += f'{fromto},'
        for act in fromto["list_of_acts"]:
            csv += f"{act},"
        csv+='\n'
    return csv

def convert_to_csv(standard_top_txt):
    arr = re.findall("m  -  .*",standard_top_txt)
    new_arr=[]
    for act in arr:
        stripped = act.split("m  - ")[1]
        new_arr.append(stripped)
    csv = ""
    for act in new_arr:
        csv +=act+","
    csv+='\n'
    return csv

def summary_top():
    html = BOOTSTRAP_STRING
    html+= "<style>.col\{ border:solid black 2px; \} </style>"
    html += "<div class='container'>"
    html += "<div class='row'>"
    html +="<pre class='col' >"

    html += get_top_for_days(1)

    html += "</pre>"
  
    html +="<pre class='col' >"
    html += get_top_for_days(7)
    html += "</pre>"
    html +="<pre class='col' >"
    html += get_top_for_days(14)
    html += "</pre>"
    html +="<pre class='col' >"
    html += get_top_for_days(21)
    html += "</pre>"
    html +="<pre class='col' >"
    html += get_top_for_days(30)
    html += "</pre>"
    html +="<pre class='col' >"
    html += get_top_for_days(60)
    html += "</pre>"
    html +="<pre class='col' >"
    html += get_top_for_days(90)
    html += "</pre>"
    html +="<pre class='col' >"
    html += get_top_for_days(180)
    html += "</pre>"
    html += "</div>"
    html += "</div>"

    return html

def get_simple_activity_obj(activity):
    act = SimpleNamespace()
    act.starttime = datetime.fromisoformat(activity['startTime'])
    act.endtime= datetime.fromisoformat(activity['endTime'])
    act.duration = act.endtime - act.starttime
    act.notes = get_notes(activity)
    return act

def get_nice_date_and_time(datetime):
    return f'{datetime.day}/{datetime.month}/{datetime.year} - {datetime.hour}:{datetime.minute}'

def get_timesheet_csv(tag,days,minimum_minutes=30):
    to_time = getNow()
    from_time = to_time -timedelta(days=int(days))
    res_json = getactivities_json(to_time,from_time)
    timesheet_units_csv ="from,till,duration,notes\n"
    timesheet_total = timedelta (hours=0)
    filtered_act_array = []
    for activity in res_json['activities']:
        if activity['displayName'].lower() == tag.lower():
            act = get_simple_activity_obj(activity)
            act.notes = act.notes.replace("\n"," - - ")
            if act.duration.seconds > (60*int(minimum_minutes)):
                filtered_act_array.append(act)
                timesheet_units_csv += f'{act.starttime},{act.endtime},{act.duration},{act.notes}\n'
                timesheet_total +=act.duration
    timesheet_total = round(timesheet_total.total_seconds()/3600 ,2)
    return timesheet_units_csv + f"TOTAL: {timesheet_total} hours"

def get_timesheet_html(tag,days,minimum_minutes=30):
    to_time = getNow()
    from_time = to_time -timedelta(days=int(days))
    res_json = getactivities_json(to_time,from_time)
    timesheet_units_html ="<style> .work_unit{ border: solid 2px } </style>"
    timesheet_total = timedelta (hours=0)
    filtered_act_array = []
    for activity in res_json['activities']:
        if activity['displayName'].lower() == tag.lower():
            act = get_simple_activity_obj(activity)
            act.notes = act.notes.replace("\n"," - - ")
            if act.duration.seconds > (60*int(minimum_minutes)):
                filtered_act_array.append(act)
                timesheet_units_html += f'''
                        <div class='work_unit'>
                            {get_nice_date_and_time(act.starttime)} - {get_nice_date_and_time(act.endtime)}: <br>
                            {act.notes}<br>
                            {act.duration}
                        </div>'''
                timesheet_total +=act.duration
    timesheet_units_html += get_graph_html_for_timesheet(filtered_act_array,tag)
    return timesheet_units_html + f"<br>{timesheet_total}"

def get_graph_html_for_timesheet(act_arr, tag):
    graph_html =""
    labels = [get_nice_date_and_time(act.starttime) for act in act_arr]
    graph_html += f'''
        <script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.0/dist/chart.min.js" integrity="sha256-Y26AMvaIfrZ1EQU49pf6H4QzVTrOI8m9wQYKkftBt4s=" crossorigin="anonymous"></script>

        <canvas id="myChart" width="400" height="400"></canvas>
        <script>
            const ctx = document.getElementById('myChart').getContext('2d');
            const labels = {labels}
            const config ={{
                type: 'bar',
                backgroundColor: "yellow",
                data: {{
                labels: labels,
                datasets: [{{
                    label: '{tag}',
                    data: {[(act.duration.seconds)/60 for act in act_arr]},
                    fill: false,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }}]
                }},
                
            }}
            const myChart = new Chart(ctx, config);
        </script>'''
    return graph_html

def get_report_for_tag(tag_name,start,end):
    to_time = end
    from_time = start
    res_json = getactivities_json(to_time,from_time)
    text = ""
    dur = timedelta(hours=0)
    for activity in res_json['activities']:
        if activity['displayName'].lower() == tag_name.lower():
            starttime = datetime.fromisoformat(activity['startTime'])
            endtime= datetime.fromisoformat(activity['endTime'])
            duration = endtime - starttime
            # date = starttime.date
            try: 
                notes = activity['textData'].split('Notes')[1]
            except Exception as e:
                notes =""
            text += f"""on: {starttime.date()} \n{starttime.hour}:{starttime.minute} \nduration:{duration}\nNotes:\n {notes} \n\n\n"""
            dur +=duration
    return (dur, text)
        



def create_activity_tag(user_tag,notes,datetimeObj,duration,datetimestr=''):
    response = requests.get(f'{SERVER_LINK}/api/timelines', headers=headers)
    timelines = json.loads(response.text)
    for timeline in timelines['timelines']:
        if timeline['timelineType']['typeName'] =="ManicTime/Tags":
            tags_timeline_id = timeline['timelineId']
    start = f"{datetimeObj.isoformat()}+{newzealnd}:00"
    if datetimestr !='':
        start = str(datetimestr)
    post_json = json.dumps({
        "values":{
            "name": user_tag,
            "notes":notes.strip(),
            "timeInterval": {
                "start": start,
                "duration": duration
            }
        }
    })
    headers1 = {
        'Accept': 'application/vnd.manictime.v3+json',
        'Content-Type': 'application/vnd.manictime.v3+json',
        'Authorization': f'Bearer {AUTH_TOKEN}',
    }
    response = requests.post(url=f'{SERVER_LINK}/api/timelines/{tags_timeline_id}/activities',data=post_json,headers=headers1)
    print(response.text)





def getNow():
    return datetime.utcnow()+ timedelta(hours=newzealnd)


def get_formated_time(dto):
    return f'{dto.hour}:{dto.minute}:{dto.second}'

def getLastfewHours(notes_needed,hours_wanted=12):
    text = ""
    
    to_time =  getNow()
    
    from_time = to_time - timedelta(hours = hours_wanted)

    res_json = getactivities_json(to_time,from_time)

    for activity in res_json['activities']:
        duration = datetime.fromisoformat(activity['endTime']) - datetime.fromisoformat(activity['startTime'])
        notes = ""
        if notes_needed == True:
            try: 
                notes = "\n Notes:"+ activity['textData'].split('Notes')[1]
                notes = notes.replace('>',"")
                notes = notes.replace('</',"")
            except Exception as e:
                notes = ""

        text += f'{activity["startTime"].split("T")[1].split("+")[0][0:5]} - {activity["endTime"].split("T")[1].split("+")[0][0:5]} - {duration} - {activity["displayName"]}  {notes} \n'
    return text 


def gettimeofact(act):
    return datetime.fromisoformat(act['startTime'])

def fix_manictime(minutes=30):
    to_time = getNow()
    from_time = to_time - timedelta(minutes=minutes)
    res_json = getactivities_json(to_time,from_time)
    activities_array = (res_json['activities'])
    sorted_act_array = newlist = sorted(activities_array, key=lambda x: x['endTime'] )
    for  activity in sorted_act_array:
            index = sorted_act_array.index(activity)
            activity1 = activity
            
            if (index+1)< len(sorted_act_array):
                activity2 = sorted_act_array[index+1]
                a2start =  datetime.fromisoformat(activity2['startTime'])
                a1end = datetime.fromisoformat(activity1['endTime'])
                delta = a2start-a1end 
                if activity1['displayName']==activity2['displayName']:
                    merge_activities(activity1,activity2)
                    return fix_manictime()
                elif delta > timedelta(seconds=0):
                    update_activity_start(activity2,a1end,delta)



def merge_activities(act1,act2):
    a2end = datetime.fromisoformat(act2['endTime'])
    a1start = datetime.fromisoformat(act1['startTime'])
    duration = str((a2end-a1start).total_seconds()).split('.')[0]
    merged_notes = ""
    try:
        a1notes=  notes = act1['textData'].split("<")[2].split('Notes>')[1]
    except KeyError:
        a1notes =""
    try:
        a2notes =  notes = act2['textData'].split("<")[2].split('Notes>')[1]
    except KeyError:
        a2notes =""
    merged_notes = a1notes +"\n"+a2notes 
    create_activity_tag(act1['displayName'],merged_notes,a1start,duration,a1start)
    deleteActivity(act1)
    deleteActivity(act2)

def deleteActivity(act):
    act_id = act['activityId']
    response = requests.get(f'{SERVER_LINK}/api/timelines', headers=headers)
    timelines = json.loads(response.text)
    for timeline in timelines['timelines']:
        if timeline['timelineType']['typeName'] =="ManicTime/Tags":
            tags_timeline_id = timeline['timelineId']
    headers1 = {
        'Accept': 'application/vnd.manictime.v3+json',
        'Content-Type': 'application/vnd.manictime.v3+json',
        'Authorization': f'Bearer {AUTH_TOKEN}',
    }
    response = requests.delete(f'{SERVER_LINK}/api/timelines/{tags_timeline_id}/activities/{act_id}', headers=headers1)
    print(response.text)

def update_activity_start(activity,new_start_time,delta):
    act_id = activity['activityId']
    response = requests.get(f'{SERVER_LINK}/api/timelines', headers=headers)
    timelines = json.loads(response.text)
    for timeline in timelines['timelines']:
        if timeline['timelineType']['typeName'] =="ManicTime/Tags":
            tags_timeline_id = timeline['timelineId']
    owndelta = datetime.fromisoformat(activity['endTime']) - datetime.fromisoformat(new_start_time.isoformat())
    newduration = str(owndelta.total_seconds()).split('.')[0]
    try:
        notes = activity['textData'].split("<")[2].split('Notes>')[1]
    except KeyError:
        notes = ""
    payload = json.dumps({
         "values":{
            "name": activity['displayName'],
            "notes":notes.strip(),
            "timeInterval": {
                "start": f"{new_start_time.isoformat()}",
                "duration": newduration,
            }
        }
    })
    headers1 = {
        'Accept': 'application/vnd.manictime.v3+json',
        'Content-Type': 'application/vnd.manictime.v3+json',
        'Authorization': f'Bearer {AUTH_TOKEN}',
    }
    response = requests.put(f'{SERVER_LINK}/api/timelines/{tags_timeline_id}/activities/{act_id}', headers=headers1,data=payload)
    print(response.text)
    # res_json = json.loads(response.text)
    # print(res_json)
    # return res_json


#fix_manictime()
            

def get_time_spent_today(tag):
    now = getNow()
    from_time = now - timedelta(hours=now.hour,minutes=now.minute,seconds=now.second)
    to_time = now
    unique_acts = get_unique_activities(to_time,from_time)
    for act in unique_acts:
        if (act['name']).strip().lower() == tag.strip().lower():
            return act['totalTime']
    return ""

   
