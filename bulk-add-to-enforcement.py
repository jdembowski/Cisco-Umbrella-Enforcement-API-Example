#!/usr/bin/python3

# This script takes a list of hostnames and domains in a text file like so.
#
# example1.com
# example2.com
# example3.net
# example4.net
# example5.org
#
# and inserts it into a list via the Umbrella Enforcement API.
#
# https://docs.umbrella.com/enforcement-api/reference/
#
# Read this link.
#
# https://docs.umbrella.com/enforcement-api/reference/#domain-acceptance-process2
#
# If the target host name or domain does not match that criteria then the item
# will not be added to the list.

import requests, json, sys, os, time, re
from datetime import datetime

# Read the enforcement API token, single line
with open('enforcement-api-key.txt', 'r') as k:
    api_key = k.read().rstrip()

# Initialize vars
domains = []
timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.0Z")
# timestamp ='2013-02-08T09:30:26.0Z'

if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    print('ERROR: please provide an input file name')
    sys.exit(1)

with open(filename) as f:
    domains = f.read().splitlines()

# Make one long list into a list of lists and each list has a number of items.
# Python is cool.

# Use a small number. 100 is bad.
items = 100
domains = [domains[i:i + items] for i in range(0, len(domains), items)]

count = 1
delay_multiplier = 0

for chunk in domains:
    bigdata=[]

    for domain in chunk:
        if (
                # Simple URL character test
        		re.search(r'[\*\/\\:]', domain) or
                # No IP Addresses please
        		re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain) or
                # FQDNs only
        		len(domain.split('.')) == 1 or
                # Numbers in TLDs are not valid.
        		re.search(r'[0-9]', domain.split('.')[-1])
        	):
            print('Skipped invalid input', domain)
        else:
            # Add valid hostname or domain to json
            data={}
            data = {
            'deviceId': 'ba6a59f4-e692-4724-ba36-c28132c761de',
            'deviceVersion': '13.7a',
            'eventTime': timestamp,
            'alertTime': timestamp,
            'dstDomain': domain,
            'dstUrl': 'http://'+domain+'/bad-url',
            'protocolVersion': '1.0a',
            'providerName': 'Security Platform'
            }
            bigdata.append(data)

    print('Chunk No.:', count, 'in',len(domains))

    # Reset the response and make sure we default to borked. Python doesn't have
    # a case statement. Shut up.
    response = 0
    borked = 1

    while response != 202:
        headers = {'content-type': 'application/json'}
        req = requests.post('https://s-platform.api.opendns.com/1.0/events?customerKey='+api_key, data=json.dumps(bigdata), headers=headers)
        response = req.status_code

        # Handle the different response codes.
        if response == 202:

            # Successful API submission so let's do the next chunk.
            print('Successfully submitted', len(bigdata),'entries to the Enforcement API.', flush=True)
            delay_multiplier = 0
            count = count + 1
            borked = 0

        if response == 400:

            # Something may be borked in the input.
            print('Response:', response, 'Exiting due to input error.')
            print('Dumping the last chunk of data.')
            print(bigdata)
            sys.exit(1)

        if response == 401:

            # Authentication error with the API key token.
            print('Response:', response, 'Exiting due to invalid API token.')
            print('Please check the token in your Umbrella dashboard.')
            sys.exit(1)

        if response == 403:

            # The API key token exists but has not been enabled in the Umbrella dashboard.
            print('Response:', response, 'Exiting due to API authentication error.')
            print('The API token exists but is not enabled in your Umbrella dashboard.')
            sys.exit(1)

        if response == 429:
            # If the API is waving us off then we're hitting the rate limit.
            # Start with a 15 second wait and keep bumping it up with each 429.
            delay_multiplier = delay_multiplier + 1
            print('Response:', response, 'Rate limited - waiting', 65 * delay_multiplier, 'seconds', flush=True)
            time.sleep(65 * delay_multiplier)
            borked = 0

        if response >= 500:
            # Something borked on the server side. Stop and report it.
            print('Response:', response, 'Exiting due to server side error.')
            sys.exit(1)

        if borked:
            # What was that??? Print the status code and exit.
            print('Unexpected status code', response,'exiting.')
            sys.exit(1)

print('Done')
