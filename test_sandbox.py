from test_tgb import create_message_obj
from main import LAKSHAY_CID, TOKEN, requests, json, the_activities_markup,get_reply_markup_for_now,check
from main import set_value
from main import get_value

def test_backwards_compatibality_with_rm():
    set_value("ci", '0')
    set_value("mt", 'on')
    mt_val = get_value("mt")
    ci_val = get_value("ci")
    assert mt_val == 'on'
    assert ci_val == '0'


