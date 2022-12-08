from os.path import exists
from time import sleep
import requests
import json
import datetime
import os
from manictime  import AUTH_TOKEN,SERVER_LINK
path_to_file = "/home/ubuntu/code/dashboard/frontend/src/manictime.json"

def getactivities_json(to_time,from_time):
    headers = {
        'Accept': 'application/vnd.manictime.v2+json',
        'Authorization': f'Bearer {AUTH_TOKEN}',
    }
    response = requests.get(f'{SERVER_LINK}/api/timelines', headers=headers)
    if response.status_code!=200:
        return json.dumps({"status":"error occured with manictime request"})
    timelines = json.loads(response.text)
    for timeline in timelines.get('timelines'):
        if timeline.get('timelineType').get('typeName') =="ManicTime/Tags":
            tags_timeline_id = timeline.get('timelineId')
    print('making manictime request')
    response = requests.get(f'{SERVER_LINK}/api/timelines/{tags_timeline_id}/activities?fromTime={from_time}&toTime={to_time}', headers=headers)
    res_json = json.loads(response.text)
    return res_json

def get_json_object(lock=1):
    to_time=datetime.datetime.utcnow()+datetime.timedelta(days=5)
    from_time=to_time-datetime.timedelta(days=106)
    with open(path_to_file, 'w') as manictime_json_file:
        if lock == 1:
            manictime_json_file.write(json.dumps(getactivities_json(to_time,from_time)))
        else:
            manictime_json_file.write("")
    return getactivities_json(to_time,from_time)

def generate_html():
    json_obj=get_json_object()
    json_string_for_js=json.dumps(json_obj)
    html = ""
    for activity in json_obj.get('activities'):
        act_name=activity.get('displayName')
        act_st=activity.get('startTime')
        act_et=activity.get('endTime')
        act_notes_xml=activity.get('textData')

    html+=f"<script>const data= {json_string_for_js}; console.log(data)</script>"
    return str(html)

