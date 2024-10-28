# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *
from aqt import gui_hooks
from anki.stdmodels import models
from anki import collection as col
from . import basic
import os


# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.

def add_models():
    models.append(('Viet (test)', basic.add_model))

def start() -> None:
    """
    Show a message box with the number of cards in the current collection.

    This function is called when the menu item created below is activated.
    """
    # get the number of cards in the current collection, which is stored in
    # the main window
    """
    model = mw.col.models.by_name("Cloze")
    new_note = mw.col.newNote(model)
    new_note["Back"] = "example description"
    new_note["Front"] = "example name"
    
    
    deckId = mw.col.decks.id_for_name("TST")
    mw.col.add_note(new_note, deckId)
    """
    
    new_model = mw.col.models.new("Sample")
    
    fld1 = {
            "name": "Text", #name of the field
            "ord": 0, #order
            "sticky": False,
            "rtl": False,
            "font": "Arial",
            "size": 20,
            "description": "",
            "plainText": False,
            "collapsed": False,
            "excludeFromSearch": False,
            "id": None,
            "tag": None,
            "preventDeletion": False,
        }
    
    fld2 = {
            "name": "Back Extra",
            "ord": 1,
            "sticky": False,
            "rtl": False,
            "font": "Arial",
            "size": 20,
            "description": "",
            "plainText": False,
            "collapsed": False,
            "excludeFromSearch": False,
            "id": None,
            "tag": None,
            "preventDeletion": False,
        }
    
    
    mw.col.models.add_field(new_model, fld1)
    mw.col.models.add_field(new_model, fld2)
    template = mw.col.models.new_template("Sample Template")
    template["qfmt"] = "{{Text}}"
    template["afmt"] = "{{Back Extra}}"
    print(template)
    mw.col.models.add_template(new_model, template)
    
    mw.col.models.add(new_model)
    
    #1 template required error
    print(template)
    print(new_model)
    
    
    
    
    """
    new_note["Text"] = 'foo'
    new_note["Back Extra"] = 'bar'
    did = mw.col.decks.id("TST")
    mw.col.addNote(new_note, did)
    """


# create a new menu item, "test"
action = QAction("test", mw)
# set it to call testFunction when it's clicked
qconnect(action.triggered, start)
# and add it to the tools menu
mw.form.menuTools.addAction(action)
