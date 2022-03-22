#!/usr/bin/python

# Use pip install requests if your system is missing it. My Windows PC was.
import requests, json

# Read Eforcement API key, single line
with open('enforcement-api-key.txt', 'r') as k:
    api_key = k.read().rstrip()

domain_list = []
# This is a paged output and the max entries per page is 200 (the default)
next='https://s-platform.api.opendns.com/1.0/domains'+'?customerKey='+api_key+'&limit=200'
page=0

# keep doing GET requests, until looped through all domains
# or in this case stop at 10 pages of 200 entries each.
# The enforcement integration I test with has over 130k domains.
while next:
    req = requests.get(next)
    json_file = req.json()
    # print(json.dumps(json_file,sort_keys=True, indent=4))
    for row in json_file["data"]:
        domain_list.append(row["name"])
    # GET requests will only list 200 domains, if more than that, it will request next bulk of 200 domains
    #if bool(json_file["meta"]["next"]):
    #    next = json_file["meta"]["next"]
    next = json_file["meta"]["next"]
    page = json_file['meta']['page']


for domain in domain_list:
    print(domain, flush=True)
