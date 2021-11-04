from manictime import getLastfewHours
from types import SimpleNamespace
def get_calendar_html():

    html = ''


    text = getLastfewHours(False) 
    # this text we need to parse and write an html file 
    lines = text.split('\n')
    activities = []
    for line in lines:
        if 'from - to - activity' not in line:
            act = SimpleNamespace()
            act.from_time = line.split(' - ')[0]
            act.to_time = line.split(' - ')[2]
            act.duration = line.split(' - ')[3]
            act.tag = line.split(' - ')[4]
            

           


