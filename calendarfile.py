from manictime import getLastfewHours
from types import SimpleNamespace
def get_calendar_html():

    text = getLastfewHours(False) 
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
            activities.append(act)

    return getHtml(activities)


def getHeight(dur_string):
    height = 10
    split = dur_string.split(":")
    hours = int(split[0])*83
    min = int(split[1])*2
    # sec = int(split[2])
    height += hours + min
    return height
    # 11:11:03


def getHtml(activities):
    act_div = ""
    for act in activities:
        name = act.tag
        height = getHeight(act.duration)
        duration = act.duration
        
        act_div += f'<div style="height:{height}px" \
                    class = "activity-aware act-1 "> \
                            {name} {duration} \
                             t : {act.from_time}-{act.to_time} \
                        </div>'


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
                .act-1 {{ border-top:solid 5px;border-bottom: solid 5px;  }}
                .act-3 {{ border-bottom: solid 5px;  }}
            </style>

            
            <div class="container">
                <div class="row">
                <div class="col-4">{act_div}</div>

                    
                
                </div>
            </div>
            




        </body>
        </html> '''
