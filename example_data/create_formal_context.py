import json

data = {}
attributes = []
obj = {}

with open("attributes.json") as f:
    attributes = json.load(f)

fc_attr = []
    
for att in attributes:
    # fc_attr.append(att["label"]+":unknown")
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
                    #if a <= att["percentiles"][1]:
                    #    batts.append(att["label"]+":low")
                    #else:
                    #    batts.append(att["label"]+":high")                        
                    if a < att["percentiles"][0]:
                        batts.append(att["label"]+":low")
                    elif a > att["percentiles"][2]:
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


with open("country.slf", "w") as f:
    f.write("[Lattice]\n")
    f.write(str(len(obj.keys())))
    # f.write("5")
    f.write("\n")
    f.write(str(len(fc_attr)))
    # f.write("5")    
    f.write("\n")    
    f.write("[Objects]\n")
    count = 0
    for o in obj:
         f.write(o.encode('utf-8'))
         f.write("\n")
         count = count +1
         #if count == 5:
         #    break
    print(count)
    f.write("[Attributes]\n")
    count = 0
    for a in fc_attr:
        f.write(a)
        f.write("\n")
        count = count + 1
        # if count == 5:
        #    break
    f.write("[relation]\n")          
    count1 = 0
    for o in obj:
        count2 = 0        
        for v in obj[o]:
            if v:
                f.write("1 ")
            else:
                f.write("0 ")
            count2 = count2 + 1
            # if count2 == 5:
            #    break
        f.write("\n")
        count1 = count1 + 1
        # if count1 == 5:
        #    break


with open("country.csv", "w") as f:
    for a in fc_attr:
        f.write(";"+a)
    f.write("\n")
    for o in obj:
        f.write(o.encode('utf-8'))
        for i in obj[o]:
            if obj[o][i]:
                f.write(";1")
            else:
                f.write(";0")
        f.write("\n")
        
with open("country.rcf", "w") as f:
    f.write("# countries\n\n")
    f.write("[Relational Context]\nDefault Name\n[Binary Relation]\nName of Dataset\n")
    first = True
    for o in obj:
        if not first:
            f.write(" | ")
        first = False
        f.write(o.encode('utf-8'))
    f.write("\n")
    first = True
    for a in fc_attr:
        if not first:
            f.write(" | ")
        first = False
        f.write(a)
    f.write("\n")
    for o in obj:
        first = True
        for v in obj[o]:
            if not first:
                f.write(" ")
            first = False
            if (v):
                f.write("1")
            else:
                f.write("0")
        f.write("\n")
    f.write("[END Relational Context]")
    
