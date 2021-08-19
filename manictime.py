
from datetime import timezone
from operator import itemgetter
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
    total =timedelta(hours=0)
    for activity in res_json['activities']:
        if activity['displayName'] not in str(unique_activities):
            ua = {'name':activity['displayName'],
            'totalTime':datetime.fromisoformat(activity['endTime']) - datetime.fromisoformat(activity['startTime'])}
            unique_activities.append(ua)
        elif activity['displayName'] in str(unique_activities):
            for ua in unique_activities:
                if ua['name'] == activity['displayName']:
                    ua['totalTime'] += datetime.fromisoformat(activity['endTime']) - datetime.fromisoformat(activity['startTime'])
        
        total += (datetime.fromisoformat(activity['endTime']) - datetime.fromisoformat(activity['startTime']))
    
    unique_activities = sorted(unique_activities, key=itemgetter('totalTime'), reverse=True)
    for index,ua in enumerate(unique_activities):
        interval_str += f'''{ ua["totalTime"] }  -  {ua["name"] }\n'''
    return interval_str 


def get_manictime_yesterday(bot,message):
    now = datetime.now()
    today_started = now - timedelta(hours=now.hour) - timedelta(minutes=now.minute) -timedelta(seconds=61)
    to_time = today_started
    from_time = today_started -timedelta(days=1)
    text = "yesterday\n"+  get_activities_for_awareness(to_time,from_time)
    bot.send_message(message.chat.id,text=text)
    # return f""" yesterday: \n8.2   sleep \n3.2   programming \n3.2   food \n2.3   doing phone """

def get_manictime_today(bot,message):
    now = datetime.now()
    today_started = now - timedelta(hours=now.hour) - timedelta(minutes=now.minute)
    to_time = now
    from_time = today_started
    
    text = 'today\n'+ get_activities_for_awareness(to_time,from_time)
    bot.send_message(message.chat.id,text=text)
    # return f""" today:\n    9.5   sleep \n     3.2   programming \n    2.0   food \n    1.3   doing phone """


