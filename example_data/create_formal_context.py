import json

data = {}
attributes = []
obj = {}

with open("attributes.json") as f:
    attributes = json.load(f)

fc_attr = []
    
for att in attributes:
    fc_attr.append(att["label"]+":unknown")
    if "percentiles" in att:
        fc_attr.append(att["label"]+":low")
        fc_attr.append(att["label"]+":medium")
        fc_attr.append(att["label"]+":high")        
    elif "values" in att:
        for v in att["values"]:
            fc_attr.append(att["label"]+":"+v)


print(json.dumps(fc_attr, indent=2))
            
with open("country_data.json") as f:
    data = json.load(f)

for c in data:
    label = c["labels"]["en"]["value"]
    vector = []
    batts = []
    ucount = 0
    for att in attributes:
        if att["id"] in c["claims"]:
            cl = c["claims"][att["id"]]        
            if len(cl) > 0:
                a = "unknown"
                v = cl[0]
                dt = v["mainsnak"]["datatype"]
                if "datavalue" in v["mainsnak"]:
                    if not isinstance(v["mainsnak"]["datavalue"]["value"],dict):
                        a = v["mainsnak"]["datavalue"]["value"]
                    elif "amount" in v["mainsnak"]["datavalue"]["value"]:
                        a = v["mainsnak"]["datavalue"]["value"]["amount"]
                    elif "text" in v["mainsnak"]["datavalue"]["value"]:
                        a = v["mainsnak"]["datavalue"]["value"]["text"]
                    elif "id" in v["mainsnak"]["datavalue"]["value"]:
                        a = v["mainsnak"]["datavalue"]["value"]["id"]
                    else:
                        print(v["mainsnak"])
                if "percentiles" in att:
                    a = float(a)
                    if a < att["percentiles"][0]:
                        batts.append(att["label"]+":low")
                    elif a > att["percentiles"][1]:
                        batts.append(att["label"]+":high")
                    else:
                        batts.append(att["label"]+":medium")  
                else:
                    batts.append(att["label"]+":"+att["values"][att["id_values"].index(a)])
            else:                
                batts.append(att["label"]+":unknown")
                ucount = ucount + 1
        else:
            batts.append(att["label"]+":unknown")
            ucount = ucount + 1            
    print(label+":"+json.dumps(batts, indent=2))
    for a in fc_attr:
        vector.append(a in batts)
    if ucount <= len(attributes)*0.0:
        print("ucount OK "+str(ucount))
        obj[label] = vector        
    else:
        print("not including it "+str(ucount))

print(str(len(obj.keys()))+" objects saved with "+str(len(fc_attr))+" attributes")
        
with open("fc_attributes.json", "w") as f:
    json.dump(fc_attr, f)


with open("fc_objects.json", "w") as f:
    json.dump(obj, f)


