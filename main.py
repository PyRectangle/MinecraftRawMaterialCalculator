import sys
import os
nameMain = __name__ == "__main__"
if nameMain:
    try:
        os.chdir(os.path.dirname(__file__))
    except FileNotFoundError:
        pass
    sys.path.append(".")
if os.path.exists(os.path.expanduser("~/.local/share/mrmc")):
    os.chdir(os.path.expanduser("~/.local/share/mrmc"))
needGui = len(sys.argv) == 1 or "-g" in sys.argv or "--gui" in sys.argv
from importDialog import main as importDialog
if needGui:
    import PySimpleGUI as sg
    if sys.platform == "win32":
        sg.set_global_icon("icon.ico")
    else:
        sg.set_global_icon("icon.png")


def checkImport():
    for i in "ids.json", "itemTextures.json", "lang", "recipes", "spritesheet.png", "tags", "textures":
        if not os.path.exists(i):
            return False
    return True


def minecraftGetter():
    if sys.platform == "win32":
        path = "%appdata%\.minecraft"
    elif sys.platform == "darwin":
        path = "~/Library/Application Support/minecraft"
    else:
        path = "~/.minecraft"
    path = os.path.expanduser(os.path.expandvars(path))
    if os.path.exists(path):
        return path
    else:
        wrong = True
        while wrong:
            wrong = False
            if needGui:
                path = sg.PopupGetFolder("Select your .minecraft folder.")
                if path == None:
                    exit(1)
            else:
                path = input("Select your .minecraft folder:")
            if os.path.exists(path):
                files = os.listdir(path)
                for i in "versions", "assets":
                    if not i in files:
                        wrong = True
            else:
                wrong = True
            if wrong:
                if needGui:
                    sg.Popup("This doesn't seem to be a .minecraft folder.")
                else:
                    print("This doesn't seem to be a .minecraft folder.")
        return path


if nameMain:
    try:
        if not checkImport() and needGui:
            sg.Popup("You need to import some assets before you can use this program.")
            importDialog(True, minecraftGetter())
        elif not checkImport():
            print("You need to import some assets before you can use this program.")
            importDialog(False, minecraftGetter())
    except PermissionError:
        if needGui:
            sg.Popup("You don't have permission to import assets.")
        else:
            print("You don't have permission to import assets")
        exit(1)
if needGui:
    from PIL import Image
    if nameMain:
        import config as configDialog
import lang
import json
import io


config = json.load(open("config.json"))
otherConfig = json.load(open(config["config"]))
for key in otherConfig:
    config[key] = otherConfig[key]
langJson, langJsonInverted = lang.getLang("lang/" + config["lang"] + ".json")
if needGui:
    sg.theme(config["theme"])
    idPos = json.load(open("itemTextures.json"))
    atlas = Image.open("spritesheet.png")
recipeDone = []
recipeDoneWith = {}
doneAt = {}
awnsered = {}
ways = {}
lastMultiplier = 1
craftingTypes = {"crafting_shaped": langJson["block.minecraft.crafting_table"], "crafting_shapeless": langJson["block.minecraft.crafting_table"], "smelting": langJson["container.furnace"], "blasting": langJson["container.blast_furnace"], "smoking": langJson["container.smoker"], "campfire_cooking": langJson["block.minecraft.campfire"], "stonecutting": langJson["container.stonecutter"], "smithing": langJson["block.minecraft.smithing_table"]}


def convertLitematicaList(text):
    text = text
    count = 0
    normalizedList = ""
    for line in text.split("\n"):
        if line == "" or list(line)[0] == "+":
            continue
        count += 1
        if count > 2:
            material = line.split(" | ")
            material[0] = material[0].replace("| ", "")
            materialName = ""
            materialNameList = list(material[0])
            materialNameList.reverse()
            spaceCount = 0
            for i in range(len(materialNameList)):
                if materialNameList[i] != " ":
                    break
                spaceCount += 1
            for i in range(spaceCount):
                del materialNameList[0]
            materialNameList.reverse()
            for i in materialNameList:
                materialName += i
            try:
                normalizedList += materialName + ":" + str(int(material[1])) + "\n"
            except ValueError:
                pass
    return normalizedList.replace("Item:Total\n", "")


