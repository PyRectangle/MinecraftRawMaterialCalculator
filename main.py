import json
import sys
import re
import os


config = json.load(open(sys.argv[1]))
langJson = json.load(open("lang/" + config["lang"] + ".json"))
langJsonInverted = {y: x for x, y in langJson.items()}
recipeDone = []
doneAt = {}
awnsered = {}
ways = {}
lastMultiplier = 1
craftingTypes = {"crafting_shaped": langJson["block.minecraft.crafting_table"], "crafting_shapeless": langJson["block.minecraft.crafting_table"], "smelting": langJson["container.furnace"], "blasting": langJson["container.blast_furnace"], "smoking": langJson["container.smoker"], "campfire_cooking": langJson["block.minecraft.campfire"], "stonecutting": langJson["container.stonecutter"]}


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


def blockIdToName(blockId):
    try:
        blockName = langJson["block." + blockId.replace(":", ".")]
    except KeyError:
        try:
            blockName = langJson["item." + blockId.replace(":", ".")]
        except KeyError:
            blockName = langJson["container." + blockId.replace(":", ".")]
    return blockName


def howToCraftDialog(possebilities, blockId):
    try:
        return awnsered[str(possebilities)]
    except KeyError:
        pass
    print("What do you use to make", blockIdToName(blockId) + "?")
    count = 0
    for possebility in possebilities:
        print(count, possebility)
        count += 1
    while True:
        try:
            solution = possebilities[int(input("The number:"))]
            awnsered[str(possebilities)] = solution
            return solution
        except ValueError:
            print("Needs to be a number!")


def recipeToDict(blockId, returnType = False):
    realId = blockId.split("_from_")[0]
    materials = {}
    path = "recipes/" + blockId + ".json"
    recipeJson = json.load(open(path))
    try:
        count = recipeJson["result"]["count"]
    except (KeyError, TypeError):
        count = 1
    if recipeJson["type"] == "minecraft:crafting_shaped":
        recipeString = ""
        for line in recipeJson["pattern"]:
            recipeString += line
        for key in recipeJson["key"]:
            if type(recipeJson["key"][key]) == list:
                possebilities = []
                for i in recipeJson["key"][key]:
                    try:
                        possebilities.append(blockIdToName(i["item"]))
                    except KeyError:
                        possebilities.append("tag:" + blockIdToName(i["tag"]))
                solution = langJsonInverted[howToCraftDialog(possebilities, "minecraft:" + realId)].replace("container.", "").replace("block.", "").replace("item.", "").replace("minecraft.", "minecraft:")
                materials[solution] = recipeString.count(key) / count
            else:
                try:
                    materials[recipeJson["key"][key]["item"]] = recipeString.count(key) / count 
                except KeyError:
                    materials["tag:" + recipeJson["key"][key]["tag"]] = recipeString.count(key) / count 
    if recipeJson["type"] == "minecraft:crafting_shapeless":
        for i in recipeJson["ingredients"]:
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
                            possebilities.append(blockIdToName(i["item"]))
                        except KeyError:
                            possebilities.append("tag:" + blockIdToName(i["tag"]))
                    solution = langJsonInverted[howToCraftDialog(possebilities, "minecraft:" + realId)].replace("container.", "").replace("block.", "").replace("item.", "").replace("minecraft.", "minecraft:")
                    materials[solution] = 1
    if recipeJson["type"] == "minecraft:stonecutting":
        materials[recipeJson["ingredient"]["item"]] = 1 / recipeJson["count"]
    if recipeJson["type"] == "minecraft:blasting" or recipeJson["type"] == "minecraft:smoking" or recipeJson["type"] == "minecraft:campfire_cooking":
        if type(recipeJson["ingredient"]) == list:
            possebilities = []
            for i in recipeJson["ingredient"]:
                possebilities.append(i["item"])
            solution = howToCraftDialog(possebilities, "minecraft:" + realId)
            materials[solution] = 1
        else:
            materials[recipeJson["ingredient"]["item"]] = 1
    if returnType:
        materials["type"] = recipeJson["type"]
    return materials


def convertToRaw(item, multiplier = 1):
    global lastMultiplier
    if "tag:" in item:
        tagitem = getTagBlockId(item)
        if tagitem == None:
            return {item: multiplier}
        else:
            item = tagitem
    if item.replace("minecraft:", "") in config["StopAt"]:
        return {item: multiplier}
    if item in doneAt:
        ways[item][1] += doneAt[item][1] / doneAt[item][0] * multiplier
        return {item: multiplier}
    if item in recipeDone:
        try:
            ways[item][1] += lastMultiplier
        except KeyError:
            ways[item] = [recipeDone[-1], lastMultiplier]
        doneAt[item] = [multiplier, lastMultiplier]
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
            for i in possebilities:       
                recipe = recipeToDict(i, True)
            print("How do you make", blockIdToName(item) + "?")
            for i in possebilities:
                recipe = recipeToDict(i, True)
                craftingType = recipe["type"].replace("minecraft:", "")
                del recipe["type"]
                print(count, craftingTypes[craftingType] + ": ", end = "")
                for material, materialCount in recipe.items():
                    if materialCount > int(materialCount):
                        materialCount = int(materialCount + 1)
                    else:
                        materialCount = int(materialCount)
                    print(blockIdToName(material) + ": " + str(materialCount), end = " ")
                print()
                count += 1
            while True:
                try:
                    recipe = possebilities[int(input("The Number:"))]
                    awnsered[str(possebilities)] = recipe
                    break
                except ValueError:
                    print("Needs to be a number!")
    else:
        recipe = possebilities[0]
    try:
        recipeDict = recipeToDict(recipe)
        for material in recipeDict:
            recipeDict[material] *= multiplier
        return convertListToRaw(recipeDict, "" , False)
    except FileNotFoundError:
        return {item: multiplier}


def mergeDicts(d0, d1):
    for i in d1:
        try:
            d0[i] += d1[i]
        except KeyError:
            d0[i] = d1[i]
    return d0


def getTagBlockId(tag):
    possebilities = []
    for i in os.listdir("recipes"):
        try:
            if json.load(open("recipes/" + i))["group"] == tag.replace("tag:minecraft:", ""):
                possebilities.append("minecraft:" + i.split("_from_")[0].replace(".json", ""))
        except KeyError:
            continue
    if len(possebilities) == 0:
        return None
    elif len(possebilities) == 1:
        return possebilities[0]
    try:
        return awnsered[str(possebilities)]
    except KeyError:
        print("What", tag.replace("tag:minecraft:", ""), "do you use?")
        count = 0
        for i in possebilities:
            print(count, blockIdToName(i))
            count += 1
        while True:
            try:
                solution = possebilities[int(input("The Number:"))]
                awnsered[str(possebilities)] = solution
                return solution
            except ValueError:
                print("Needs to be a number!")


def convertListToRaw(materialList, prefix = "minecraft:", clear = True):
    rawList = {}
    for material, count in materialList.items():
        if clear:
            recipeDone.clear()
        raw = convertToRaw(prefix + material, count)
        rawList = mergeDicts(rawList, raw)
    return rawList


normalList = convertLitematicaList(open(sys.argv[2]).read())
dictList = convertListToDict(normalList)
rawList = convertListToRaw(dictList)
print("\nMaterial list:")
print(convertDictToList(rawList))
