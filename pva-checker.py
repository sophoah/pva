#!/usr/bin/env python3
# coding: utf-8

import json
import requests
from requests.exceptions import HTTPError
import re
import argparse

def get_information_rpc(rpc_endpoint, method, params):
    url = rpc_endpoint
    headers = {'Content-Type': 'application/json'}
    data = {"jsonrpc":"2.0", "method": method, "params": params, "id":1}
    try:
        r = requests.post(url, headers=headers, data = json.dumps(data))
        r.raise_for_status()
    except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6
    else:
        content = json.loads(r.content)
        return content

def getNodemetadata_rpcurl(rpcurl):
    method = 'hmyv2_getNodeMetadata'
    params = []
    return get_information_rpc(rpcurl, method, params)['result']


def GetLatestChainHeaders_rpcurl(rpcurl):
    method = "hmyv2_getLatestChainHeaders"
    params = []
    return get_information_rpc(rpcurl, method, params)['result']

def getValidatorInfo_rpc(validator, rpcurl):
    method = "hmyv2_getValidatorInformation"
    params = [validator]
    return get_information_rpc(rpcurl, method, params)['result']

def getAllValidatorInfo_rpc(rpcurl):
    method = "hmyv2_getAllValidatorInformation"
    params = [-1]
    return get_information_rpc(rpcurl, method, params)['result']

def getNodeNetwork(nodeurl):
    nodeinfo = getNodemetadata_rpcurl(nodeurl)
    endpoint = ""

    if (nodeinfo['network'] == "mainnet"):
        endpoint=f"https://api.s0.t.hmny.io"
    if (nodeinfo['network'] == "testnet"):
        endpoint=f"https://api.s0.b.hmny.io"

    data["network"] = nodeinfo['network']
    data["endpoint"] = endpoint
    return data

def IsInSynced(nodeurl = "http://127.0.0.1:9500"):
    nodeinfo = getNodemetadata_rpcurl(nodeurl)
    shardid = nodeinfo['shard-id']
    network = nodeinfo['network']

    #print (shardid)

    if (network == "mainnet"):
        endpoint=f"https://api.s{shardid}.t.hmny.io"
    if (network == "testnet"):
        endpoint=f"https://api.s{shardid}.b.hmny.io"
    
    latest_headers = GetLatestChainHeaders_rpcurl(nodeurl)
    node_bc_shard_block_height = latest_headers['beacon-chain-header']['block-number']
    node_non_bc_shard_block_height = latest_headers['shard-chain-header']['block-number']

    network_latest_header = GetLatestChainHeaders_rpcurl(endpoint)
    network_bc_shard_block_height = network_latest_header['beacon-chain-header']['block-number']
    network_non_bc_shard_block_height = network_latest_header['shard-chain-header']['block-number']

    #print (f"  Node (s{shardid}) block info [{node_bc_shard_block_height}, {node_non_bc_shard_block_height}]")
    #print (f"  Network block info [{network_bc_shard_block_height}, {network_non_bc_shard_block_height}]")

    bc_diff = abs(node_bc_shard_block_height - network_bc_shard_block_height) 
    non_bc_diff = abs(node_non_bc_shard_block_height - network_non_bc_shard_block_height)

    bc_sync_status = True if bc_diff < 100 else False
    non_bc_sync_status = True if non_bc_diff < 100 else False

    #print (f"  {bc_sync_status}({bc_diff}) {non_bc_sync_status}({non_bc_diff})")

    if (bc_sync_status and non_bc_sync_status):
        return True
    else:
        return False

def CheckVersion(nodeurl = "http://127.0.0.1:9500", version = "v6268-v2.3.5"):
    nodeversion = getNodemetadata_rpcurl(nodeurl)['version']
    if re.search(version, nodeversion) != None:
        return True
    return False

def CheckBLS(validator, nodeurl = "http://127.0.0.1:9500"):
    nodeinfo = getNodemetadata_rpcurl(nodeurl)
    shardid = nodeinfo['shard-id']
    network = nodeinfo['network']
    endpoint = ""
    s0endpoint = ""
    #print (shardid)

    if (network == "mainnet"):
        endpoint=f"https://api.s{shardid}.t.hmny.io"
        s0endpoint=f"https://api.s0.t.hmny.io"
    if (network == "testnet"):
        endpoint=f"https://api.s{shardid}.b.hmny.io"
        s0endpoint=f"https://api.s0.b.hmny.io"

    validatorinfo = getValidatorInfo_rpc(validator, s0endpoint)

    #print(f"  {validatorinfo")

    configured_network_bls = validatorinfo["validator"]["bls-public-keys"]
    node_bls = nodeinfo["blskey"]

    #print("  {node_bls")

    for key_on_chain in configured_network_bls:
        key_found = False
        for key_on_node in node_bls:
            if key_on_chain == key_on_node:
                key_found = True
                continue
        if key_found == False:
            return False
    return True