def convertCSVList(text):
    text = text.replace(text[0:text.index("\n")] + "\n", "")
    normalList = ""
    for line in text.split("\n"):
        line = line.split(",")
        if len(line) > 1:
            normalList += line[0].replace("\"", "") + ":" + line[1] + "\n"
    return normalList


def convertListToDict(text):
    materialDict = {}
    for line in text.split("\n"):
        material = line.split(":")
        if len(material) != 2:
            continue
        materialName = langJsonInverted[material[0]].replace("block.", "").replace("item.", "").replace("container.", "").replace("minecraft.", "")
        if not materialName in config["Ignore"]:
            materialDict[materialName] = int(material[1])
    return materialDict


def convertDictToList(dictList):
    text = ""
    for material, count in dictList.items():
        if count > int(count):
            count = int(count + 1)
        else:
            count = int(count)
        try:
            wayCount = ways[material][1]
            if wayCount > int(wayCount):
                wayCount = int(wayCount + 1)
            else:
                wayCount = int(wayCount)
            way = " / " + blockIdToName(ways[material][0]) + ": " + str(wayCount)
        except KeyError:
            way = ""
        try:
            text += blockIdToName(material.replace("tag:", "")) + ": " + str(count) + way + "\n"
        except KeyError:
            materialNameList = list(material.replace("tag:", ""))
            del materialNameList[-1]
            materialName = ""
            for char in materialNameList:
                materialName += char
            try:
                text += blockIdToName(materialName) + ": " + str(count) + way + "\n"
            except KeyError:
                text += material + ": " + str(count) + way + "\n"
    return text


def getItemTexture(itemId, pil = False):
    try:
        item = Image.open("textures/" + itemId.replace("minecraft:", "") + ".png")
        item = item.resize((32, 32), Image.NEAREST)
    except FileNotFoundError:
        pos = idPos[itemId]
        y = int(pos / 32) * 32
        x = (pos % 32 - 1) * 32
        if x < 0:
            x += 32 * 32
            y -= 32
        item = atlas.crop((x, y, x + 32, y + 32))
    if pil:
        return item
    itemData = io.BytesIO()
    item.save(itemData, "PNG")
    return itemData.getvalue()


def blockIdToName(blockId):
    if blockId == "empty":
        return None
    try:
        blockName = langJson["block." + blockId.replace(":", ".")]
    except KeyError:
        try:
            blockName = langJson["item." + blockId.replace(":", ".")]
        except KeyError:
            try:
                blockName = langJson["container." + blockId.replace(":", ".")]
            except KeyError:
                return blockId
    return blockName


def howToCraftDialog(possebilities, blockId):
    try:
        return awnsered[str(possebilities)]
    except KeyError:
        pass
    text = "What do you use to make " + blockIdToName(blockId) + "?"
    if cmd:
        number = cmdDialog([blockIdToName(block) for block in possebilities], text)
        awnsered[str(possebilities)] = possebilities[number]
        return possebilities[number]
    layout = [[sg.Text(text)]]
    first = True
    for i in possebilities:
        layout.append([sg.Image(data = getItemTexture(i)), sg.Radio(blockIdToName(tagToName(i)), "craft", first, key = i)])
        first = False
    layout.append([sg.Button("Ok", bind_return_key = True), sg.Button("Cancel")])
    if "test" in sys.argv:
        return possebilities[0]
    else:
        window = sg.Window(text, layout)
        event, values = window.read()
        window.close()
        if event == "Cancel" or event == sg.WIN_CLOSED:
            return "Cancel"
        if event == "Ok":
            for i in values:
                if values[i]:
                    awnsered[str(possebilities)] = i
                    return i


