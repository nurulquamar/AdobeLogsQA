#import statements
import re
import json

#initialize all values to blank
sessionId = platform = fsearch_flightType = fsearch_origin = fsearch_destination = fsearch_depdate = \
fsearch_arrdate = fsearch_adults = fsearch_child = fsearch_infants = fsearch_class = ""

customValues = ['adobe.content.platform','adobe.content.sessionid','adobe.user.loginstatus','adobe.link.platform',
'adobe.link.sessionid','adobe.fsearch.flightType','adobe.fsearch.origin','adobe.fsearch.destination','adobe.fsearch.depdate',
'adobe.fsearch.arrdate','adobe.fsearch.adults','adobe.fsearch.child','adobe.fsearch.infants','adobe.fsearch.class']

platform = "app android"

#parse the logs and check for values
with open("AdobeLogs.txt") as f:
    for line in f:
        #get origin, destination, trip type, depart date, arrival date, class, number of Adults, Infants and Children from Request
        if("Nimble search Criteria" in line):
            #split the request params
            req_params =  line.split("Criteria ")[1]
            #convert it to JSON
            j = json.loads(req_params)
            #get Values from JSON
            sessionId = j['sessionId']
            fsearch_flightType = j["tripType"].lower()
            fsearch_origin = j['tripList'][0]["origin"].lower()
            fsearch_destination = j['tripList'][0]["destination"].lower()
            fsearch_depdate = j['tripList'][0]['departureDate']
            fsearch_arrdate = j['tripList'][1]['departureDate']
            fsearch_infants = j["noOfInfants"]
            fsearch_child = j["noOfChildren"]
            fsearch_adults = j["noOfAdults"]
            fsearch_class = j["travelClass"].lower()

def ifNumber(expected):
    if(".0" in expected):
        try:
            float(expected)
            return expected.split(".")[0]
        except ValueError:
            print("Exception: Not a float value")
    else:
        return expected

def validateValues(key, expected, actual):
    key = str(key)
    expected = str(expected)
    actual = str(actual)
    expected = ifNumber(expected)
    if(key in customValues):
        if("sessionid" in key):
            expected = sessionId
        elif("platform" in key):
            expected = platform
        elif("loginstatus" in key):
            expected = "logged-in"
        elif("flightType" in key):
            expected = fsearch_flightType
        elif("origin" in key):
            expected = fsearch_origin
        elif("destination" in key):
            expected = fsearch_destination
        elif("depdate" in key):
            expected = fsearch_depdate
        elif("arrdate" in key):
            expected = fsearch_arrdate
        elif("fsearch.adults" in key):
            expected = fsearch_adults
        elif("fsearch.fsearch_child" in key):
            expected = fsearch_child
        elif("fsearch.infants" in key):
            expected = fsearch_infants
        elif("fsearch.class" in key):
            expected = fsearch_class
    return (expected, actual, str(expected)==str(actual))