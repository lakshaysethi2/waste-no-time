
from datetime import timezone
from operator import itemgetter
SERVER_LINK = 'https://manictime.lak.nz'
AUTH_TOKEN = "5989585dc24846a6aaf2febe48e37879"
tags_timeline_id = ''
import requests
import json
from datetime import datetime,timedelta,timezone

headers = {
    'Accept': 'application/vnd.manictime.v2+json',
    'Authorization': f'Bearer {AUTH_TOKEN}',
}

def get_token():

    headers = {
        'Accept': 'application/vnd.manictime.v2+json',
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
    }

    data = {
    'grant_type': 'password',
    'username': 'username',
    'password': 'password'
    }

    resp=  requests.post(f'{SERVER_LINK}/api/token', headers=headers,data=data)
    print (resp.text)

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
        # durationStr = f"{duration.hours}h {duration.minutes}m"
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
        if index < 6:
            total += ua["totalTime"]
            interval_str += f'''{str(round(ua["totalTime"].total_seconds()/3600)).split(":")[0]}h{str(ua["totalTime"]).split(":")[1]}m  -  {ua["name"] }\n'''
    total= round(total.total_seconds()/3600 ,2)  
    interval_str += f'total: {total}\n'
    return interval_str 
 

def get_manictime_yesterday(bot,message):
    now = datetime.now() + timedelta(hours=12)
    today_started = now - timedelta(hours=now.hour) - timedelta(minutes=now.minute) -timedelta(seconds=61)
    to_time = today_started
    from_time = today_started -timedelta(days=1)
    text = "yesterday\n"+  get_activities_for_awareness(to_time,from_time)
    bot.send_message(message.chat.id,text=text)
    # return f""" yesterday: \n8.2   sleep \n3.2   programming \n3.2   food \n2.3   doing phone """

def get_manictime_today(bot,message):
    now = datetime.now() + timedelta(hours=12)
    today_started = now - timedelta(hours=now.hour) - timedelta(minutes=now.minute)
    to_time = now
    from_time = today_started
    
    text = 'today\n'+ get_activities_for_awareness(to_time,from_time)
    bot.send_message(message.chat.id,text=text)
    # return f""" today:\n    9.5   sleep \n     3.2   programming \n    2.0   food \n    1.3   doing phone """



def get_manictime_7days_total(bot,message,goal):
    now = datetime.now() + timedelta(hours=12)
    
    to_time = now
    from_time = now - timedelta(hours=168)
    text = goal
    text += '\nlast 7 days \n'+ get_activities_for_awareness(to_time,from_time)
    bot.send_message(message.chat.id,text=text)
    # return f""" today:\n    9.5   sleep \n     3.2   programming \n    2.0   food \n    1.3   doing phone """




def get_manictime_last_x_days(bot,message,x):
    text = ""
    now = datetime.now() + timedelta(hours=12)
    for a in range (0,x):
        day_start = datetime(now.year,now.month,now.day,0,0) - timedelta(days=a)
        day_end = day_start+timedelta(hours=24)
        from_time = day_start
        to_time = day_end
        text += f'{day_start.day}-{day_start.month}\n'+ get_activities_for_awareness(to_time,from_time)
    bot.send_message(message.chat.id,text = text)


def get_report(tag,message,bot):
    to_time = datetime.now() + timedelta(hours=12)
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
    bot.send_message(message.chat.id,text)


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
        



def create_activity_tag(user_tag,notes,datetimeObj,duration):
    response = requests.get(f'{SERVER_LINK}/api/timelines', headers=headers)
    timelines = json.loads(response.text)
    for timeline in timelines['timelines']:
        if timeline['timelineType']['typeName'] =="ManicTime/Tags":
            tags_timeline_id = timeline['timelineId']
    post_json = json.dumps({
        "values":{
            "name": user_tag,
            "notes":notes,
            "timeInterval": {
                "start": f"{datetimeObj.isoformat()}"+"+12:00",
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