def recipeToDict(blockId):
    realId = blockId.split("_from_")[0]
    materials = {}
    path = "recipes/" + blockId + ".json"
    recipeJson = json.load(open(path))
    try:
        count = recipeJson["result"]["count"]
    except (KeyError, TypeError):
        try:
            count = recipeJson["count"]
        except KeyError:
            count = 1
    try:
        materials["result"] = recipeJson["result"]["item"]
    except (KeyError, TypeError):
        try:
            materials["result"] = "tag:" + recipeJson["result"]["tag"]
        except (KeyError, TypeError):
            try:
                materials["result"] = recipeJson["result"]
            except KeyError:
                print("This recipe is hardcoded in the game and can therefore not be shown here.")
                exit(1)
    materials["count"] = count
    if recipeJson["type"] == "minecraft:crafting_shaped":
        materials["shape"] = recipeJson["pattern"]
        materials["keys"] = {}
        recipeString = ""
        for line in recipeJson["pattern"]:
            recipeString += line
        for key in recipeJson["key"]:
            if type(recipeJson["key"][key]) == list:
                possebilities = []
                for i in recipeJson["key"][key]:
                    try:
                        possebilities.append(i["item"])
                    except KeyError:
                        possebilities.append("tag:" + i["tag"])
                solution = howToCraftDialog(possebilities, "minecraft:" + realId)
                if solution == "Cancel":
                    return "Cancel"
                materials[solution] = recipeString.count(key) / count
            else:
                try:
                    solution = recipeJson["key"][key]["item"]
                except KeyError:
                    solution = "tag:" + recipeJson["key"][key]["tag"]
                materials[solution] = recipeString.count(key) / count 
            materials["keys"][key] = solution
    if recipeJson["type"] == "minecraft:crafting_shapeless":
        for i in recipeJson["ingredients"]:
            if type(i) == list:
                possebilities = []
                for p in i:
                    try:
                        itemCount = p["count"]
                    except KeyError:
                        itemCount = 1
                    try:
                        possebilities.append(p["item"])
                    except KeyError:
                        possebilities.append("tag:" + p["tag"])
                solution = howToCraftDialog(possebilities, "minecraft:" + realId)
                if solution == "Cancel":
                    return "Cancel"
                materials[solution] = itemCount / count
            else:
                try:
                    itemCount = i["count"]
                except KeyError:
                    itemCount = 1
                try:
                    try:
                        materials[i["item"]] += itemCount / count
                    except KeyError:
                        materials["tag:" + i["tag"]] += itemCount / count
                except KeyError:
                    try:
                        materials[i["item"]] = itemCount / count
                    except KeyError:
                        materials["tag:" + i["tag"]] = itemCount / count
    if recipeJson["type"] == "minecraft:smelting":
        try:
            materials[recipeJson["ingredient"]["item"]] = 1
        except (KeyError, TypeError):
            try:
                materials["tag:" + recipeJson["ingredient"]["tag"]] = 1
            except (KeyError, TypeError):
                if type(recipeJson["ingredient"]) == list:
                    possebilities = []
                    for i in recipeJson["ingredient"]:
                        try:
                            possebilities.append(i["item"])
                        except KeyError:
                            possebilities.append("tag:" + i["tag"])
                    solution = howToCraftDialog(possebilities, "minecraft:" + realId)
                    if solution == "Cancel":
                        return "Cancel"
                    materials[solution] = 1
    if recipeJson["type"] == "minecraft:stonecutting":
        materials[recipeJson["ingredient"]["item"]] = 1 / recipeJson["count"]
    if recipeJson["type"] == "minecraft:blasting" or recipeJson["type"] == "minecraft:smoking" or recipeJson["type"] == "minecraft:campfire_cooking":
        if type(recipeJson["ingredient"]) == list:
            possebilities = []
            for i in recipeJson["ingredient"]:
                possebilities.append(i["item"])
            solution = howToCraftDialog(possebilities, "minecraft:" + realId)
            if solution == "Cancel":
                    return "Cancel"
            materials[solution] = 1
        else:
            try:
                materials[recipeJson["ingredient"]["item"]] = 1
            except KeyError:
                materials["tag:" + recipeJson["ingredient"]["tag"]] = 1
    if recipeJson["type"] == "minecraft:smithing":
        materials[recipeJson["base"]["item"]] = 1
        materials[recipeJson["addition"]["item"]] = 1
    materials["type"] = recipeJson["type"]
    return materials


def tagToName(tag):
    tag = tag.replace("#", "").replace("tag:", "")
    name = blockIdToName(tag.replace("#", ""))
    if "minecraft:" in name:
        name = blockIdToName(tag.replace("#", "")[0:-1])
    if "minecraft:" in name:
        name = tag.replace("minecraft:", "")
    return name


