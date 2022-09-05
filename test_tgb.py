from main import *
import pytest

msg_txt1 = '/now programming, tgb can do 1 '
msg_txt2 = '/now programming, tgb can do 2'
msg_txt3 = '/now testing, tbb can do 3'
msg_txt4 = '/now testing, tbb can do 4'
msg_txt5 = '/now tag5'
msg_txt6 = '/now tag6'
msg_txt7 = '/now tag7'
msg_txt8 = '/now tag8'

def setup_for_last_used():
    set_value("last_used", '/now manictime')
    set_value('last_to_last_used', "/now programming")
    set_value('last_to_last_to_last_used', "/now testing")
    set_value('last_to_last_to_last_to_last_used', "/now reading")

def create_message_obj():
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
    message = create_message_obj()
    setup_for_last_used()
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
    message = create_message_obj()
    setup_for_last_used()
    send_basic_messages(message)
    test_reply_markup_now = get_reply_markup_for_now()
    assert test_reply_markup_now.keyboard[3] == [{'text':msg_txt1}]
    assert test_reply_markup_now.keyboard[2] == [{'text':msg_txt2}]
    assert test_reply_markup_now.keyboard[1] == [{'text':msg_txt3}]
    assert test_reply_markup_now.keyboard[0] == [{'text':msg_txt4}]


def test_top_reply_button_is_always_last_used():
    message = create_message_obj()
    setup_for_last_used()
    send_basic_messages(message)
    test_reply_markup_now = get_reply_markup_for_now()
    message.text = msg_txt3
    now(message)
    test_reply_markup_now = get_reply_markup_for_now()
    assert test_reply_markup_now.keyboard[0] == [{'text':msg_txt3}]

def test_app_does_not_break_if_same_is_supplied_twice():
    message = create_message_obj()
    setup_for_last_used()
    message.text = msg_txt3
    now(message)
    test_reply_markup_now = get_reply_markup_for_now()
    now(message)
    test_reply_markup_now = get_reply_markup_for_now()
    assert test_reply_markup_now.keyboard[0] == [{'text':msg_txt3}]
    assert test_reply_markup_now.keyboard[1] != [{'text':msg_txt3}]

def test_require_notes():
    message = create_message_obj()
    message.text = f'/now trying or setting up'
    assert now(message) is False
    message.text = f'/now testing, testing notes required'
    assert now(message) is True

def test_budget():
    message = create_message_obj()
    budgets(message)

def test_notes_should_not_show_up_in_reply_markup():
    message = create_message_obj()
    setup_for_last_used()
    message.text = "/now abc"
    now(message)
    message.text = "/now abc, hi"
    now(message)
    # assert that /now programming, hi is not in reply markup
    test_reply_markup_now = get_reply_markup_for_now()
    assert test_reply_markup_now["keyboard"][0] == ['/now abc']
    assert test_reply_markup_now["keyboard"][0] != ['/now abc,hi']
    assert test_reply_markup_now["keyboard"][1] != ['/now abc,hi']
    assert test_reply_markup_now["keyboard"][2] != ['/now abc'] # should really be does not contain?
    assert test_reply_markup_now["keyboard"][3] != ['/now abc']
    assert test_reply_markup_now["keyboard"][4] != ['/now abc']
    


def test_last_x_used_in_reply_markup():
    message = create_message_obj()
    setup_for_last_used()
    message.text = msg_txt4
    now(message)
    message.text = msg_txt5
    now(message)
    message.text = msg_txt6
    now(message)
    message.text = msg_txt7
    now(message)
    message.text = msg_txt8
    now(message)
    test_reply_markup_now = get_reply_markup_for_now()
    assert test_reply_markup_now["keyboard"][3] == [msg_txt5]
    assert test_reply_markup_now["keyboard"][2] == [msg_txt6]
    assert test_reply_markup_now["keyboard"][1] == [msg_txt7]
    assert test_reply_markup_now["keyboard"][0] == [msg_txt8]
    assert test_reply_markup_now["keyboard"][4] == [msg_txt4]

def test_manual_calendar():
    message = create_message_obj()
    message.text = "/calendar"
    last(message)

def test_top_piechart_and_percent():
    message = create_message_obj()
    message.text = "/top 2"
    assert "pie" in str(manictime_top(message))

def test_no_notes_in_last_used():
    message = create_message_obj()
    setup_for_last_used()
    message.text = "/now food"
    now(message)
    message.text = "/now food, bla"
    now(message)
    test_reply_markup_now = get_reply_markup_for_now()
    assert test_reply_markup_now["keyboard"][4] == ["/now food"]
    assert test_reply_markup_now["keyboard"][3] != ["/now food, bla"]

def test_top_more_items():
    message = create_message_obj()
    # message.text = "/top 24*300"
    # manictime_top(message)
    message.text = "/top 1"
    manictime_top(message)


def test_pdf_works():
    message = create_message_obj()
    message.text = "/top 10"
    manictime_top(message)
    assert True

def test_toggle_strict_notes_mode():
    message = create_message_obj()
    message.text = "/key strict_notes, yes"
    keyvalue(message)
    message.text = "/now Trying or setting up"
    tagmade = now(message)
    assert tagmade is False
    message.text = "/key strict_notes, no"
    keyvalue(message)
    message.text = "/now Trying or setting up"
    tagmade = now(message)
    assert tagmade is True


def test_timesheet_test():
    message = create_message_obj()
    message.text = "/timesheet driving,100,1"
    timesheet_html(message)
   