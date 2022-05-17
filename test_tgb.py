from main import *
import pytest

msg_txt1 = '/now programming, tgb can do 1 '
msg_txt2 = '/now programming, tgb can do 2'
msg_txt3 = '/now testing, tbb can do 3'
msg_txt4 = '/now testing, tbb can do 4'

def setup_for_last_used():
    set_value("last_used", '/now manictime')
    set_value('last_to_last_used', "/now programming")
    set_value('last_to_last_to_last_used', "/now testing")
    set_value('last_to_last_to_last_to_last_used', "/now reading")

    chat =  telebot.types.Chat(LAKSHAY_CID, 'type')
    message = telebot.types.Message(123, 'from_user', getNow(),chat , content_type='text', options=[], json_string='')
    message.chat.id = LAKSHAY_CID
    return message

def send_basic_messages(message):
    message.text = msg_txt1
    now(message)
    message.text = msg_txt2
    now(message)
    message.text = msg_txt3
    now(message)
    message.text = msg_txt4
    now(message)

def test_last_4_used_are_unique():
    message = setup_for_last_used()
    send_basic_messages(message)
    test_reply_markup_now = get_reply_markup_for_now()
    assert test_reply_markup_now.keyboard[0] != test_reply_markup_now.keyboard[1] != test_reply_markup_now.keyboard[2] != test_reply_markup_now.keyboard[3]
    message.text = msg_txt1
    now(message)
    message.text = msg_txt2
    now(message)
    message.text = msg_txt1
    now(message)
    message.text = msg_txt2
    now(message)
    test_reply_markup_now = get_reply_markup_for_now()
    assert test_reply_markup_now.keyboard[0] != test_reply_markup_now.keyboard[2] 
    assert test_reply_markup_now.keyboard[1] != test_reply_markup_now.keyboard[3]
    
def test_last_used_array_works_with_last4():
    message = setup_for_last_used()
    send_basic_messages(message)
    test_reply_markup_now = get_reply_markup_for_now()
    assert test_reply_markup_now.keyboard[3] == [{'text':msg_txt1}]
    assert test_reply_markup_now.keyboard[2] == [{'text':msg_txt2}]
    assert test_reply_markup_now.keyboard[1] == [{'text':msg_txt3}]
    assert test_reply_markup_now.keyboard[0] == [{'text':msg_txt4}]
