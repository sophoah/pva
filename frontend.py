import json
from flask import Flask, render_template
import requests
import pprint
from requests.exceptions import HTTPError

app = Flask(__name__)

# reading an URL url returning a JSON
def get_url(url):
    try:
        r = requests.get(url)
        out = r.json()
    except:
        return '{"error": "reading json RPC"}'
    return out

def get_result():
    return get_url("http://127.0.0.1:5000/pvausers/results")

def get_pva_users():
    return get_url("http://127.0.0.1:5000/pvausers")  

def get_oneaddress_from_pvalist(oid, pvalist):
    for pva in pvalist:
        if oid == pva['_id']['$oid']:
            return pva['validatoraddress']
    return 0 

def build_finalresult():
    results = get_result()
    pva_users = get_pva_users()

    final_result={}

    for result in results:
        #print (f"pvauser : {result['pvauser']['$oid']}\n")
        oneaccount = get_oneaddress_from_pvalist(result['pvauser']['$oid'], pva_users)
        if oneaccount == 0: #oid not found in DB
            print("oid not found in PVAUSER DB")
            continue
        final_result[oneaccount] = final_result.setdefault(oneaccount, {})
        final_result[oneaccount]["totalscore"] = (final_result[oneaccount].setdefault("totalscore", 0)) + result["gameresult"]
        final_result[oneaccount][result["gamename"]] = result["gameresult"]
# example for the struct being used:
# "one1tjn2mskvsczn666wktjtkshann9a6cp8d2tkty": {
#   "totalscore": 22,
#    "uptime": 21,
#    "newgame": 1
# }
    final_result = dict(sorted (final_result.items(), key=lambda x: x[1]['totalscore'], reverse=True))
    print (f"{final_result}\n")

    return final_result

@app.route("/")
def home():
    finalresult = build_finalresult()
    return render_template("index.html.j2", result=finalresult)

if __name__ == "__main__":
    #build_dashboard()
    app.run(host= '0.0.0.0', port=9081)

