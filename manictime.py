
from datetime import timezone
from operator import itemgetter
import math
SERVER_LINK = 'https://manictime.lak.nz'
AUTH_TOKEN = "5989585dc24846a6aaf2febe48e37879"
tags_timeline_id = ''
import requests
import json
from datetime import datetime,timedelta,timezone
LAKSHAY_CID =1040271347
try:
    from keyvalue import *
except:
    from .keyvalue import *

newzealnd = 13
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
    timelines = json.loads(response.text)
    for timeline in timelines['timelines']:
        if timeline['timelineType']['typeName'] =="ManicTime/Tags":
            tags_timeline_id = timeline['timelineId']
    response = requests.get(f'{SERVER_LINK}/api/timelines/{tags_timeline_id}/activities?fromTime={from_time}&toTime={to_time}', headers=headers)
    res_json = json.loads(response.text)
    return res_json




def get_activities_for_awareness(to_time,from_time):
    res_json = getactivities_json(to_time,from_time)
    unique_activities = []
    interval_str =""
    
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
    total = timedelta(hours=0)
    for index,ua in enumerate(unique_activities):
        if index < 10:
            total += ua["totalTime"]
            interval_str += f'''{str(math.floor(ua["totalTime"].total_seconds()/3600)).split(":")[0]}h{str(ua["totalTime"]).split(":")[1]}m  -  {ua["name"] }\n'''
    total= round(total.total_seconds()/3600 ,2) 
    interval_str += 'top %\n\n'
    for index,ua in enumerate(unique_activities):
        if index<5:
            percent = round(((ua["totalTime"].total_seconds()/3600)/total)*100,2)
            interval_str += f'{percent}% {round(percent/100*24,1)}hr - {ua["name"] }  \n'
    interval_str += f'total: {total}\n'
    return interval_str 
 

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
   

def get_top_for_days(bot,days):
    now = getNow()
    to_time = now
    text = ""
    from_time = now - timedelta(days=days)
    text += f'\nlast {days} days top activities\n'+ get_activities_for_awareness(to_time,from_time)
    bot.send_message(LAKSHAY_CID,text=text)
    


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

def getLastfewHours(notes_needed):
    text = ""
    
    to_time =  getNow()
    
    from_time = to_time - timedelta(hours = 12)

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

def fix_manictime():
    to_time = getNow()
    from_time = to_time - timedelta(hours=20)
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
            


   
