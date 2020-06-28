from urllib.request import urlopen
import zipfile
import shutil
import lang
import json
import sys
import os


print("What version do you use?")
count = 0
versions = os.listdir(os.path.join(sys.argv[1], "versions"))
versions.sort()
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
indexFile = json.load(open(os.path.join(sys.argv[1], "versions", version, version + ".json")))["assetIndex"]["id"] + ".json"
indexes = json.load(open(os.path.join(sys.argv[1], "assets/indexes", indexFile)))
os.makedirs("lang", exist_ok = True)
for i in indexes["objects"]:
    if "minecraft/lang" in i:
        fileHash = indexes["objects"][i]["hash"]
        path = os.path.join(sys.argv[1], "assets/objects", fileHash[0:2], fileHash)
        shutil.copyfile(path, i.replace("minecraft/", ""))
jarFile = zipfile.ZipFile(open(os.path.join(sys.argv[1], "versions", version, version + ".jar"), "rb"))
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
jarFile = zipfile.ZipFile(open(os.path.join(sys.argv[1], "versions", version, version + ".jar"), "rb"))
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
    config = {}
config["minecraft"] = os.path.expanduser(sys.argv[1])
json.dump(config, open("config.json", "w"), indent = 4)
