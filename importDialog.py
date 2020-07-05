from urllib.request import urlopen
import zipfile
import shutil
import lang
import time
import json
import os
import sys
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


def main(gui, minecraftFolder):
    versions = os.listdir(os.path.join(minecraftFolder, "versions"))
    versions.sort()
    while True:
        wrong = False
        version = None
        if gui:
            import PySimpleGUI as sg
            columnLayout = []
            for i in versions:
                columnLayout.append([sg.Radio(i, "versions")])
            layout = [[sg.Text("What version do you use?", size = (24, 3))],
                      [sg.Column(columnLayout, size = (None, 480), scrollable = True, vertical_scroll_only = True)],
                      [sg.Button("Ok"), sg.Button("Cancel")]]
            window = sg.Window("What version do you use?", layout)
            event, values = window.read()
            if event == "Cancel" or event == sg.WIN_CLOSED:
                exit()
            if event == "Ok":
                for number in values:
                    if values[number]:
                        version = versions[number]
            window.close()
        else:
            print("What version do you use?")
            count = 0
            for i in versions:
                print(count, i.replace(".json", ""))
                count += 1
            while True:
                try:
                    number = int(input("The number:"))
                    break
                except ValueError:
                    pass
            version = versions[number]
        if version != None:
            try:
                indexFile = json.load(open(os.path.join(minecraftFolder, "versions", version, version + ".json")))["assetIndex"]["id"] + ".json"
            except KeyError:
                wrong = True
            try:
                versionSplit = version.split(".")
                number = 0
                div = 1
                for i in versionSplit:
                    number += int(i) / div
                    div *= 10
                if not number >= 2.4:
                    wrong = True
            except ValueError:
                wrong = True
        else:
            wrong = True
        if wrong:
            if gui:
                sg.Popup("Version is not compatible with this program.")
            else:
                print("Version is not compatible with this program")
                time.sleep(1)
        else:
            break
    indexes = json.load(open(os.path.join(minecraftFolder, "assets/indexes", indexFile)))
    try:
        os.makedirs("lang", exist_ok = True)
    except OSError:
        if sys.platform == "win32":
            if gui:
                sg.Popup("You need admin rights to do this.")
            else:
                print("You need admin rights to do this.")
            exit(1)
        if sys.platform == "linux":
            os.makedirs(os.path.expanduser("~/.local/share/mrmc/lang"), exist_ok = True)
            shutil.copy("icon.png", os.path.expanduser("~/.local/share/mrmc/icon.png"))
            os.chdir(os.path.expanduser("~/.local/share/mrmc"))
    for i in indexes["objects"]:
        if "minecraft/lang" in i:
            fileHash = indexes["objects"][i]["hash"]
            path = os.path.join(minecraftFolder, "assets/objects", fileHash[0:2], fileHash)
            shutil.copyfile(path, i.replace("minecraft/", ""))
    jarFile = zipfile.ZipFile(open(os.path.join(minecraftFolder, "versions", version, version + ".jar"), "rb"))
    prefix = None
    os.makedirs("recipesExtract", exist_ok = True)
    langFiles = []
    for i in jarFile.namelist():
        if "minecraft/recipes" in i:
            prefix = os.path.dirname(i)
            jarFile.extract(i, "recipesExtract")
        if "assets/minecraft/lang/" in i:
            langFiles.append(i)
            jarFile.extract(i, "lang")
    for langFile in langFiles:
        shutil.move("lang/" + langFile, "lang/" + os.path.basename(langFile))
    shutil.rmtree("lang/assets")
    if os.path.exists("recipes"):
        shutil.rmtree("recipes")
    shutil.move(os.path.join("recipesExtract", prefix), "recipes")
    shutil.rmtree("recipesExtract")
    ids = []
    langJson, langJsonInverted = lang.getLang("lang/en_us.json")
    spritesheet = open("spritesheet.png", "wb")
    spritesheet.write(urlopen("https://minecraft.gamepedia.com" + urlopen("https://minecraft.gamepedia.com/Template:InvSprite").read().decode().split("background-image:url(")[1].split(")")[0]).read())
    spritesheet.close()
    rawLua = urlopen("https://minecraft.gamepedia.com/Module:InvSprite").read().decode().replace("&quot;", "'").split("ids = {\n")[1].split("</pre>")[0].split("\n")
    del rawLua[-3:]
    itemTextures = {}
    for i in rawLua:
        if "['" in i:
            name = i.split("['")[1].split("']")[0]
        else:
            name = i.split("=")[0].replace("\t", "").replace(" ", "")
        try:
            itemId = langJsonInverted[name].replace("block.", "").replace("shield.", "").replace("item.", "").replace("entity.", "").replace(".", ":")
            if "container." in itemId:
                for test in langJson:
                    if langJson[test] == name:
                        if "block.minecraft." in test:
                            itemId = test.replace("block.minecraft.", "minecraft:")
                itemId = itemId.replace("container.", "")
            itemTextures[itemId] = int(i.split("pos = ")[1].split(",")[0])
        except KeyError:
            pass
    itemTextures["empty"] = 3643
    site = urlopen("https://minecraft.gamepedia.com/Block").read().decode()
    os.makedirs("textures", exist_ok = True)
    os.makedirs("tags", exist_ok = True)
    for i in langJson:
        if "block." == i[0:6]:
            if not i.replace("block.minecraft.", "minecraft:") in itemTextures:
                url = site.split(">" + langJson[i] + "<")[0].split("1.5x, ")[-1].split(" 2x")[0]
                path = "textures/" + i.replace("block.minecraft.", "") + ".png"
                if not os.path.exists(path) and url[0:4] == "http":
                    open(path, "wb").write(urlopen(url).read())
    json.dump(itemTextures, open("itemTextures.json", "w"), indent = 4)
    os.makedirs("itemExtract", exist_ok = True)
    os.makedirs("tagExtract", exist_ok = True)
    jarFile = zipfile.ZipFile(open(os.path.join(minecraftFolder, "versions", version, version + ".jar"), "rb"))
    for i in jarFile.namelist():
        if "assets/minecraft/textures/item" in i:
            name = i.replace("assets/minecraft/textures/item/", "").split("_")
            for index in range(len(name)):
                try:
                    int(name[index].replace(".png", ""))
                    name[index] = ""
                except ValueError:
                    pass
            realName = ""
            for part in name:
                if part != "":
                    realName += part + "_"
            realName = realName[0:-1].replace(".png", "")
            if not realName in ids:
                ids.append(realName)
            jarFile.extract(i, "itemExtract")
        if "data/minecraft/tags/" in i:
            jarFile.extract(i, "tagExtract")
        if "data/minecraft/loot_tables/blocks/" in i:
            name = i.replace("data/minecraft/loot_tables/blocks/", "").replace(".json", "")
            if not name in ids:
                ids.append(name)
        if "assets/minecraft/blockstates/" in i:
            name = i.replace("assets/minecraft/blockstates/", "").replace(".json", "")
            if not name in ids:
                ids.append(name)
        if "assets/minecraft/models/item" in i:
            name = i.replace("assets/minecraft/models/item/", "").split("_")
            for index in range(len(name)):
                try:
                    int(name[index].replace(".json", ""))
                    name[index] = ""
                except ValueError:
                    pass
            realName = ""
            for part in name:
                if part != "":
                    realName += part + "_"
            realName = realName[0:-1].replace(".json", "")
            if not realName in ids:
                ids.append(realName) 
    for tagType in "fluids", "entity_types", "blocks", "items":
        for filename in os.listdir("tagExtract/data/minecraft/tags/" + tagType):
            shutil.move("tagExtract/data/minecraft/tags/" + tagType + "/" + filename, "tags/" + filename)
    for filename in os.listdir("itemExtract/assets/minecraft/textures/item"):
        shutil.move("itemExtract/assets/minecraft/textures/item/" + filename, "textures/" + filename)
    shutil.rmtree("itemExtract")
    shutil.rmtree("tagExtract")
    realIds = []
    for i in ids:
        isWrong = "spawn_egg" == i or "_wall_" in i or "_armor_slot_" in i or "tipped_arrow" in i or "_air" in i or "wall_torch" in i or "crossbow_" in i or "ruby" in i or "_overlay" in i
        if not isWrong:
            realIds.append(i)
    json.dump(realIds, open("ids.json", "w"), indent = 4)
    try:
        config = json.load(open("config.json"))
    except FileNotFoundError:
        config = {"config": "./calculatorConfig.json", "theme": "LightGrey2"}
        if not os.path.exists(config["config"]):
            json.dump({"Ignore": [], "StopAt": ["honey_bottle"], "lang": "en_us"}, open(config["config"], "w"))
    config["minecraft"] = os.path.expanduser(minecraftFolder)
    json.dump(config, open("config.json", "w"), indent = 4)
