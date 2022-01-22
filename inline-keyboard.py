# https://api.telegram.org/1909326610:AAFh7rsp1dbD6XJ2IGmn5Og8ZfIuF6ZRmNk/getupdates?timeout=100
import requests

base_url = "https://api.telegram.org/1909326610:AAFh7rsp1dbD6XJ2IGmn5Og8ZfIuF6ZRmNk"
LAKSHAY_CID= 1040271347
text = """please select a goal to work on from the following
1 be productive
2 fix CTKCYB-5600
3 fix CTKCYB-5601
4 Improve goals-cli"""
reply_markup = '''{"inline_keyboard":[[{"text":"1","url":"http://t.co/"},{"text":"2","url":"http://t.co/"},
{"text":"3","url":"http://t.co/"}
]]}'''

url = f"{base_url}/sendmessage?text={text}&chat_id={LAKSHAY_CID}&reply_markup={reply_markup}"
r = requests.get(url)

print (r.text)
