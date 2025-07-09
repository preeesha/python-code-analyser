import json


def get_color_map(filename):
    with open(f"outputs/{filename}.json", "r") as file:
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
    i = 0
    color_map = {}
    for node in nodes_type:
        color_map[node] = colours[i]
        i += 1
    return color_map


{
    "source": {"id": "Main.Py", "type": "File"},
    "target": {"id": "Openai", "type": "Module"},
    "relationship_type": "IMPORTS",
    "properties": {"context": "Import statement", "line_number": "1"},
},


def data_for_prompt(filename):
    with open(f"outputs/{filename}.json", "r") as file:
        data = json.load(file)
        prompt_data = []
        src_nodes = set()
        tgt_nodes = set()
        rel = data["relationships"]
        for r in rel:
            temp = {}
            temp["source"] = r["source"]["id"]
            temp["target"] = r["target"]["id"]
            temp["relationship_type"] = r["relationship_type"]
            src_nodes.add(r["source"]["id"])
            tgt_nodes.add(r["target"]["id"])
            prompt_data.append(temp)
            
        nodes=data["nodes"]
        for n in nodes:
            if n["id"] not in src_nodes and n["id"] not in tgt_nodes:
                prompt_data.append(n["id"])
        return prompt_data
    


