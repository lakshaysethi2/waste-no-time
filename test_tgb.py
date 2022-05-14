from main import *
import pytest

def setup_for_last_used():

    set_value('last_used', "")
    set_value('last_to_last_used', "")
    set_value('last_to_last_to_last_used', "")
    set_value('last_to_last_to_last_to_last_used', "")

    test_reply_markup_before = get_reply_markup_for_now()
    chat =  telebot.types.Chat(LAKSHAY_CID, 'type')
    message = telebot.types.Message(123, 'from_user', getNow(),chat , content_type='text', options=[], json_string='')
    message.chat.id = LAKSHAY_CID
    return message

def test_last_2_used_are_unique():
    """
    runs /now prog 
    then /now prog 
    and tests if 2 same are not shown twice in teh reply markup
    """
    message = setup_for_last_used()
    message.text = '/now programming'
    now(message)
    now(message)
    test_reply_markup_now = get_reply_markup_for_now()
    assert test_reply_markup_now.keyboard[0] == [{'text':'/now programming'}]
    assert test_reply_markup_now.keyboard[1] != [{'text':'/now programming'}]


def test_last_used_array_works_with_last4():
    """
    runs /now prog 
    then /now test 
    then /now Trying or setting up
    then /now cleaning
    and tests if reply markup has /now prog then /now test then .. and then the default array
    """
    message = setup_for_last_used()
    msg_txt1 = '/now programming, tgb can do 1 '
    msg_txt2 = '/now programming, tgb can do 2'
    msg_txt3 = '/now testing, tbb can do 3'
    msg_txt4 = '/now testing, tbb can do 4'
    message.text = msg_txt1
    now(message)
    sleep(1)
    message.text = msg_txt2
    now(message)
    sleep(1)
    message.text = msg_txt3
    now(message)
    sleep(1)
    message.text = msg_txt4
    now(message)
    test_reply_markup_now = get_reply_markup_for_now()
    assert test_reply_markup_now.keyboard[3] == [{'text':msg_txt1}]
    assert test_reply_markup_now.keyboard[2] == [{'text':msg_txt2}]
    assert test_reply_markup_now.keyboard[1] == [{'text':msg_txt3}]
    assert test_reply_markup_now.keyboard[0] == [{'text':msg_txt4}]