def tagDialog(tag, possebilities):
    text = "What " + tagToName(tag) + " do you use?"
    if cmd:
        for i in range(len(possebilities)):
            possebilities[i] = tagToName(possebilities[i])
        return cmdDialog(possebilities, text)
    layout = [[sg.Text(text)]]
    first = True
    count = 0
    for i in possebilities:
        tagId = i.replace("#", "").replace("tag:", "")
        try:
            texture = getItemTexture(tagId)
        except KeyError:
            try:
                texture = getItemTexture(tagId[0:-1])
            except KeyError:
                texture = None
        layout.append([sg.Image(data = texture), sg.Radio(tagToName(i), "tag", first, key = str(count))])
        first = False
        count += 1
    layout.append([sg.Button("Ok", bind_return_key = True), sg.Button("Cancel")])
    if "test" in sys.argv:
        return 0
    else:
        window = sg.Window(text, layout)
        event, values = window.read()
        window.close()
        if event == "Cancel" or event == sg.WIN_CLOSED:
            return "Cancel"
        if event == "Ok":
            for i in values:
                if values[i]:
                    return int(i)


def getTagBlockId(tag):
    if "tag:" in tag:
        try:
            possebilities = json.load(open("tags/" + tag.replace("tag:minecraft:", "") + ".json"))["values"]
            try:
                returnTag = awnsered[str(possebilities)]
                if "tag:" in returnTag or "#minecraft" in returnTag:
                    return getTagBlockId(returnTag)
                else:
                    return returnTag
            except KeyError:
                pass
            if len(possebilities) == 1:
                if possebilities[0][0] == "#":
                    returnTag = getTagBlockId(possebilities[0].replace("#", "tag:"))
                    awnsered[str(possebilities)] = returnTag
                    return returnTag
                awnsered[str(possebilities)] = possebilities[0]
                return possebilities[0]
            number = tagDialog(tag, possebilities.copy())
            if number == "Cancel":
                return "Cancel"
            if possebilities[number][0] == "#":
                returnTag = getTagBlockId(possebilities[number].replace("#", "tag:"))
                awnsered[str(possebilities)] = returnTag
                return returnTag
            awnsered[str(possebilities)] = possebilities[number]
            return possebilities[number]
        except FileNotFoundError:
            return tag
    else:
        return tag


def convertToRaw(item, multiplier = 1):
    global lastMultiplier
    if "tag:" in item:
        tagitem = getTagBlockId(item)
        if tagitem == "Cancel":
            return "Cancel"
        if tagitem == None:
            return {item: multiplier}
        else:
            item = tagitem
    if item.replace("minecraft:", "") in config["StopAt"]:
        return {item: multiplier}
    if item in doneAt:
        try:
            ways[item][1] += doneAt[item][1] / doneAt[item][0] * multiplier
        except KeyError:
            pass
        try:
            returnRecipe = {}
            for material in recipeDoneWith[item]:
                returnRecipe[material] = recipeDoneWith[item][material] * multiplier
            return returnRecipe
        except KeyError:
            return {item: multiplier}
        return {item: multiplier}
    if item in recipeDone:
        try:
            ways[item][1] += lastMultiplier
        except KeyError:
            ways[item] = [recipeDone[-1], lastMultiplier]
        doneAt[item] = [multiplier, lastMultiplier]
        try:
            returnRecipe = {}
            for material in recipeDoneWith[item]:
                returnRecipe[material] = recipeDoneWith[item][material] * multiplier
            return returnRecipe
        except KeyError:
            return {item: multiplier}
    lastMultiplier = multiplier
    recipeDone.append(item)
    possebilities = []
    for i in os.listdir("recipes"):
        if i.split("_from_")[0] == item.replace("minecraft:", "") or i.replace(".json", "") == item.replace("minecraft:", ""):
            possebilities.append(i.replace(".json", ""))
    if len(possebilities) == 0:
        return {item: multiplier}
    elif len(possebilities) > 1:
        try:
            recipe = awnsered[str(possebilities)]
        except KeyError:
            count = 0
            recipe = recipeChooseDialog(possebilities, "How do you make " + blockIdToName(item) + "?")
            if recipe == "Cancel":
                return "Cancel"
            awnsered[str(possebilities)] = recipe
    else:
        recipe = possebilities[0]
    try:
        recipeDict = recipeToDict(recipe)
        if recipeDict == "Cancel":
            return "Cancel"
        realRecipeDict = {}
        for material in recipeDict:
            if "minecraft:" in material:
                realRecipeDict[material] = multiplier * recipeDict[material]
        recipeDoneWith[item] = convertListToRaw(realRecipeDict, "" , False)
        if recipeDoneWith[item] == "Cancel":
            return "Cancel"
        returnRecipe = recipeDoneWith[item].copy()
        for material in recipeDoneWith[item]:
            recipeDoneWith[item][material] /= multiplier
        return returnRecipe
    except FileNotFoundError:
        return {item: multiplier}


