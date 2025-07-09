import json

def get_color_map():
    with open("output/parsed_code.json", "r") as file:
        data = json.load(file)
        nodes = data["nodes"]
        nodes_type = set()
        for node in nodes:
            nodes_type.add(node["type"])

    colours = [
        "#1f75fe",
        "#ff6f61",
        "#bada55",
        "#7fffd4",
        "#8a2be2",
        "#e0115f",
        "#ffb6c1",
        "#228b22",
        "#00ced1",
        "#ffa07a",
        "#20b2aa",
        "#dc143c",
        "#9932cc",
        "#3cb371",
        "#ff8c00",
    ]
    i=0
    color_map={}
    for node in nodes_type:
        color_map[node]=colours[i]
        i+=1
    return color_map
