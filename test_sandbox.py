from test_tgb import create_message_obj
from main import LAKSHAY_CID, TOKEN, requests, json, activities_markup,get_reply_markup_for_now,check
from main import set_value

def test_reply_markup_3_btn_one_row():
    text = 'what have you been up to?'
    rm = get_reply_markup_for_now()
    url = f'https://api.telegram.org/bot{TOKEN}/sendmessage?text={text}&disable_notification=true&reply_markup={rm}'
    response = requests.post(url,data={"chat_id":LAKSHAY_CID})
    assert response.status_code == 200


def test_backwards_compatibality_with_rm():
    set_value("ci", '0')
    set_value("mt", 'on')
    check()