def correctWays(raw):
    global ways
    delete = []
    for item in ways:
        if ways[item][0] in raw:
            delete.append(item)
    for item in delete:
        del ways[item]


def convertListToRaw(materialList, prefix = "minecraft:", clear = True):
    rawList = {}
    for material, count in materialList.items():
        if clear:
            recipeDone.clear()
        if "minecraft:" in material:
            raw = convertToRaw(material, count)
        else:
            raw = convertToRaw(prefix + material, count)
        if raw == "Cancel":
            return "Cancel"
        rawList = mergeDicts(rawList, raw)
    correctWays(rawList)
    return rawList


def mergeDicts(d0, d1):
    for i in d1:
        try:
            d0[i] += d1[i]
        except KeyError:
            d0[i] = d1[i]
    return d0


if "test" in sys.argv:
    def input(text):
        print(text + "0")
        return "0"


def getRecipeLayout(recipe):
    recipe = recipeToDict(recipe)
    if recipe == "Cancel":
        return "Cancel"
    recipeLayout = []
    if recipe["type"] == "minecraft:crafting_shaped":
        for i in recipe["shape"]:
            recipeLayout.append(list(i))
        for row in range(len(recipeLayout)):
            for i in range(len(recipeLayout[row])):
                if recipeLayout[row][i] == " ":
                    blockId = "empty"
                else:
                    blockId = getTagBlockId(recipe["keys"][recipeLayout[row][i]])
                    if blockId == "Cancel":
                        return "Cancel"
                recipeLayout[row][i] = blockId
    else:
        row = []
        appended = False
        for i in recipe:
            if "minecraft:" in i:
                for number in range(int(recipe[i] * recipe["count"])):
                    row.append(i)
                    if len(row) == 3:
                        recipeLayout.append(row.copy())
                        row = []
                        appended = True
        if not appended:
            while len(row) < 3 and recipe["type"] == "minecraft:crafting_shaped":
                row.append("empty")
            recipeLayout.append(row)
    for row in range(len(recipeLayout)):
        for i in range(len(recipeLayout[row])):
            blockId = getTagBlockId(recipeLayout[row][i])
            if blockId == "Cancel":
                return "Cancel"
            recipeLayout[row][i] = sg.Image(data = getItemTexture(blockId), tooltip = blockIdToName(blockId)) 
    middle = int(len(recipeLayout) / 2) 
    recipeLayout[middle].append(sg.Text("--> " + str(recipe["count"]) + "x"))
    tagBlockId = getTagBlockId(recipe["result"])
    if tagBlockId == "Cancel":
        return "Cancel"
    recipeLayout[middle].append(sg.Image(data = getItemTexture(tagBlockId), tooltip = blockIdToName(tagBlockId)))
    return recipeLayout


def cmdDialog(possebilities, text):
    print(text)
    count = 0
    for i in possebilities:
        print(count, i)
        count += 1
    while True:
        try:
            number = int(input("The number:"))
            if number >= len(possebilities):
                print("Number is too large.")
            elif number < 0:
                print("Number is too small.")
            else:
                return number
        except ValueError:
            print("Needs to be a number.")


