# https://api.telegram.org/bot5061167346:AAECJdb_-U9jQorMiJRsITRJBRyf-53Ctv4/getupdates?timeout=100
import requests
import json

base_url = "https://api.telegram.org/bot5061167346:AAECJdb_-U9jQorMiJRsITRJBRyf-53Ctv4"
LAKSHAY_CID= 1040271347
text = """select your energy level"""
reply_markup = json.loads('{"inline_keyboard":[[]]}')
ik = reply_markup.get('inline_keyboard')
ik[0].append({'text': 'very low', 'url': 'idk.lak.nz'})
ik[0].append({'text': 'low', 'url': 'idk.lak.nz'})
ik[0].append({'text': 'low-med', 'url': 'idk.lak.nz'})
ik[0].append({'text': 'high-med', 'url': 'idk.lak.nz'})
ik[0].append({'text': 'high', 'callback_data': 'idk.lak.nz'})
reply_markup = json.dumps(reply_markup)
url = f"{base_url}/sendmessage?text={text}&chat_id={LAKSHAY_CID}&reply_markup={reply_markup}"
r = requests.get(url)

print (r.text)
