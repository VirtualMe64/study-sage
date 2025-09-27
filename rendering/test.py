import json

data = json.load(open("result.json", "r", encoding="utf-8"))

for file in data['sceneFiles']:
    filename = file['filename']
    with open("generated/" + filename, "w", encoding="utf-8") as f:
        f.write(file['code'])

with open("generated/" + data['masterFile']['filename'], "w", encoding="utf-8") as f:
    f.write(data['masterFile']['content'])