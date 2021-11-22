from peewee import ProgrammingError
from manictime import getLastfewHours
from types import SimpleNamespace

def getStyle(tag:str):
    color = ""
    if 'programming' in tag.lower():
        color = '#a4ed82'
    elif 'uber' in tag.lower():
        color = '#656664'
    elif 'ctek' in tag.lower():
        color = '#72dba1'
    elif 'sleep' in tag.lower():
        color = '#373837'
    elif 'bio' in tag.lower():
        color = "#f54949"
    return f'background-color:{color};'

def get_calendar_html():

    text = getLastfewHours(False,24) 
    # this text we need to parse and write an html file 
    lines = text.split('\n')
    activities = []
    for line in lines:
        if 'from - to - activity' not in line and line !='':
            act = SimpleNamespace()
            act.from_time = line.split(' - ')[0]
            act.to_time = line.split(' - ')[1]
            act.duration = line.split(' - ')[2]
            act.tag = line.split(' - ')[3].strip()
            act.style = getStyle(act.tag)
            activities.append(act)


    return getHtml(activities)

#1 minute = 0.70 pixels
# = 1 minute = 0.7*3 = 2  pixel
def getHeight(dur_string):
    height_px = 2
    split = dur_string.split(":")
    hours = int(split[0])*60*2
    minutes_px = int(split[1])*2
    # sec = int(split[2])
    height_px += hours + minutes_px
    return height_px
    # 11:11:03


def getHtml(activities):
    act_div = ""
    for act in activities:
        name = act.tag
        height = getHeight(act.duration)
        duration = act.duration
        
        act_div += f'''<div style="height:{height}px; {act.style}" class = "activity-aware act-1"> 
                            {act.from_time} - {name}<br>   
                            ------- {duration}   
                            <div class = "notes">  
                                <textarea></textarea>
                            </div>
                            <div class="to-time">{act.to_time}</div> 
                        </div>
                    '''


    return    f'''<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.0/css/bootstrap-grid.min.css" integrity="sha512-3AxW5HcDzhL9MJdO2mpDEGEZ6NcCg/pDSa8R2kH5gwEA4r48RxZf0nPITA1NfX1pNA6a/eAayX+yW6QopF4jeg==" crossorigin="anonymous" referrerpolicy="no-referrer" />
        </head>
        <body>
            <style>
                .act-1 {{ border:solid 1px; overflow:hidden;position: relative; }}
               .to-time{{  position: absolute; bottom: 0;  }}
            </style>
            <div class="container">
                <div class="row">
                <div class="col">{act_div}</div>
                </div>
            </div>
       
        <script>
        let all_activity_divs = document.querySelectorAll(".activity-aware")
        function change_color(b){{
        if (b.style.background == 'red'){{
            b.style.background = 'white';
        }}
        else if (b.style.background == 'white'){{
            b.style.background = 'green'
        }}else{{b.style.background = "red"}}
        }}
        all_activity_divs.forEach(  (b) =>{{b.addEventListener('click',()=>{{change_color(b)}})}})
        </script>
        </body>
        </html> '''
