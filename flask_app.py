from flask import abort, Flask, request
from datetime import datetime
import requests
import json
import view_templates
import os


app = Flask(__name__)

with open('config.json', 'r') as config_file:
    config = json.load(config_file)
slack_token = config['SLACK']['verification_token']
bot_access_token = config['SLACK']['bot_access_token']
clear_notes_pwd = config['OTHER']['clear_notes_pwd']


### Method is invoked when slash command '/retronote' is used
@app.route('/', methods=['POST'])
def main():

    received_token = request.form['token']
    if received_token != slack_token:
        return abort(400)

    response_url = request.form['response_url']
    command_params = request.form['text'].strip().split(" ", 1)
    channel_id = request.form['channel_id']
    retro_file_name = get_retrofile_name(channel_id)

    ### When user invokes "/retronote help" or "/retronote h"
    if command_params[0] == 'help' or command_params[0] == 'h':
        show_help(response_url)

    ### When user invokes "/retronote add" or "/retronote add {SOME_TEXT}"
    elif command_params[0] == 'add':
        trigger_id = request.form['trigger_id']
        ### Check if user added some text after "/retronote add" and pass this text as param to be shown in the add note modal (in description field)
        if len(command_params) == 2:
            show_add_retronote_modal(channel_id, trigger_id, initial_description=command_params[1])
        else:
            show_add_retronote_modal(channel_id, trigger_id)

    ### When user invokes "/retronote list"
    elif command_params[0] == 'list':
        show_retronotes(response_url, retro_file_name)

    ### When user invokes "/retronote clear {SECRET PASSWORD}"
    elif len(command_params) == 2 and command_params[0] == 'clear' and command_params[1] == clear_notes_pwd:
        if is_file_exists(retro_file_name):
            os.remove(retro_file_name)
            requests.post(response_url, json=view_templates.get_simple_message_view("Зачистка произведена :wink:"))
        else:
            requests.post(response_url, json=view_templates.get_simple_message_view("Удалять нечего. Заметок ещё нет :eyes:"))

    ### When user invokes "/retronote download"
    elif command_params[0] == 'download':
        if is_file_exists(retro_file_name):
            with open(retro_file_name, "r") as retrofile:
                retronotes = retrofile.read()
            data = {
                "channels": channel_id,
                "title": "retronotes.txt",
                "initial_comment": "Файл со всеми созданными заметками для ретро готов к скачиванию",
                "filename": "retronotes.txt",
                "filetype": "text",
                "content": retronotes
            }
            requests.post('https://slack.com/api/files.upload', data=data,
                headers={'Authorization': 'Bearer {}'.format(bot_access_token)})

        else:
            requests.post(response_url, json=view_templates.get_simple_message_view("Нечего скачивать. Заметок ещё нет :eyes:"))

    ### Show main view when no params (keys) were used  with command or params were used in wrong format
    else:
        requests.post(response_url, json=view_templates.get_main_view())

    return ""


### Method is invoked when any interactions with shortcuts, modals, or
### interactive components (such as buttons, select menus, and datepickers) happen
@app.route('/slack/message_action/', methods=['POST'])
def process_message_action():

    received_data = request.form.to_dict(flat=False)
    payload = json.loads(received_data['payload'][0])
    received_token = payload["token"]
    response_url = payload.get("response_url")

    ### Debug method to view received payload
    #requests.post(response_url, json=view_templates.get_simple_message_view("```{}```".format(payload)))

    if received_token != slack_token:
        return abort(400)

    ### When user submits modal with filled fields of retronote
    if payload["type"] == "view_submission":
        return process_view_submission(payload)

    ### When user clicks "Help" in overflow menu
    if payload["type"] == "block_actions" and payload["actions"][0]["type"] == "overflow":
        if payload["actions"][0]["selected_option"]["value"] == "help_menuitem_selected":
            show_help(response_url)

    ### When user clicks "Add note" or "View notes" button in message
    if payload["type"] == "block_actions" and payload["actions"][0]["type"] == "button":

        ### When user clicks "Add note" button in message
        if payload["actions"][0]["value"] == "add_note":
            channel_id = payload["container"]["channel_id"]
            trigger_id = payload["trigger_id"]
            show_add_retronote_modal(channel_id, trigger_id)

         ### When user clicks "View notes" button in message
        if payload["actions"][0]["value"] == "view_notes":
            channel_id = payload["container"]["channel_id"]
            retro_file_name = get_retrofile_name(channel_id)
            show_retronotes(response_url, retro_file_name)

    ### When user clicks "Add as a retronote" shortcut
    if payload["type"] == "message_action" and payload["callback_id"] == "add_retronote_shortcut":
        message_text = payload["message"]["text"]
        channel_id = payload["channel"]["id"]
        trigger_id = payload["trigger_id"]
        show_add_retronote_modal(channel_id, trigger_id, initial_description=message_text)


    return ""


