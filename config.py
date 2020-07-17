from main import getItemTexture
from PIL import Image
import PySimpleGUI as sg
import pyautogui as ag
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import tkinter
import json
import sys


def mousePress(event):
    global mousePressed
    mousePressed = True


def mouseWheel(event):
    global globalScroll
    if event.num == 5 or event.delta == -120:
        globalScroll += 1
    if event.num == 4 or event.delta == 120:
        globalScroll -= 1


def selectBlock():
    global globalScroll, mousePressed
    ids = json.load(open("ids.json"))
    ids.sort()
    height = int(len(ids) / 20 * 32 + 1)
    column0 = [[sg.Graph((640, 480), (0, 0), (640, height), key = "pygame")],
               [sg.Text("Selected Block:", size = (80, 1))]]
    column1 = [[sg.Slider((100, 0), 0, disable_number_display = True, enable_events = True, key = "scroll", size = (25, 20))],
               [sg.Button("Ok")]]
    layout = [[sg.Text("Search:"), sg.Input(key = "Search", enable_events = True)],
              [sg.Column(column0), sg.Column(column1)]]
    window = sg.Window("Select a block", layout, finalize = True)
    window.TKroot.bind("<Button-5>", mouseWheel)
    window.TKroot.bind("<Button-4>", mouseWheel)
    if sys.platform != "win32":
        window.TKroot.bind("<Button-3>", mousePress)
        window.TKroot.bind("<Button-2>", mousePress)
        window.TKroot.bind("<Button-1>", mousePress)
    embed = window["pygame"].TKCanvas
    os.environ["SDL_WINDOWID"] = str(embed.winfo_id())
    if sys.platform == "win32":
        os.environ["SDL_VIDEODRIVER"] = "windib"
    screen = pygame.display.set_mode((640, 480))
    screen.fill((200, 200, 200))
    pygame.display.init()
    images = {}
    x, y = 0, 0
    realIds = []
    for block in ids:
        try:
            image = getItemTexture("minecraft:" + block, True)
            size = image.size
            data = image.tobytes()
            mode = image.mode
            if mode != "RGBA":
                newImage = Image.new("RGBA", size, (255, 255, 255, 255))
                newImage.paste(image)
                mode = "RGBA"
                data = newImage.tobytes()
            images[block] = pygame.image.frombuffer(data, size, mode)
            screen.blit(images[block], (x, y))
            x += 32
            if x > 640:
                x = 0
                y += 32
            realIds.append(block)
        except KeyError:
            pass
    pygame.display.update()
    search = ""
    offset = [0, 0]
    selectedBlock = 0
    scroll = 0
    realSelect = None
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 5:
                    globalScroll += 1
                elif event.button == 4:
                    globalScroll -= 1
                else:
                    mousePressed = True
            if event.type == pygame.MOUSEMOTION:
                pos = list(pygame.mouse.get_pos())
                if sys.platform == "win32":
                    mousePos = pos
                    mousePos[1] += scroll
                else:
                    mousePos = ag.position()
                    windowPos = list(window.current_location())
                    mousePos = [mousePos.x - windowPos[0], mousePos.y - windowPos[1]]
                    offset = [mousePos[0] - pos[0], mousePos[1] - pos[1]]
        event, values = window.read(10, "loop")
        if event == "Search":
            if search != values["Search"]:
                column0[1][0].update("Selected Block:")
                realSelect = None
                search = values["Search"]
                scroll = 0
                column1[0][0].update(value = 0)
        elif event == "scroll" or globalScroll != 0:
            values["scroll"] += globalScroll / (height - 480) * 5000
            if values["scroll"] > 100:
                values["scroll"] = 100
            if values["scroll"] < 0:
                values["scroll"] = 0
            scroll = int(values["scroll"] / 100 * (height - 480))
            if globalScroll != 0:
                globalScroll = 0
                column1[0][0].update(value = values["scroll"])
            if height <= 480:
                scroll = 0
                column1[0][0].update(value = 0)
        elif event == "loop":
            if sys.platform != "win32":
                mousePos = ag.position()
                windowPos = list(window.current_location())
                mousePos = [mousePos.x - windowPos[0] - offset[0], mousePos.y - windowPos[1] - offset[1] + scroll]
            blockX = int(mousePos[0] / 32)
            blockY = int(mousePos[1] / 32)
            selectedBlock = blockY * 21 + blockX
            mouseInPygame = mousePos[0] >= 0 and mousePos[1] - scroll >= 0 and mousePos[0] <= 640 and mousePos[1] - scroll <= 480
        elif event == "Ok":
            break
        elif event == sg.WIN_CLOSED:
            pygame.quit()
            window.close()
            return
        if mousePressed:
            mousePressed = False
            if mouseInPygame:
                try:
                    column0[1][0].update("Selected Block: " + realIds[selectedBlock])
                    realSelect = selectedBlock
                except (IndexError, TypeError):
                    pass
        screen.fill((200, 200, 200))
        x, y = 0, -scroll
        newRealIds = []
        for block in images:
            if search.upper() in block.upper():
                newRealIds.append(block)
                try:
                    try:
                        if block == realIds[realSelect]:
                            pygame.draw.polygon(screen, (255, 0, 0), [[x, y], [x + 31, y], [x + 31, y + 31], [x, y + 31]])
                    except (IndexError, TypeError):
                        pass
                    if block == realIds[selectedBlock] and mouseInPygame:
                        pygame.draw.polygon(screen, (0, 0, 255), [[x, y], [x + 31, y], [x + 31, y + 31], [x, y + 31]])
                except IndexError:
                    pass
                screen.blit(images[block], (x, y))
                x += 32
                if x > 640:
                    x = 0
                    y += 32
        realIds = newRealIds
        height = int(len(newRealIds) / 20 * 32 + 1)
        pygame.display.update()
    window.close()
    pygame.quit()
    if realSelect != None:
        return realIds[realSelect]


