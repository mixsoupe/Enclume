import csv
import json

csv_path = "R:/enclume/bkl.csv"
json_path = "R:/enclume/Revasion_temp.json"

bkl = {"path": "R://", "task":["LAYOUT", "ANIM"], "sequences":{}}


last_seq = "sq010"
shots = []
with open(csv_path, newline='', encoding="utf8") as csvfile:
    reader = csv.reader(csvfile)
    next(reader, None)
    next(reader, None)
    
    for row in reader:
        seq = row[0]
        if seq != last_seq:            
            bkl["sequences"][last_seq] = shots
            shots = []

        shots.append(row[1])
        last_seq = seq
        




with open(json_path, "w") as outfile:
    json.dump(bkl, outfile)


