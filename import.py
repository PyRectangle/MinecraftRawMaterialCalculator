import zipfile
import shutil
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
for i in jarFile.namelist():
    if "minecraft/recipes" in i:
        prefix = os.path.dirname(i)
        jarFile.extract(i, "recipesExtract")
shutil.move(os.path.join("recipesExtract", prefix), "recipes")
shutil.rmtree("recipesExtract")