def recipeChooseDialog(recipes, text):
    if cmd:
        possebilities = []
        for recipe in recipes:
            recipeDict = recipeToDict(recipe)
            if recipeDict == "Cancel":
                return "Cancel"
            recipeName = craftingTypes[recipeDict["type"].replace("minecraft:", "")] + ":"
            for material in recipeDict:
                if "minecraft:" in material:
                    try:
                        int(recipeDict[material])
                        materialCount = float(recipeDict[material]) * recipeDict["count"]
                        if materialCount > int(materialCount):
                            materialCount = int(materialCount) + 1
                        else:
                            materialCount = int(materialCount)
                        recipeName += " " + str(materialCount) + "x " + tagToName(blockIdToName(material))
                    except ValueError:
                        pass
            recipeName += " = " + str(recipeDict["count"]) + "x " + tagToName(blockIdToName(recipeDict["result"]))
            possebilities.append(recipeName)
        return recipes[cmdDialog(possebilities, text)]
    tabs = []
    count = 0
    names = []
    for i in recipes:
        tabName = craftingTypes[json.load(open("recipes/" + i + ".json"))["type"].replace("minecraft:", "")]
        while tabName in names:
            tabName = tabName + " "
        names.append(tabName)
        recipeLayout = getRecipeLayout(i)
        if recipeLayout == "Cancel":
            return "Cancel"
        tabs.append(sg.Tab(tabName, recipeLayout, key = "tab" + str(count)))
        count += 1
    layout = [[sg.Text(text)], [sg.TabGroup([tabs], key = "Tab")]]
    layout.append([sg.Button("Ok", bind_return_key = True), sg.Button("Cancel")])
    if "test" in sys.argv:
        recipe = recipes[0]
    else:
        window = sg.Window(text, layout)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == "Cancel":
                window.close()
                return "Cancel"
            if event == "Ok":
                recipe = recipes[int(values["Tab"].replace("tab", ""))]
                break
        window.close()
    return recipe


def showList(dictList):
    if dictList == "Cancel":
        if cmd:
            print("Operation aborted by user.")
        else:
            sg.Popup("Operation aborted by user.")
        return
    if cmd:
        print("\nMaterials:")
        print(convertDictToList(dictList))
    else:
        layout = []
        for material in dictList:
            count = dictList[material]
            if count == int(count):
                count = int(count)
            else:
                count = int(count + 1)
            try:
                wayCount = ways[material][1]
                if wayCount > int(wayCount):
                    wayCount = int(wayCount + 1)
                else:
                    wayCount = int(wayCount)
                way = str(wayCount) + "x " + blockIdToName(ways[material][0])
            except KeyError:
                way = ""
            if way == "":
                layout.append([sg.Image(data = getItemTexture(material)), sg.Text(str(count) + "x " + blockIdToName(material))])
            else:
                layout.append([sg.Image(data = getItemTexture(material)), sg.Text(str(count) + "x " + blockIdToName(material)), sg.Image(data = getItemTexture(ways[material][0])), sg.Text(way)])
        height = len(layout) * 40
        if height > 640:
            height = 640
        window = sg.Window("Material List", [[sg.Text("Material List:", size = (14, 3))], [sg.Column(layout, scrollable = True, size = (None, height))], [sg.FileSaveAs(enable_events = True, key = "SaveAs", file_types = [("TXT Files", "*.txt")])]])
        while True:
            event, values = window.read()
            if event == "SaveAs":
                if values["SaveAs"] != "":
                    listFile = open(values["SaveAs"], "w")
                    listFile.write(convertDictToList(dictList))
                    listFile.close()
            if event == sg.WIN_CLOSED:
                window.close()
                return


def convertPathToDict(path):
    try:
        content = open(path).read()
        try:
            dictList = convertListToDict(convertLitematicaList(content))
        except Exception:
            dictList = {}
        if dictList == {}:
            try:
                dictList = convertListToDict(convertCSVList(content))
            except Exception:
                pass
        if dictList == {}:
            dictList = convertListToDict(content)
        if dictList == {}:
            if cmd:
                print("Error:", "Could not extract any data from file.")
                exit(1)
            else:
                sg.Popup("Error:", "Could not extract any data from file.")
        else:
            newList = {}
            for i in dictList:
                newList["minecraft:" + i] = dictList[i]
            return newList
    except Exception as error:
        if cmd:
            print("Error:", error)
            exit(1)
        else:
            sg.Popup("Error:", error)