def argsparse():
    parser = argparse.ArgumentParser(description="POPS PVA Checker")
    parser.add_argument( "-vc", "--versioncheck", 
                        help="harmony binary version to check",
                        default="v6268-v2.3.4")
    parser.add_argument( "-n", "--node", help="Validator Node URL (eg: http://1.1.1.1:9500)",
                        default="http://127.0.0.1:9500")
    parser.add_argument( "-vla", "--validator_addr", 
                         help="validator address the node is helping")
    args = parser.parse_args()
    return args

#use a master list and verify
PVA_Participants_List=[
{"address": "one13up8rppejatmznzr7nder8u6llatvudrumxt02", "challenges": ["uptime"] },
{"address": "one1tjn2mskvsczn666wktjtkshann9a6cp8d2tkty", "challenges": ["uptime"] },
{"address": "one1gyl6ja6d8tad75v3lrxq25gz0qka434v2eehpa", "challenges":["uptime"] },
{"address": "one16xwec874npwmm5shavyvjmhcg5u902ak2ad4vn", "challenges":["uptime"] },
{"address": "one12rjhtpwaclyms73lw3qjchs4httvr5nhxfc42l", "challenges":["uptime"] },
{"address": "one1t3tex27l80cs4eltq5t7wymcxwwct6xxuyf7w4", "challenges":["uptime"] },
{"address": "one1dzqeetfpyp02evw00mag4nnhlqvu92wr9esnq3", "challenges":["uptime"] },
{"address": "one1zv6rxnwm6e75f7qzca5eae3lxc8ggvnwq4qtj2", "challenges":["uptime"] },
{"address": "one16jck2hq039sp0w6ehhjkq858nz2a95emjqff0w", "challenges":["uptime"]},
{"address": "one1xx7d6ldrtla7dw7yawg4rq05ws05qrkhxxfqaa", "challenges":["uptime"]},
{"address": "one1d2zjm9czlfzdes97pfuzdydflw0t80kspwst0x", "challenges":["uptime"]},
{"address": "one14gevvn4z6vmz6htkxwp62pe77c3dwj3p2cvrv6", "challenges":["uptime"]},
{"address": "one122u7pnfsgk542ht3uankt270w3zcjzg35jccyp", "challenges":["uptime"]},
{"address": "one1hrcm8pesmwutea4cxa8690x2jdzfjx87sfj39k", "challenges":["uptime"]},
{"address": "one1p8xss440xe7qz862y6l5dqvc6pzs74hl0jfalz", "challenges":["uptime"]},
{"address": "one17qqnjy4llulpcs3g2uzryhehk5rcyedy4qhet6", "challenges":["uptime"]},
{"address": "one1hukwz92wuymvls8hrk4fhwclk0cer5r2f03mu4", "challenges":["uptime"]},
{"address": "one1ypmrh75zsqpav6q0hhpgm3p46jykkaclhp0ydl", "challenges":["uptime"]},
{"address": "one1ktksx4t8t6grdllrf8vv78pj8pc6fwggvjhqzq", "challenges":["uptime"]},
{"address": "one1dd3rjz4ew4m9k2pf285gyfesjwe03a7am6axll", "challenges":["uptime"]},
{"address": "one1djdj7g588xs4605laaxjxfrk0kuler2s6uasw6", "challenges":["uptime"]},
{"address": "one15hs9d9kdnsd5jxjmu507wljcmmdfe390akxe3d", "challenges":["uptime"]},
{"address": "one14gq8ptec7dynfxyv8elejnsqxjle44kyvk780r", "challenges":["uptime"]},
{"address": "one1akg6gqea74mmpjvd6qxlmd762v5gfy2e5r7xf2", "challenges":["uptime"]},
{"address": "one1k4scpcd3wh4arkjmec2dslmjtdjsqjhrve5cvc", "challenges":["uptime"]},
{"address": "one15zmw8ea9mjru57t2qr5dr6jkxd9u9rg4q6m5j9", "challenges":["uptime"]},
{"address": "one1wqyr9yp8uyjdfgaa73u8n5rj08eqdvd9p9wej8", "challenges":["uptime"]},
{"address": "one19py40wf5tu7pu2zdfy82y7nter86lk8h0pj906", "challenges":["uptime"]},
{"address": "one1svmrvxwaqdtaueqkhsahst3ay669sugxlqnyyt", "challenges":["uptime"]},
{"address": "one1w9u59r7v8cukhwfc2w0672j942txz4yn0sjwrh", "challenges":["uptime"]},
{"address": "one1qnn3nvgnzxqr9s44sjpgjsqs4jhl6hhls24vvq", "challenges":["uptime"]},
{"address": "one1yfscyp6cf5wpapy6mfwtvs840r3hqnac4ymvxp", "challenges":["uptime"]},
{"address": "one1ged33s5wrtprjmum7l6dmka9k5fd6q8zpsrfjz", "challenges":["uptime"]},
{"address": "one1qka5ahyct3k4hc6gqujedyj9xq3d68nj0ws4st", "challenges":["uptime"]},
{"address": "one1p60v292gndwqk5qskhf9szqdpysavvm06kf36a", "challenges":["uptime"]},
{"address": "one1nt66aaal0csfna3eaghmsqqxkz3exkvnn574lr", "challenges":["uptime"]},
{"address": "one1cg3p9e3vsrlf9lf8cw42tmpfzc9dc56l6r038g", "challenges":["uptime"]},
{"address": "one1l9cwh9t2h2zu094ykwuthnktqt42ltf64e5das", "challenges":["uptime"]},
{"address": "one1hjv0u6rcm0tdvh4k47y87lulu4fd0h2zgduyvz", "challenges":["uptime"]},
{"address": "one1y7sjnm3pxrunvj2t4k7dctj69rssuyfrgajpj0", "challenges":["uptime"]},
{"address": "one1ylm7uwfk60sy05luw5lp67ffywgvhsx639dp83", "challenges":["uptime"]},
{"address": "one1nsycmjwwe0fcdtzd4a3tgadfw76jxkuyhzsp4f", "challenges":["uptime"]},
{"address": "one1tnlzwvdc5yc98nfpvun300f2uqd6l5qgmyz46d", "challenges":["uptime"]},
{"address": "one17j706lucfndyf5celgpwru45cf0qn2yyqgsf6q", "challenges":["uptime"]},
{"address": "one1zr3y8tr2l5djdff5wjvtf0ec6j2shsp6rp5j80", "challenges":["uptime"]},
{"address": "one1wsha5ruzzp8sz6nu779wmt8a83vzp4wkc2fr9t", "challenges":["uptime"]},
{"address": "one1gjmkznyllxprpjj9yjvnyp3w2f0the7c7hvcjk", "challenges":["uptime"]},
{"address": "one1p5c73w3f8w666jy707mamkqv3vv8wwny5ypffk", "challenges":["uptime"]},
{"address": "one1t2t4kst30d0aprvp9rhk339upee6m23vlglsp6", "challenges":["uptime"]},
{"address": "one150r6lnl8yqua85vd9v5p2ju7zua62qc936q7ap", "challenges":["uptime"]},
{"address": "one14xfv2jv9fujjkg6t9qt7s2kz0ws290en8ngrsv", "challenges":["uptime"]},
{"address": "one1lrye4mmkld3a625ygvl8ulsmha3qzarmxny5pv", "challenges":["uptime"]},
{"address": "one18f0n04frheycfr75ccpntmrmrc0r368vdmjmru", "challenges":["uptime"]},
{"address": "one1m3w07gke5ekxg8yyj66v5eky5wx2e5kvqh3fkc", "challenges":["uptime"]},
{"address": "one1q6ml8lvk72de9ufhw99urv7kvpwqk647xj583j", "challenges":["uptime"]},
{"address": "one1t7p6nre40hq7z97anrf5cqug3n3776tn3as5ds", "challenges":["uptime"]},
{"address": "one16pwdqvu4kcq6rpazf3n729fzdw3gvgxc6luu8r", "challenges":["uptime"]},
{"address": "one132cjmjzxmqye0a0tv32mm2q6nrzwdcmpjysm87", "challenges":["uptime"]},
{"address": "one1zjlwqjty6kzefgt8lqgmsx4zzsafzdqxlejsvg", "challenges":["uptime"]},
{"address": "one1nhfnjxfwrkk8653jfz97wtdxvw295nws2vft48", "challenges":["uptime"]},
{"address": "one1xwapk9zj0vddz6803qdl2sv8wess7pjp89swvh", "challenges":["uptime"]},
{"address": "one1826ddqszv48s3a6tuhhrzmzr0xhl94v9fh2vv2", "challenges":["uptime"]},
{"address": "one1zh4q0k7zqzg29mmrnjyn4kg38ykxqkgr4c3adn", "challenges":["uptime"]}
]

