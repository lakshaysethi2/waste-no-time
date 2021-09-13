from main import bot, LAKSHAY_CID,timedelta,datetime

import schedule
import time


def there_is_no_tag(from_time,to_time)->bool:
    """returns true if thre is no tag in from time, to time , if tag is found returns false
    so can be used like if there_is_no_tag"""

    return True

def check():
    now = datetime.utcnow() + timedelta(hours =12)
    to_time = now
    from_time = to_time - timedelta(minutes=15)
    
    if there_is_no_tag(from_time, to_time):
        cid = LAKSHAY_CID
        text = 'long time no tag mate!, what have you been up to?'
        bot.send_message(cid,text=text,reply_markup= rm)
        


# schedule.every(10).minutes.do(job)
# schedule.every().hour.do(job)
# schedule.every().day.at("10:30").do(job)
# schedule.every(5).to(10).minutes.do(job)
# schedule.every().monday.do(job)
# schedule.every().wednesday.at("13:15").do(job)
# schedule.every().minute.at(":17").do(job)

schedule.every(10).seconds.do(check)

while True:
    schedule.run_pending()
    time.sleep(1)
