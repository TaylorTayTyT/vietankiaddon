# -*- coding: utf-8 -*-
from aqt import mw, gui_hooks
from aqt.operations import QueryOp
from aqt.qt import *
from aqt.utils import showInfo
import os
import sys
import asyncio

file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(file_dir)
# Add the path to the src directory to sys.path
sys.path.append(os.path.join(file_dir, 'libs'))

# Now import load_dotenv from the dotenv package
import dotenv
import aiohttp
dotenv.load_dotenv()
from translate import translate_text, tts

note_type_name = "Viet Anki AddOn"
user_head, _ = os.path.split(file_dir)
user_head, _ = os.path.split(user_head)

directories = [item for item in os.listdir(user_head) if os.path.isdir(os.path.join(user_head, item))]
USER_LIST = [user for user in directories if not user == "addons21"]
USER = None
if not len(USER_LIST) == 0:
    USER = USER_LIST[0]


def start() -> None:
    if(not USER):
        showInfo("No user found")
        return
    if mw.col.models.by_name(note_type_name):
        return
    new_model = mw.col.models.new(note_type_name)
    
    fields = ["Viet", "English", "Sentence", "Sound"]
    for i, field_name in enumerate(fields):
        field = mw.col.models.newField(field_name)
        field.ord = i
        field.font = "Arial"
        field.size = 20
        mw.col.models.addField(new_model, field)
    
    template = mw.col.models.newTemplate("Sample Template")
    template.qfmt = "<div>{{Viet}}</div>"
    template.afmt = "<div>{{Viet}}</div><div>{{English}}</div><div>{{Sentence}}</div><!-- {{Sound}}-->"
    
    mw.col.models.addTemplate(new_model, template)
    mw.col.models.add(new_model)

gui_hooks.profile_did_open.append(start)

def on_add_cards_init(addcard):
    label1 = QLabel("Hello")
    label2 = QLabel("World")
    
    addcard.form.verticalLayout_3.addWidget(label1)
    addcard.form.verticalLayout_3.addWidget(label2)
    
    def get_field_values():
        field_values = {}

        # Check if `editor` and `note` are available in `addcard`
        if hasattr(addcard, 'editor') and hasattr(addcard.editor, 'note'):
            note = addcard.editor.note

            # Loop through all fields in the note and get the text
            for field_name, field_text in zip(note.keys(), note.fields):
                field_values[field_name] = field_text

        # Show field values for testing purposes
        return field_values

    # Add a button to trigger the value retrieval (for testing purposes)
    retrieve_button = QPushButton("Get Field Values")
    retrieve_button.clicked.connect(get_field_values)
    addcard.form.verticalLayout_3.addWidget(retrieve_button)
        
    
    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.KeyRelease and event.key() == Qt.Key.Key_Tab:
            
            #go to media directory
            head, _ = os.path.split(file_dir)
            parent_dir, _ = os.path.split(head)
            viet = None
            if("Viet" in get_field_values()):
                viet = get_field_values()['Viet']
            if viet:
                loop = asyncio.get_event_loop()
                async def fill_fields(viet, addcard):
                    head, _ = os.path.split(file_dir)
                    parent_dir, _ = os.path.split(head)
                    media = os.path.join(parent_dir, USER, "collection.media")
                    viet = viet.strip()

                    note = addcard.editor.note
                    try:
                        english = await translate_text(viet)
                        english = english["data"]["translations"]
                        english = [translation["translatedText"] for translation in english]
                        note.fields[1] = '\n'.join(english)
                    except Exception as e:
                        print(e)
                        return False
                    
                    audio_file = f"{viet}.mp3"
                    audio_path = os.path.join(media, audio_file)
                    local_audio_path = os.path.join(file_dir, "audio", audio_file)
                    media_output_file = os.path.join(media, audio_file)

                    if(not os.path.exists(media_output_file)):
                        try:
                            if(not os.path.exists(local_audio_path)):
                                print("Going to Google TTS API")
                                await tts(viet)
                        except Exception as e:
                            print(e)
                            #showInfo("Something went wrong\nYou might have to change the .env file")
                            return False
                        try:
                            print(local_audio_path, media_output_file)
                            os.rename(local_audio_path, media_output_file)
                            if(os.path.exists(local_audio_path)):
                                print("removing")
                                os.remove(local_audio_path)
                            
                            note.fields[3] = f'[sound:{audio_file}]'
                        except FileExistsError:
                            print("File already exists")
                            note.fields[3] = f'[sound:{audio_file}]'
                        except Exception as e:
                            print("os.rename error")
                            print(e)
                    else:
                        note.fields[3] = f'[sound:{audio_file}]'
                    
                
                def success(addcard):
                    addcard.editor.loadNote()
                    print("success")
                    return True
                op = QueryOp(
                    parent=mw,
                    op=lambda mw: loop.run_until_complete(fill_fields(viet, addcard)),
                    success=lambda mw: success(addcard),
                )
                op.with_progress().run_in_background()
            return True  # Mark event as handled
        return False  # Pass event to other handlers
    
    addcard.form.centralwidget.installEventFilter(addcard)
    addcard.eventFilter = eventFilter.__get__(addcard)
gui_hooks.add_cards_did_init.append(on_add_cards_init)