def createWindow(defval = None):
    sg.change_look_and_feel(defval)
    sg.theme(defval)
    layout = [[sg.Combo(sg.theme_list(), defval)],
              [sg.Text("Config Location:"), sg.Input(config["config"]), sg.FileSaveAs("Browse", file_types = [("JSON Files", "*.json")])],
              [sg.Text("Minecraft folder:"), sg.Input(config["minecraft"]), sg.FolderBrowse()]]
    diff = ""
    for i in realConfig:
        if type(realConfig[i]) == list:
            layout.append([sg.Text(i), sg.Listbox(realConfig[i].copy(), select_mode = sg.LISTBOX_SELECT_MODE_MULTIPLE, size = (50, 10), right_click_menu = [None, ["Add" + diff, "Remove" + diff]], key = i, tooltip = "Right click to Add/Remove")])
            configIndexes[i] = len(layout) * 2
            diff += " "
        if i == "lang":
            langs = os.listdir("lang")
            for index in range(len(langs)):
                langs[index] = langs[index].replace(".json", "")
            langs.sort()
            layout.append([sg.Text("Language:"), sg.Combo(langs, realConfig[i])])
    layout.append([sg.Button("Ok"), sg.Button("Save"), sg.Button("Cancel")])
    return sg.Window("Config", layout)


def save(values):
    global config, realConfig, window
    config["theme"] = values[0]
    config["config"] = values[1]
    config["minecraft"] = values[2]
    realConfig["Ignore"] = window.element_list()[configIndexes["Ignore"]].GetListValues()
    realConfig["StopAt"] = window.element_list()[configIndexes["StopAt"]].GetListValues()
    realConfig["lang"] = values[3]
    return config, realConfig


def saveToFile():
    sg.Popup("You might have to restart for some changes to take effect.")
    json.dump(config, open("config.json", "w"), indent = 4)
    json.dump(realConfig, open(config["config"], "w"), indent = 4)


window = None
mousePressed = False
globalScroll = 0
configIndexes = {}
config = json.load(open("config.json"))
realConfig = json.load(open(config["config"]))


def start():
    global window, mousePressed, globalScroll, configIndexes, config, realConfig
    mousePressed = False
    globalScroll = 0
    configIndexes = {}
    config = json.load(open("config.json"))
    realConfig = json.load(open(config["config"]))
    c, rc = config.copy(), realConfig.copy()
    window = createWindow(config["theme"])
    while True:
        event, values = window.read()
        if event == "Remove" or event == "Remove ":
            name = "Ignore"
            if event == "Remove ":
                name = "StopAt"
            listValues = window.element_list()[configIndexes[name]].GetListValues()
            for i in values[name]:
                listValues.remove(i)
            window.element_list()[configIndexes[name]].Update(listValues)
        if event == "Add" or event == "Add ":
            name = "Ignore"
            if event == "Add ":
                name = "StopAt"
            listValues = window.element_list()[configIndexes[name]].GetListValues()
            window.hide()
            block = selectBlock()
            if block != None:
                listValues.append(block)
            window.un_hide()
            window.element_list()[configIndexes[name]].Update(listValues)
        if event == "Save":
            save(values)
            saveToFile()
            c, rc = config.copy(), realConfig.copy()
            window.close()
            window = createWindow(values[0])
        if event == "Ok":
            save(values)
            saveToFile()
            c, rc = config.copy(), realConfig.copy()
            break
        if event == "Cancel":
            if save(values) != (c, rc):
                awnser = sg.PopupYesNo("Are you sure you don't want to save?")
                if awnser == "Yes":
                    break
            else:
                break
        if event == sg.WIN_CLOSED:
            break
    window.close()
