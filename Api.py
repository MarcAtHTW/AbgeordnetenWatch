import json
import urllib2

'''
API-Verbintdung zu Abgeordnetenwatch
'''

url = "https://www.abgeordnetenwatch.de/api/parliaments.json"
data = json.load(urllib2.urlopen(url))

print json.dumps(data, indent=4)