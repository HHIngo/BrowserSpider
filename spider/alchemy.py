import codecs
import json
import re
from pandas import DataFrame


def purify(load_dict, crystal):
    for regex, replace in load_dict["purify"].items():
        crystal = re.sub(regex, replace, crystal)
    return crystal


def refine(load_dict, crystal):
    for regex in load_dict["refine"]:
        crystal = re.sub(regex, "", crystal)
    return crystal


# 考虑外部调用，可能需要定制处理
def reconstruct(load_dict, data):
    crystal = {}
    temp_keys = []
    for key, value in load_dict["reconstruct"].items():
        if len(data[key]) == len(data[value]) and data[key] != "":
            temp_keys.append(key)
            temp_keys.append(value)
            crystal[value + ":" + key] = DataFrame(data[key], data[value]).to_dict("dict")
    for key in data.keys():
        if key not in temp_keys:
            crystal[key] = data[key]
    return crystal


def inferno(data, purify_choice=True, refine_choice=True, reconstruct_choice=False, file_name="Alchemy"):
    alchemy = codecs.open("./alchemyPack/" + file_name + ".json", "r", "utf-8-sig")
    load_dict = json.load(alchemy)
    if reconstruct_choice:
        crystal = reconstruct(load_dict, data)
    crystal = str(crystal)
    if purify_choice:
        crystal = purify(load_dict, crystal)
    if refine_choice:
        crystal = refine(load_dict, crystal)
    return crystal

if __name__ == "__main__":
    info = codecs.open("./result/4.json", "r", "utf-8-sig").read()
    res = inferno(info, True, True, False)
    print(res)