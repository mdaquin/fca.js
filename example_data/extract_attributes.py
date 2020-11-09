import json
import requests
import numpy

properties = {}

with open("country_data.json") as f:
    data = json.load(f)
    for c in data:
        for k in c["claims"].keys():
            if k not in properties:
                properties[k] = {"count": 0, "datatypes": [], "values": [], "all": []}
            properties[k]["count"] += 1
            if len(c["claims"][k]) > 0:
                v = c["claims"][k][0]
                dt = v["mainsnak"]["datatype"]
                if "datavalue" in v["mainsnak"]:
                    if not isinstance(v["mainsnak"]["datavalue"]["value"],dict):
                        a = v["mainsnak"]["datavalue"]["value"]
                        if a not in properties[k]["values"]:
                            properties[k]["values"].append(a) 
                    elif "amount" in v["mainsnak"]["datavalue"]["value"]:
                        a = v["mainsnak"]["datavalue"]["value"]["amount"]
                        if a not in properties[k]["values"]:
                            properties[k]["values"].append(a)
                        properties[k]["all"].append(float(a))
                    elif "text" in v["mainsnak"]["datavalue"]["value"]:
                        a = v["mainsnak"]["datavalue"]["value"]["text"]
                        if a not in properties[k]["values"]:
                            properties[k]["values"].append(a)
                    elif "id" in v["mainsnak"]["datavalue"]["value"]:
                        a = v["mainsnak"]["datavalue"]["value"]["id"]
                        if a not in properties[k]["values"]:
                            properties[k]["values"].append(a)
                    else:
                        print(v["mainsnak"])
                else:
                    print(v)                        
                if dt not in properties[k]["datatypes"]:
                    properties[k]["datatypes"].append(dt)

props = []
                    
for k in properties:
    if float(properties[k]["count"])/float(len(data)) > 0.90 and ("quantity" in properties[k]["datatypes"] or (len(properties[k]["values"]) < 6 and len(properties[k]["values"]) != 0)):
        url = 'https://www.wikidata.org/wiki/Special:EntityData/'+k+'.json'
        r = requests.get(url)
        sp = {"id": k}
        label = "nolabel"
        try:
            d = json.loads(r.text)
            if "entities" in d and k in d["entities"] and "labels" in d["entities"][k] and "en" in d["entities"][k]["labels"] and "value" in d["entities"][k]["labels"]["en"]:    
                label = d["entities"][k]["labels"]["en"]["value"]            
        except json.decoder.JSONDecodeError:
            print("nop "+r.text)
        sp["label"] = label
        if 'quantity' in properties[k]["datatypes"]:
            p = numpy.percentile(properties[k]["all"], [33.3, 66.67])
            sp["percentiles"] = p.tolist()
        else:
            sp["values"] = []
            sp["id_values"] = []
            # get labels of values
            for v in properties[k]["values"]:
                vl = v
                sp["id_values"].append(v)
                url = 'https://www.wikidata.org/wiki/Special:EntityData/'+v+'.json'
                r = requests.get(url)
                try:
                    d = json.loads(r.text)
                    if "entities" in d and v in d["entities"] and "labels" in d["entities"][v] and "en" in d["entities"][v]["labels"] and "value" in d["entities"][v]["labels"]["en"]:    
                        vl = d["entities"][v]["labels"]["en"]["value"]
                except json.decoder.JSONDecodeError:
                    print("nop "+r.text)
                sp["values"].append(vl)
        props.append(sp)        
        print(k+" ("+label+"):"+str(properties[k]["count"])+" "+str(float(properties[k]["count"])/float(len(data)))+" "+str(properties[k]["datatypes"])+" "+str(len(properties[k]["values"])))

print(props)
with open("attributes.json", "w") as f:
    json.dump(props, f)

