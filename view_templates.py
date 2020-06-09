ADD_NOTE_BUTTON_NAME = "Add note"
ADD_NOTE_BUTTON_VALUE = "add_note"

VIEW_NOTES_BUTTON_NAME = "View notes"
VIEW_NOTES_BUTTON_VALUE = "view_notes"

DEFAULT_VIEW_RESPONSE_TYPE = "ephemeral"  ### another possible option is "in_channel", which means view will be shown to all users in channel
DEFAULT_VIEW_REPLACE_ORIGINAL = False


### Main view is shown when /retronote slack command is invoked
def get_main_view(response_type=DEFAULT_VIEW_RESPONSE_TYPE, replace_original=DEFAULT_VIEW_REPLACE_ORIGINAL):
    return {
        "response_type": response_type,
        "replace_original": replace_original,
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Позволяет создавать заметки для предстоящего ретро и просматривать их в любое время в текущем slack канале."
                },
                "accessory": {
                    "type": "overflow",
                    "action_id": "overflow_menu",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Help",
                                "emoji": True
                            },
                            "value": "help_menuitem_selected"
                        }
                    ]
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Используйте команды `/retronote add` и `/retronote list` или кнопки ниже для добавления заметки и для отображения всех созданных заметок."
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": ADD_NOTE_BUTTON_NAME
                        },
                        "style": "danger",
                        "value": ADD_NOTE_BUTTON_VALUE
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": VIEW_NOTES_BUTTON_NAME
                        },
                        "style": "primary",
                        "value": VIEW_NOTES_BUTTON_VALUE
                    }
                ]
            }
        ]
    }


### no_notes_view is shown when "/retronote list" command is invoked or
### "View notes" button is pressed and file with retronotes does not exist yet
### or is empty
def get_no_notes_view(response_type=DEFAULT_VIEW_RESPONSE_TYPE, replace_original=DEFAULT_VIEW_REPLACE_ORIGINAL):
    return {
        "response_type": response_type,
        "replace_original": replace_original,
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "У вас ещё нет заметок для ретро :scream:"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Создайте же их скорее с помощью кнопки *{}* ".format(ADD_NOTE_BUTTON_NAME)
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": ADD_NOTE_BUTTON_NAME
                    },
                    "value": ADD_NOTE_BUTTON_VALUE,
                    "style": "danger"
                }
            }
        ]
    }


### retronotes_list_view is shown when "/retronote list" command is invoked or
### "View notes" button is pressed and there is file with created retronotes
def get_retronotes_list_view(retronotes, response_type=DEFAULT_VIEW_RESPONSE_TYPE,
                             replace_original=DEFAULT_VIEW_REPLACE_ORIGINAL):
    return {
        "response_type": response_type,
        "replace_original": replace_original,
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Созданные заметки для ретро:* \n ```{}```".format(retronotes)
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "_Добавить заметку можно с помощью команды `/retronote add` или с помощью кнопки *{}* ниже_".format(
                        ADD_NOTE_BUTTON_NAME)
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": ADD_NOTE_BUTTON_NAME
                        },
                        "style": "primary",
                        "value": ADD_NOTE_BUTTON_VALUE
                    }
                ]
            }
        ]
    }


### retronote_add_initial_view is shown when "Add note" button is clicked
def get_retronote_add_initial_view(channel_id, initial_description=""):
    return {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "Заметка для ретро"
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit"
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "private_metadata": "channel_id:{}".format(channel_id),
        "blocks": [
            {
                "type": "input",
                "block_id": "note_type_block",
                "element": {
                    "type": "static_select",
                    "action_id": "note_type",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Выберите тип заметки"
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Хорошо :+1:",
                                "emoji": True
                            },
                            "value": "note_type_good"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Плохо / нужно улучшить :thinking_face:",
                                "emoji": True
                            },
                            "value": "note_type_bad"
                        }
                    ]
                },
                "label": {
                    "type": "plain_text",
                    "text": "Тип"
                }
            },
            {
                "type": "input",
                "block_id": "note_description_block",
                "optional": False,
                "element": {
                    "type": "plain_text_input",
                    "action_id": "note_description",
                    "multiline": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Добавьте подробное описание заметки"
                    },
                    "initial_value": initial_description,
                    "max_length": 1000
                },
                "label": {
                    "type": "plain_text",
                    "text": "Описание"
                }
            }
        ]
    }


### retronote_add_confirm_view is shown when retronote was successfully created
def get_retronote_add_confirm_view(retronote):
    return {
        "response_action": "update",
        "view": {
            "type": "modal",
            "title": {
                "type": "plain_text",
                "text": "Заметка добавлена"
            },
            "close": {
                "type": "plain_text",
                "text": "Close"
            },
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Текст заметки:* \n ```{}```".format(retronote)
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "_Для просмотра всех созданных заметок используйте команду `/retronote list`_"
                    }
                }
            ]
        }
    }


### get_simple_message should be used for short-text notifications
def get_simple_message_view(text, response_type=DEFAULT_VIEW_RESPONSE_TYPE,
                            replace_original=DEFAULT_VIEW_REPLACE_ORIGINAL):
    return {
        "response_type": response_type,
        "replace_original": replace_original,
        "text": text
    }