### Method is used to receive slack event notifications
# @app.route('/slack/event_action/', methods=['POST'])
# def process_event_action():
#     #received_data = request.form.to_dict(flat=False)

#     ### Debug method to view received payload
#     WEBHOOK_URL_MAX = 'https://hooks.slack.com/services/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'
#     requests.post(WEBHOOK_URL_MAX, json=view_templates.get_simple_message_view("```{}```".format(request.form.to_dict())))
#     challenge = "3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P"

#     data = {
#         "challenge": challenge
#         }

#     requests.post(json=data,
#       headers={'Content-Type':'application/json; charset=UTF-8'})



def show_add_retronote_modal(channel_id, trigger_id, initial_description=""):

    initial_view = view_templates.get_retronote_add_initial_view(channel_id, initial_description)
    data = {
        "trigger_id": trigger_id,
        "view": initial_view
        }

    requests.post('https://slack.com/api/views.open', json=data,
      headers={'Content-Type':'application/json; charset=UTF-8',
              'Authorization': 'Bearer {}'.format(bot_access_token)})


def process_view_submission(payload):
    state_values = payload["view"]["state"]["values"]
    note_type_code = state_values["note_type_block"]["note_type"]["selected_option"]["value"]
    note_text = state_values["note_description_block"]["note_description"]["value"]
    private_metadata = payload["view"]["private_metadata"]
    channel_id = private_metadata.split(":")[1]
    retro_file_name = get_retrofile_name(channel_id)

    note_type_text = ""
    if note_type_code == "note_type_good":
    	note_type_text = "Хорошо"
    if note_type_code == "note_type_bad":
    	note_type_text = "Плохо / нужно улучшить"

    NOTE_DELIMITER = "***"

    retronote = "\n\n"
    retronote += NOTE_DELIMITER + "\n"
    retronote += "Тип: {}".format(note_type_text) + "\n"
    retronote += "Описание: {}".format(note_text) + "\n"
    retronote += "Добавлена: {}".format(datetime.today().strftime('%d %b, %Y')) + "\n"
    retronote += NOTE_DELIMITER

    with open(retro_file_name, "a") as retrofile:
        retrofile.write(retronote)

    data = {
        "channel": channel_id,
        "text": "Добавлена заметка для ретро :eyes:"
    }

    requests.post('https://slack.com/api/chat.postMessage', json=data,
      headers={'Content-Type':'application/json',
              'Authorization': 'Bearer {}'.format(bot_access_token)})

    return view_templates.get_retronote_add_confirm_view(retronote)


def show_retronotes(response_url, retro_file_name):
    if is_file_exists(retro_file_name):
        with open(retro_file_name, "r") as retrofile:
            retronotes = retrofile.read()
            sorted_retronotes = get_sorted_notes_string(retronotes)
        requests.post(response_url, json=view_templates.get_retronotes_list_view(sorted_retronotes))
    else:
        requests.post(response_url, json=view_templates.get_no_notes_view())


def show_help(response_url):
    help_message = '''Команда `/retronote` позволяет управлять заметками для ретро: \n
        - `/retronote help (h)` - посмотреть help по возможностям команды и формату использования\n
        - `/retronote add` - добавить заметку для ретро \n
        - `/retronote list` - просмотреть все созданные заметки для ретро \n
        - `/retronote download` - скачать текстовый файл со всеми созданными заметками \n
        - `/retronote clear` - удалить все заметки _(опция доступна только админам)_ '''

    requests.post(response_url, json=view_templates.get_simple_message_view(help_message, replace_original=False))


def get_retrofile_name(channel_id):
    return "ch_" + str(channel_id) + ".txt"


def is_file_exists(filename):
    try:
        f = open(filename, 'r')
        f.close()
    except FileNotFoundError:
        return False
    return True


def get_notes_string(note_list_title, notes_list):
    if not notes_list:
        return ""

    notes_string = ""
    notes_string += note_list_title
    notes_string += "\n\n"
    for note in notes_list:
        notes_string += "***" + "\n"
        notes_string += note.strip() + "\n"
        notes_string += "***" + "\n\n"
    notes_string += "\n"
    return notes_string


def get_sorted_notes_string(all_notes_string):
    notes = all_notes_string.split("***")

    good_notes = [note for note in notes if note.find("Тип: Хорошо") != -1]
    bad_notes = [note for note in notes if note.find("Тип: Плохо / нужно улучшить") != -1]

    good_notes_str = get_notes_string("ЧТО БЫЛО ХОРОШО", good_notes)
    bad_notes_str = get_notes_string("ЧТО БЫЛО ПЛОХО / НУЖНО УЛУЧШИТЬ", bad_notes)

    return good_notes_str + bad_notes_str