def showMainWindow():
    global recipeDone, recipeDoneWith, doneAt, awnsered, ways, lastMultiplier, config, langJson, langJsonInverted
    path = os.path.expanduser(os.path.expandvars(os.path.join(config["minecraft"], "config/litematica")))
    if not os.path.exists(path):
        path = None
    layout = [[sg.Input(), sg.FileBrowse(file_types = [("TXT Files", "*.txt"), ("CSV Files", "*.csv")], initial_folder = path)],
              [sg.Button("Calculate"), sg.Button("Show"), sg.Button("Config"), sg.Button("Import"), sg.Button("Close")]]
    window = sg.Window("MinecraftRawMaterialCalculator", layout)
    while True:
        event, values = window.read()
        if event == "Import":
            window.hide()
            if os.path.exists(config["minecraft"]):
                importDialog(True, config["minecraft"])
            else:
                importDialog(True, minecraftGetter())
            window.un_hide()
        if event == "Calculate":
            window.hide()
            selectedList = convertPathToDict(values[0])
            if selectedList != None:
                recipeDone = []
                recipeDoneWith = {}
                doneAt = {}
                awnsered = {}
                ways = {}
                lastMultiplier = 1
                rawList = convertListToRaw(selectedList, "")
                showList(rawList)
            window.un_hide()
        if event == "Show":
            window.hide()
            selectedList = convertPathToDict(values[0])
            if selectedList != None:
                showList(selectedList)
            window.un_hide()
        if event == "Config":
            window.hide()
            configDialog.start()
            config = json.load(open("config.json"))
            otherConfig = json.load(open(config["config"]))
            for key in otherConfig:
                config[key] = otherConfig[key]
            langJson, langJsonInverted = lang.getLang("lang/" + config["lang"] + ".json")
            sg.theme(config["theme"])
            window.un_hide()
        if event == "Close" or event == sg.WIN_CLOSED:
            break
    window.close()


if nameMain:
    if len(sys.argv) == 1:
        cmd = False
        showMainWindow()
    else:
        cmd = True
        commands = {"help": ["show this help"],
                    "calc": ["calculate the raw materials needed", lambda path: showList(convertListToRaw(convertPathToDict(path)))],
                    "show": ["show the specified material list", lambda path: showList(convertPathToDict(path))],
                    "import": ["import new assets", lambda: importDialog(False, minecraftGetter())]}
        options = {"-h --help": "show this help",
                   "-g --gui": "use the gui to display dialogs"}
        filetypes = ["litematica material lists (txt format)", "litematica material lists (csv format)"]
        path = ""
        for i in sys.argv[2:]:
            if "-" == i[0]:
                isOption = False
                for option in options:
                    if i in option.split(" "):
                        isOption = True
                        if option.split(" ")[0] == "-g":
                            cmd = False
                if not isOption:
                    print("Unrecognized option:", i)
                    exit(1)
            if os.path.exists(i):
                if path != "":
                    print("This program can only process one file at a time.")
                    exit(1)
                path = i
        if "help" in sys.argv or "-h" in sys.argv or "--help" in sys.argv:
            print("Usage:")
            print("main.py <command> <file> <options>")
            print("Commands:")
            longest = 0
            for command in commands:
                if len(command) > longest:
                    longest = len(command)
            for command in commands:
                length = longest - len(command)
                print("   ", command, " " * length, commands[command][0])
            print("Options:")
            lognest = 0
            for option in options:
                if len(option) > longest:
                    longest = len(option)
            for option in options:
                length = longest - len(option)
                print("   ", option, " " * length, options[option])
            print("Supported filetypes:")
            for filetype in filetypes:
                print("   ", filetype)
        elif sys.argv[1] in commands and sys.argv[1] != "help":
            if path == "" and sys.argv[1] != "import":
                print("You need to specify a path.")
                exit(1)
            if sys.argv[1] == "import":
                commands[sys.argv[1]][1]()
            else:
                commands[sys.argv[1]][1](path)
        else:
            print("Unrecognized command:", sys.argv[1])
            exit(1)
