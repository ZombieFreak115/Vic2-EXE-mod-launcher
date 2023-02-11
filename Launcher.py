import time
from os import listdir
from os import path
import os
from os.path import isfile, join
import shutil
import subprocess
import PySimpleGUI as sg
import pyparsing as pp
from pathlib import Path
from elevate import elevate
import atexit

elevate()  # elevates to admin rights to be able to write to v2 exe


def write_bytes(offset, fixed_byte):
    with open("v2game.exe", 'r+b') as f:
        f.seek(int(offset, 16))
        f.write(fixed_byte)


def parse_mods_bytes(list_of_mod_names):
    byte_list = []
    for modname in list_of_mod_names:
        with open(mod_path + "\\" + modname, 'r') as mod:
            try:
                mod_data = grammar.parse_file(mod)  # make error msg if fail to parse
            except:
                parse_error = sg.popup_yes_no("Parse error in " + modname + "!, check syntax. It is recommended to get the problem fixed as the program may crash or your EXE will be corrupted.\nDo you want to continue?", title="Error!", keep_on_top=True, grab_anywhere=False, text_color="red")
                if parse_error == "Yes":
                    continue
                else:
                    exit()
            for item in mod_data:
                if item[0] in grammar_keys: # make sure to ignore grammar keys for parsing data
                    continue
                bytevalue = bytes(item[1], "raw_unicode_escape")
                item[1] = bytevalue.decode('unicode_escape').encode('raw_unicode_escape')
                byte_list.append(item)
    return byte_list


def parse_mods_desc(list_of_mod_names):
    desc_list = {}
    for modname in list_of_mod_names:
        with open(mod_path + "\\" + modname, 'r') as mod:
            try:
                mod_data = grammar.parse_file(mod)
            except:  # error if it fails to parse
                parse_error = sg.popup_yes_no("Parse error in " + modname + "!, check syntax. It is recommended to get the problem fixed as the program may crash or your EXE will be corrupted.\nDo you want to continue?", title="Error!", keep_on_top=True, grab_anywhere=False, text_color="red")
                if parse_error == "Yes":
                    continue
                else:
                    exit()
            for item in mod_data:
                if item[0] in grammar_keys: # make sure to ignore grammar keys for parsing data
                    desc_dict = {modname: item[1]}
                    desc_list.update(desc_dict)
    return desc_list


def process_exists(process_name): # checks if process exists, shamelessly stolen (;
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call).decode()
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())


def process_exists_loop(name, sleep, BoolParam):
    while True:
        time.sleep(sleep)
        if BoolParam:   # if we want it to return true if the process exists
            if process_exists(name):
                return process_exists(name)
        else:   # if we want it to return true if the process doesn't exist
            if not process_exists(name):
                return process_exists(name)




backup_path = Path("./v2game_vanilla.exe")

grammar_keys = ["desc"]

grammar = pp.ZeroOrMore(pp.Group(pp.CaselessLiteral("desc") - pp.Char("=").suppress() - pp.Char("\"").suppress() - pp.Word(pp.printables + " \r\n\t", exclude_chars="\"") - pp.Char("\"").suppress())) & pp.ZeroOrMore(pp.Group(pp.Word(pp.hexnums) - pp.Char("=").suppress() - pp.Char("{").suppress() -
                                pp.Combine(pp.Literal(r'\x') - pp.Word(pp.hexnums, exact=2))
                                - pp.Char("}").suppress()))
grammar.ignore(pp.python_style_comment)

mod_selected_list = []
mod_path = os.getcwd() + "\\exemods"
# bunch of error checking
if not path.isdir(mod_path):
    # check if mod dir exists
    input("Mod path not found! Create a folder called exemods in your Victoria 2 root dir! Press enter to quit...")
    exit()
if not path.isfile("v2game.exe"):
    # check if mod dir exists
    input("v2game.exe not found! Press enter to quit...")
    exit()
if not path.isfile("victoria2.exe"):
    # check if mod dir exists
    input("victoria2.exe not found! Press enter to quit...")
    exit()
mod_list = [f for f in listdir(mod_path) if isfile(join(mod_path, f))]

desc_kv = parse_mods_desc(mod_list)


options_column = [
    [sg.Text("Unloaded Mods:", enable_events=True, size=(30, 2)), sg.Text("Loaded Mods:", enable_events=True, size=(30, 2))],
    [sg.Listbox(values=mod_list, enable_events=True, size=(30, 6), select_mode='multiple', key="-MOD_NON_SELECTED-"), sg.Listbox(values=[], enable_events=True, size=(30, 6), select_mode='multiple', key="-MOD_SELECTED-")],  # non selected mods
    [sg.Button("Start Victoria 2", enable_events=True, size=(20, 6), pad=(15, 0), key="-LAUNCH-"), sg.Button("Quit", enable_events=True, size=(20, 6), pad=(90, 0), key="-QUIT-")],
    [sg.Text("description:", enable_events=True, size=(50, 6), key="-DESC-")]
]



