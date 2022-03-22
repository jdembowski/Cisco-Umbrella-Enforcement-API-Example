#!/usr/bin/python3

# This script takes a list of hostnames and domains in a text file like so.
#
# example1.com
# example2.com
# example3.net
# example4.net
# example5.org
#
# and deletes from a list via the Umbrella Enforcement API.
#
# https://docs.umbrella.com/enforcement-api/reference/
#
# Read this link.
#
# https://docs.umbrella.com/enforcement-api/reference/#domain-acceptance-process2
#

import requests, json, sys, os, time, re

# Read the enforcement API token, single line
with open('enforcement-api-key.txt', 'r') as k:
    api_key = k.read().rstrip()

# Initialize vars
domains = []

if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    print('ERROR: please provide an input file name')
    sys.exit(1)

with open(filename) as f:
    domains = f.read().splitlines()

response = 0
count = 1
borked = 1

for item in domains:
    
    headers = {'content-type': 'application/json'}
    req = requests.delete('https://s-platform.api.opendns.com/1.0/domains/?customerKey='+api_key+'&where[name]='+item, headers=headers)
    response = req.status_code

    # Handle the different response codes.
    if response == 204:

        # Successful API submission so let's do the next chunk.
        print('Successfully deleted', item,'from the Enforcement API.', flush=True)
        delay_multiplier = 0
        count = count + 1
        borked = 0

    if response == 400:

        # Something may be borked in the input.
        print('Response:', response, 'Exiting due to input error.')
        print('Dumping the last domain.')
        print(item)
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
    
    if response == 404:

        # We are trying to delete something not there. All good.
        print('Response:', response, 'Deleting',item,'but the domain is not in the list.')
        delay_multiplier = 0
        count = count + 1
        borked = 0

    if response >= 500:
        # Something borked on the server side. Stop and report it.
        print('Response:', response, 'Exiting due to server side error.')
        sys.exit(1)

    if borked:
        # What was that??? Print the status code and exit.
        print('Unexpected status code', response,'exiting.')
        sys.exit(1)