PVA_Participants_List=[
{"address": "one13up8rppejatmznzr7nder8u6llatvudrumxt02", "challenges":["uptime"]},
{"address": "one1tjn2mskvsczn666wktjtkshann9a6cp8d2tkty", "challenges": ["uptime"]},
{"address": "one1yfscyp6cf5wpapy6mfwtvs840r3hqnac4ymvxp", "challenges": ["uptime"]},
{"address": "one1rne77yeqat997hvg59a9xqllhupj73vk34jq6e", "challenges": ["uptime"]}
]

PVA_List_address_only=[x['address'] for x in PVA_Participants_List]
#print(PVA_List_address_only)

# reading an URL url returning a JSON
def get_url(url):
    try:
        r = requests.get(url)
        out = r.json()
    except:
        return '{"error": "reading json RPC"}'
    return out

def post_url(url, data):
    headers = {'Content-Type': 'application/json'}
    try:
        r = requests.post(url, headers=headers, data = json.dumps(data))
        r.raise_for_status()
    except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6
    else:
        content = json.loads(r.content)
        return content

def put_url(url, data):
    headers = {'Content-Type': 'application/json'}
    try:
        r = requests.put(url, headers=headers, data = json.dumps(data))
        r.raise_for_status()
    except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6
    else:
        print(r.content)
        content = json.loads(r.content)
        return content

