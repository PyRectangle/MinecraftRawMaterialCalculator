import json


class LangDict(dict):
    def __setitem__(self, key, value):
        try:
            self[key]
        except KeyError:
            super().__setitem__(key, value)
            return
        if not "block." in self[key]:
            super().__setitem__(key, value)


def getLang(filename):
    langJson = json.load(open(filename))
    langJsonInverted = LangDict()
    for x, y in langJson.items():
        langJsonInverted[y] = x
    return langJson, langJsonInverted