layout_main = [
    [
        sg.Column(options_column, size=(500, 500)),

    ]
]

window_main = sg.Window("Vic2 EXE mod launcher", layout_main, modal=True, finalize=True)

if not backup_path.is_file():  # checks if copy is made already
    shutil.copyfile('v2game.exe', 'v2game_vanilla.exe') # creates backup of vanilla exe before modification
with open("v2game_vanilla.exe", 'rb') as f:
    vanilla_exe = f.read()


def cleanup_exe(): # run when the program is exited w/o crashing, and restores vanilla exe if vic2 isn't running already
    if not process_exists("v2game.exe"):
        with open("v2game.exe", 'wb') as f:  # returns the exe to its after program is exited/ends
            f.write(vanilla_exe)
        print("Unmodded Vic2 restored, exiting...")


atexit.register(cleanup_exe)


while True:
    event, values = window_main.read()
    if event in (None, "-QUIT-"):
        exit()
    elif event == "-MOD_NON_SELECTED-":  # updates selected mods when a mod is clicked and removes them from the unselected box
        if len(values["-MOD_NON_SELECTED-"]) == 0:
            continue
        selected_mod = values["-MOD_NON_SELECTED-"][0]
        if desc_kv.get(selected_mod) is None:
            window_main["-DESC-"].update(selected_mod + " description: ")
        else:
            window_main["-DESC-"].update(selected_mod + " description: " + desc_kv.get(selected_mod))
        if selected_mod in mod_selected_list:
            continue
        mod_selected_list.append(selected_mod)
        mod_list.remove(selected_mod)
        window_main["-MOD_SELECTED-"].update(mod_selected_list)
        window_main["-MOD_NON_SELECTED-"].update(mod_list)
    elif event == "-MOD_SELECTED-":  # and vice versa
        if len(values["-MOD_SELECTED-"]) == 0:
            continue
        selected_mod = values["-MOD_SELECTED-"][0]
        if desc_kv.get(selected_mod) is None:
            window_main["-DESC-"].update(selected_mod + " description: ")
        else:
            window_main["-DESC-"].update(selected_mod + " description: " + desc_kv.get(selected_mod))
        if selected_mod in mod_list or len(selected_mod) == 0:
            continue
        mod_list.append(selected_mod)
        mod_selected_list.remove(selected_mod)
        window_main["-MOD_SELECTED-"].update(mod_selected_list)
        window_main["-MOD_NON_SELECTED-"].update(mod_list)
    elif event == "-LAUNCH-":  # starts parsing files and doing stuff
        offset_byte_list = parse_mods_bytes(mod_selected_list)
        offsets = []
        for iteration in offset_byte_list: # checking there are no conflicts in file offsets to be modified
            offsets.append(iteration[0])
        for i in offsets:
            if offsets.count(i) > 1: # spawns popup and asks the user if they want to proceed despite errors
                error_prompt = sg.popup_yes_no('File offset conflict detected at offset ' + i + "!,mods may not work properly.\nAre you sure you want to proceed?", title="Error!", keep_on_top=True, grab_anywhere=False, text_color="red")
                if error_prompt == "Yes":
                    continue
                else:
                    exit()
        if not process_exists("v2game.exe"):
            for iteration in offset_byte_list:
                write_bytes(iteration[0], iteration[1]) # writes it into exe
        else:  # checks if Vic2 is already running, if it is give the user a choice of proceeding with the same mods as the 1st instance
            error_prompt = sg.popup_yes_no("Vic2 is already running, if ran it will launch another instance of Vic2 with the same exe mods as the 1st instance, continue?", title="Error!", keep_on_top=True, grab_anywhere=False)
            if error_prompt == "Yes":
                pass
            else:
                exit()
        os.startfile(".\\victoria2.exe")  # starts Vic2 launcher
        window_main.close()  # closes the main window
        print("Waiting for Vic2 to launch...")
        if process_exists_loop("v2game.exe", 1, True): # check if process exists
            print("Vic2 process found! Waiting for it to close to restore unmodded EXE, do not close while Vic2 is running!")
            if not process_exists_loop("v2game.exe", 2, False): # check if process doesn't exist
                exit()



# TODO: make stuff into functions for easier readabillity?
# TODO: error messages
# TODO: sanitize input string literals (mod name etc)
