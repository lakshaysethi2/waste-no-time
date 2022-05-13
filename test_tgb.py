from main import *
import pytest

def setup_for_last_used():
    if get_value('last_used'):
        set_value('last_used', "")
    test_reply_markup_before = get_reply_markup_for_now()
    chat =  telebot.types.Chat(LAKSHAY_CID, 'type')
    message = telebot.types.Message(123, 'from_user', getNow(),chat , content_type='text', options=[], json_string='')
    message.chat.id = LAKSHAY_CID
    return message

def test_last_used_array_is_unique():
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

def test_last_used_array_works():
    """
    runs /now prog 
    then /now test 
    and tests if reply markup has /now prog then /now test then the default array
    """
    message = setup_for_last_used()
    message.text = '/now programming'
    now(message)
    message.text = '/now testing'
    sleep(5)
    now(message)
    test_reply_markup_now = get_reply_markup_for_now()
    assert test_reply_markup_now.keyboard[0] == [{'text':'/now testing'}]
    assert test_reply_markup_now.keyboard[1] == [{'text':'/now programming'}]
