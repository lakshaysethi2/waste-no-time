from main import *
import pytest

the_arr = [msg_txt1,
msg_txt2,
msg_txt3,
msg_txt4,
msg_txt5,
msg_txt6,
msg_txt7,
msg_txt8] = [
    '/now programming',
'/now manictime',
'/now reading',
'/now walking',
'/now writing',
'/now exercise',
'/now udemy',
'/now linux',
]

def setup_for_last_used():
    set_value("last_useda", msg_txt1)
    set_value('last_usedb', msg_txt2)
    set_value('last_usedc', msg_txt3)
    set_value('last_usedd', msg_txt4)

def create_message_obj():
    chat =  telebot.types.Chat(LAKSHAY_CID, 'type')
    message = telebot.types.Message(123, 'from_user', getNow(),chat , content_type='text', options=[], json_string='')
    message.chat.id = LAKSHAY_CID
    return message

def send_basic_messages():
    set_reply_markup_last_used(msg_txt1)
    set_reply_markup_last_used(msg_txt2)
    set_reply_markup_last_used(msg_txt3)
    set_reply_markup_last_used(msg_txt4)


def test_last_n_used_are_unique():
    n = 8
    for i in range(0, n):
        set_reply_markup_last_used(the_arr[i])
    test_reply_markup_now = json.loads(get_reply_markup_for_now())
    for i in range(0, n):
        for j in range(i+1, n):
            assert test_reply_markup_now['keyboard'][i] != test_reply_markup_now['keyboard'][j]

def test_last_5_used_are_unique():
    setup_for_last_used()
    send_basic_messages()
    test_reply_markup_now = json.loads(get_reply_markup_for_now())
    assert test_reply_markup_now['keyboard'][0] != test_reply_markup_now['keyboard'][1]
    assert test_reply_markup_now['keyboard'][0] != test_reply_markup_now['keyboard'][2]
    assert test_reply_markup_now['keyboard'][0] != test_reply_markup_now['keyboard'][3]
    assert test_reply_markup_now['keyboard'][1] != test_reply_markup_now['keyboard'][2]
    assert test_reply_markup_now['keyboard'][1] != test_reply_markup_now['keyboard'][3]
    assert test_reply_markup_now['keyboard'][2] != test_reply_markup_now['keyboard'][3]
    set_reply_markup_last_used( msg_txt1)
    set_reply_markup_last_used( msg_txt2)
    set_reply_markup_last_used( msg_txt1)
    set_reply_markup_last_used( msg_txt2)
    test_reply_markup_now = json.loads(get_reply_markup_for_now())
    assert test_reply_markup_now['keyboard'][0] != test_reply_markup_now['keyboard'][1]
    assert test_reply_markup_now['keyboard'][0] != test_reply_markup_now['keyboard'][2]
    assert test_reply_markup_now['keyboard'][0] != test_reply_markup_now['keyboard'][3]
    assert test_reply_markup_now['keyboard'][1] != test_reply_markup_now['keyboard'][2]
    assert test_reply_markup_now['keyboard'][1] != test_reply_markup_now['keyboard'][3]
    assert test_reply_markup_now['keyboard'][2] != test_reply_markup_now['keyboard'][3]


def test_last_used_array_works_with_last5():
    n = 5
    for i in range(0, n):
        set_reply_markup_last_used(the_arr[i])
    set_reply_markup_last_used(msg_txt1)
    set_reply_markup_last_used(msg_txt2)
    set_reply_markup_last_used(msg_txt3)
    set_reply_markup_last_used(msg_txt4)
    set_reply_markup_last_used(msg_txt5)
    test_reply_markup_now = json.loads(get_reply_markup_for_now())
    assert test_reply_markup_now['keyboard'][0] == [msg_txt5]
    assert test_reply_markup_now['keyboard'][1] == [msg_txt4]
    assert test_reply_markup_now['keyboard'][2] == [msg_txt3]
    assert test_reply_markup_now['keyboard'][3] == [msg_txt2]
    assert test_reply_markup_now['keyboard'][4] == [msg_txt1]

def test_top_reply_button_is_always_last_used():
    setup_for_last_used()
    send_basic_messages()
    test_reply_markup_now = json.loads(get_reply_markup_for_now())
    set_reply_markup_last_used(msg_txt3)
    test_reply_markup_now = json.loads(get_reply_markup_for_now())
    assert test_reply_markup_now['keyboard'][0] == [msg_txt3]
    set_reply_markup_last_used(msg_txt2)
    test_reply_markup_now = json.loads(get_reply_markup_for_now())
    assert test_reply_markup_now['keyboard'][0] == [msg_txt2]
    set_reply_markup_last_used(msg_txt1)
    test_reply_markup_now = json.loads(get_reply_markup_for_now())
    assert test_reply_markup_now['keyboard'][0] == [msg_txt1]
    set_reply_markup_last_used(msg_txt4)
    test_reply_markup_now = json.loads(get_reply_markup_for_now())
    assert test_reply_markup_now['keyboard'][0] == [msg_txt4]


def test_app_does_not_break_if_same_is_supplied_twice():
    setup_for_last_used()
    message= msg_txt3
    set_reply_markup_last_used(message)
    test_reply_markup_now = json.loads(get_reply_markup_for_now())
    set_reply_markup_last_used(message)
    test_reply_markup_now = json.loads(get_reply_markup_for_now())
    assert test_reply_markup_now['keyboard'][0] == [msg_txt3]
    assert test_reply_markup_now['keyboard'][1] != [msg_txt3]