def GetPVADetails():
    testneturl='https://api.s0.b.hmny.io'
    allvalidator = getAllValidatorInfo_rpc(testneturl)    
    #filter PVA participants from the validator all information
    pvavalidators=[x for x in allvalidator if x['validator']['address'] in PVA_List_address_only]
    #print (pvavalidators)
    return pvavalidators

def ShowPVAdb():
    pvausers = get_url('http://127.0.0.1:5000/pvausers')
    print (pvausers[1])
    pvaresults = get_url('http://127.0.0.1:5000/results')

#first time creating of all users
def CreateAllPVAUser():
    for pvauser in PVA_List_address_only:        
        data = {
            'validatoraddress': pvauser,
            'validatorcreated': "False",
            'ispops': "False",
            'challenges': ['uptime']
        }
        post_url('http://127.0.0.1:5000/pvausers', data)

#first time creating uptime challenge
def CreateUptimeChallenge():
    for pvauser in PVA_List_address_only:
        data = {
            'pvauser': pvauser,
            'gameresult': 0,
            'gamename': 'uptime'
        }
        post_url('http://127.0.0.1:5000/results', data)

def testUptime(OnChainPvaValidatorInfo):
    for pvauser in PVA_Participants_List:
        for onchainpvauser in OnChainPvaValidatorInfo:
            if pvauser['address'] == onchainpvauser['validator']['address']:
                #put_url(f"http://127.0.0.1:5000/pvausers/add/{pvauser['address']}'", {'validatorcreated': 'True'})
                if onchainpvauser['active-status'] == 'active':
                    uptimepoints = get_url(f"http://127.0.0.1:5000/pvausers/add/{pvauser['address']}/results/uptime")
                    if len(uptimepoints) == 0:
                        #create the uptime results related fields
                        post_url(f"http://127.0.0.1:5000/pvausers/add/{pvauser['address']}/results/uptime", {"gameresult": 1})
                    else:
                        #print(f"{type(uptimepoints)} / {dir(uptimepoints)} : {uptimepoints}")
                        newpoints = int(uptimepoints[0]['gameresult']) + 1
                        #newpoints = 2
                        data = {"gameresult": newpoints } #int(uptimepoints.gameresult) + 1
                        #print(uptimepoints)
                        #print(f"new data to be saved: {data}")
                        put_url(f"http://127.0.0.1:5000/pvausers/add/{pvauser['address']}/results/uptime", data)
                        print(f"updated uptime for {pvauser['address']} with {data}")



if __name__ == "__main__":
    pvavalidators = GetPVADetails()
    testUptime(pvavalidators)
    
    #CreateAllPVAUser()
    #ShowPVAdb()

    # args = argsparse()
    # version = args.versioncheck
    # node_rpc = args.node
    # validator = args.validator_addr

    # print("PVA node Checker")
    
    # blscheck_result = CheckBLS(validator, node_rpc)
    # print(f"BLS check : {blscheck_result}")

    # version_result = CheckVersion(node_rpc, version)
    # print(f"Version expect ({version}) : {version_result}")

    # nodesync_result = IsInSynced(node_rpc)
    # print(f"Node sync: {nodesync_result}")