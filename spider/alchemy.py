import codecs
import json
import re


def purify(load_dict, crystal):
    for regex, replace in load_dict["purify"].items():
        crystal = re.sub(regex, replace, crystal)
    return crystal


def refine(load_dict, crystal):
    for regex in load_dict["refine"]:
        crystal = re.sub(regex, "", crystal)
    return crystal


def inferno(data, purify_choice=True, refine_choice=True):
    alchemy = codecs.open("./alchemyPack/Alchemy.json", "r", "utf-8-sig")
    load_dict = json.load(alchemy)
    crystal = str(data)
    if purify_choice:
        crystal = purify(load_dict, crystal)
    if refine_choice:
        crystal = refine(load_dict, crystal)
    return crystal

if __name__ == "__main__":
    info = codecs.open("./result/3.json", "r", "utf-8-sig").read()
    res = inferno(info)
    print(res)