@pytest.mark.skip(reason="not implemented yet")
def test_require_notes():
    message = create_message_obj()
    message.text = f'/now trying or setting up'
    assert set_reply_markup_last_used(message) is False
    message.text = f'/now testing, testing notes required'
    assert set_reply_markup_last_used(message) is True
@pytest.mark.skip(reason="not implemented yet")
def test_budget():
    message = create_message_obj()
    budgets(message)

def test_notes_should_not_show_up_in_reply_markup():
    setup_for_last_used()
    message = "/now programming"
    set_reply_markup_last_used(message)
    message = "/now programming, hi"
    set_reply_markup_last_used(message)
    test_reply_markup_now = json.loads(get_reply_markup_for_now())
    assert test_reply_markup_now["keyboard"][0] == ['/now programming']
    assert test_reply_markup_now["keyboard"][0] != ['/now programming,hi']
    message = "/now linux"
    set_reply_markup_last_used(message)
    message = "/now linux, hi"
    set_reply_markup_last_used(message)
    test_reply_markup_now = json.loads(get_reply_markup_for_now())
    assert test_reply_markup_now["keyboard"][0] == ['/now linux']
    assert test_reply_markup_now["keyboard"][0] != ['/now linux,hi']
    assert test_reply_markup_now["keyboard"][1] == ['/now programming']
    assert test_reply_markup_now["keyboard"][1] != ['/now programming,hi']


@pytest.mark.skip(reason="not implemented yet")
def test_last_x_used_in_reply_markup():
    message = create_message_obj()
    setup_for_last_used()
    message.text = msg_txt4
    set_reply_markup_last_used(message)
    message.text = msg_txt5
    set_reply_markup_last_used(message)
    message.text = msg_txt6
    set_reply_markup_last_used(message)
    message.text = msg_txt7
    set_reply_markup_last_used(message)
    message.text = msg_txt8
    set_reply_markup_last_used(message)
    test_reply_markup_now = json.loads(get_reply_markup_for_now())
    assert test_reply_markup_now["keyboard"][3] == [msg_txt5]
    assert test_reply_markup_now["keyboard"][2] == [msg_txt6]
    assert test_reply_markup_now["keyboard"][1] == [msg_txt7]
    assert test_reply_markup_now["keyboard"][0] == [msg_txt8]
    assert test_reply_markup_now["keyboard"][4] == [msg_txt4]
@pytest.mark.skip(reason="not implemented yet")
def test_manual_calendar():
    message = create_message_obj()
    message.text = "/calendar"
    last(message)
@pytest.mark.skip(reason="not implemented yet")
def test_top_piechart_and_percent():
    message = create_message_obj()
    message.text = "/top 2"
    assert "pie" in str(manictime_top(message))
@pytest.mark.skip(reason="not implemented yet")
def test_no_notes_in_last_used():
    message = create_message_obj()
    setup_for_last_used()
    message.text = "/now food"
    set_reply_markup_last_used(message)
    message.text = "/now food, bla"
    set_reply_markup_last_used(message)
    test_reply_markup_now = json.loads(get_reply_markup_for_now())
    assert test_reply_markup_now["keyboard"][4] == ["/now food"]
    assert test_reply_markup_now["keyboard"][3] != ["/now food, bla"]
@pytest.mark.skip(reason="not implemented yet")
def test_top_more_items():
    message = create_message_obj()
    # message.text = "/top 24*300"
    # manictime_top(message)
    message.text = "/top 1"
    manictime_top(message)

@pytest.mark.skip(reason="not implemented yet")
def test_pdf_works():
    message = create_message_obj()
    message.text = "/top 10"
    manictime_top(message)
    assert True
@pytest.mark.skip(reason="not implemented yet")
def test_toggle_strict_notes_mode():
    message = create_message_obj()
    message.text = "/key strict_notes, yes"
    keyvalue(message)
    message.text = "/now Trying or setting up"
    tagmade = set_reply_markup_last_used(message)
    assert tagmade is False
    message.text = "/key strict_notes, no"
    keyvalue(message)
    message.text = "/now Trying or setting up"
    tagmade = set_reply_markup_last_used(message)
    assert tagmade is True

@pytest.mark.skip(reason="not implemented yet")
def test_timesheet_test():
    message = create_message_obj()
    message.text = "/timesheet driving,100,1"
    timesheet_html(message)
@pytest.mark.skip(reason="not implemented yet")   
def test_top_has_piechart():
    message = create_message_obj()
    message.text = "/top 10"
    manictime_top(message)
@pytest.mark.skip(reason="not implemented yet")
def test_pdf_in_summary():
    message = create_message_obj()
    message.text = "/summary 3"
    summary(message)
@pytest.mark.skip(reason="not implemented yet")
def test_key_reply_markup():
    message = create_message_obj()
    message.text = "/key ci, 1"
    assert keyvalue(message).get("reply_markup") is None


@pytest.mark.skip(reason="not implemented yet")
def test_dash_lock_unlock():
    message = create_message_obj()
    message.text = "/unlockdash"
    resp = unlockdash(message)

@pytest.mark.skip(reason="not implemented yet")
def test_manictime_message_updated():
    message = create_message_obj()
    message.text = "/now programming, tgb"
    resp = set_reply_markup_last_used(message)
