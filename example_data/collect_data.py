import requests
import json


results = []
with open("wikidata_countries.csv") as fp:
   line = fp.readline()
   cnt = 1
   while line:
       if cnt != 1:
           uri = line.strip()
           frg = uri[uri.rfind('/')+1:]
           print(frg)
           url = 'https://www.wikidata.org/wiki/Special:EntityData/'+frg+'.json'
           r = requests.get(url)
           try:
               d = json.loads(r.text)
               if "entities" in d and frg in d["entities"]:
                   results.append(d["entities"][frg])
           except json.decoder.JSONDecodeError:
               print("nop "+r.text)           
       line = fp.readline()
       cnt += 1

with open("country_data.json", "w") as f:
    json.dump(results, f)


