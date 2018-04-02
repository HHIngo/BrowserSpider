import codecs
import json
import re


class Alchemy(object):

    def __init__(self):
        self.load_dict = {}
        self.crystal = ""

    def purify(self):
        for regex, replace in self.load_dict["purify"].items():
            self.crystal = re.sub(regex, replace, self.crystal, re.S)

    def refine(self):
        for regex in self.load_dict["refine"]:
            self.crystal = re.sub(regex, "", self.crystal, re.S)

    def inferno(self, data, purify_choice=True, refine_choice=True):
        alchemy = codecs.open("./alchemyPack/Alchemy.json", "r", "utf-8-sig")
        self.load_dict = json.load(alchemy)
        self.crystal = str(data)
        if purify_choice:
            self.purify()
        if refine_choice:
            self.refine()
        return self.crystal

if __name__ == "__main__":
    a = Alchemy()
    info = ""
    res = a.inferno(info)
    print(res)