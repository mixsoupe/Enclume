import csv
import json

csv_path = "R:/enclume/shots.csv"
json_path = "R:/enclume/Revasion_temp.json"

bkl = {"path": "R://", "task":["layout", "anim"], "sequences":{}}


last_seq = "sq010"
shots = []
with open(csv_path, newline='', encoding="utf16") as csvfile:
    reader = csv.reader(csvfile)
    # next(reader, None)
    # next(reader, None)
    
    for row in reader:
        seq = row[1]
        if seq != last_seq:            
            bkl["sequences"][last_seq] = shots
            shots = []

        shots.append(row[0])
        last_seq = seq
        




with open(json_path, "w") as outfile:
    json.dump(bkl, outfile, indent=4)


