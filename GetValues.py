#import statements
import re
import json
from datetime import datetime
date_format = '%d/%m/%Y'

#initialize all values to blank
sessionId = platform = fsearch_flightType = fsearch_origin = fsearch_destination = fsearch_depdate = \
fsearch_arrdate = fsearch_adults = fsearch_child = fsearch_infants = fsearch_class = pmCode = qbCard = promo = ""
platform = "app android"
inscheck = promosuccess = promofailure = "0"
insnotcheck = "1"
isRoundTrip = False
isInt = False
loginAtStart = False
isGuestUser = False


#Keys which are not applicable in case of OW
valuesNotApplicable = ['adobe.fsearch.arrdate', 'adobe.fsearch.ret.resultnumber', 'adobe.review.ret.class', 'adobe.review.ret.time',
'adobe.review.ret.id', 'adobe.review.ret.date', 'adobe.review.ret.stops', 'adobe.review.ret.ref', 'adobe.review.ret.difference', 'adobe.review.ret.searchrank',
'adobe.review.ret.fare', 'adobe.review.ret.class', 'adobe.review.ret.time', 'adobe.review.ret.id', 'adobe.review.ret.date', 'adobe.review.ret.stops', 'adobe.review.ret.ref',
'adobe.review.ret.diffrence', 'adobe.review.ret.searchrank', 'adobe.review.ret.fare', 'adobe.review.ret.id']

#Parse the logs and check for values
with open("AdobeLogs.txt", encoding='ISO-8859-1', errors='ignore') as f:
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
            if(len(j['tripList']))>1:
                isRoundTrip = True
                print("This is a Round Trip Flow...................")
                fsearch_arrdate = j['tripList'][1]['departureDate']
            fsearch_infants = j["noOfInfants"]
            fsearch_child = j["noOfChildren"]
            fsearch_adults = j["noOfAdults"]
            fsearch_class = j["travelClass"].lower()
            if(j["domain"]=="INT"):
                isInt = True
        elif("promoContext=REVIEW, " in line and "promoCode=" in line):
            # print("LINE: "+line)
            promo = line.split("promoCode=")[1].split(",")[0].lower()
        elif("interactionType=ValidatePromocode" in line):
            if("=200" in line):
                promosuccess = "1"
            else:
                promofailure="1"
        elif("onOptionalAddOnClicked :: Insurance is checked" in line):
            print("Insurance is selected.")
            inscheck = "1"
            insnotcheck = "0"
        elif("cybersourceFingerprintId" in line and "Post Method Request String is" in line):
            pmCode = line.split("payop%3D")[1].split("%7")[0]
            if("saveQBCard%3Dtrue" in line):
                saveQBCard = "yes"
            else:
                saveQBCard = "no"
        # elif("&purchaseAmount=" in line and "email=&" in line):
        #     print("**************** User wasn't logged in while searching flights....")
        # elif("&purchaseAmount=" in line and "email=" in line):
        #     print("**************** User was logged in while searching flights....")
        # if("userId%22%3A%22guest" in line):
        #     print("**************** User continued as guest..........")


    depDate = datetime.strptime(fsearch_depdate, date_format)
    if isRoundTrip:
        arrDate = datetime.strptime(fsearch_arrdate, date_format)
    today = datetime.today()
    daysToDep = depDate - today
    if isRoundTrip:
        daysToArr = arrDate - today
    # print("Dep Date: "+str(depDate)+"--->"+str(daysToDep))
    # print("Arr Date: "+str(arrDate)+"--->"+str(daysToArr))

def ifNumber(expected):
    if(".0" in expected):
        try:
            float(expected)
            return expected.split(".")[0]
        except ValueError:
            print("Exception: Not a float value")
    else:
        return expected

def reviewDays():
    if isRoundTrip:
        return str(daysToDep.days + 1)+"|"+str(daysToArr.days + 1)
    else:
        return str(daysToDep.days + 1)

def validateValues(key, expected, actual):
    #Key:Value pairs which can  be cross-verified from the device logs
    valuesFromLogs = {'adobe.content.platform':platform,'adobe.content.sessionid':sessionId,'adobe.user.loginstatus':"logged-in",
'adobe.link.platform':platform, 'adobe.link.sessionid':sessionId,
'adobe.fsearch.flightType':fsearch_flightType,'adobe.fsearch.origin':fsearch_origin,
'adobe.fsearch.destination':fsearch_destination,'adobe.fsearch.depdate':fsearch_depdate,
'adobe.fsearch.arrdate':fsearch_arrdate,'adobe.fsearch.adults':fsearch_adults,'adobe.fsearch.child':fsearch_child,
'adobe.fsearch.infants':fsearch_infants,'adobe.fsearch.class':fsearch_class,'adobe.review.depcity':fsearch_origin,
'adobe.review.arrcity':fsearch_destination, 'adobe.review.days':reviewDays(),
'adobe.review.adults': fsearch_adults, 'adobe.review.child':fsearch_child, 'adobe.review.infants':fsearch_infants,
'adobe.review.dep.class':fsearch_class,'adobe.review.dep.date':fsearch_depdate,'adobe.review.ret.date':fsearch_arrdate,
'adobe.review.flightType':fsearch_flightType, 'adobe.promo.promocode':promo, 'adobe.event.promosuccess':promosuccess,
'adobe.event.promofailure':promofailure, 'adobe.event.inscheck':inscheck, 'adobe.event.insnotcheck':insnotcheck,
'adobe.review.checkouttype':'logged-in', 'adobe.review.paymethod':pmCode+"|"+saveQBCard
}
    #Keys for which the values cannot be verified from Logs. Here we are assuming that the values are correct.
    valuesNotInLogs = ['adobe.fsearch.dep.resultnumber','adobe.fsearch.ret.resultnumber','adobe.sort.filterterm','adobe.review.duration',
    'adobe.review.dep.time', 'adobe.review.dep.id', 'adobe.review.dep.stops', 'adobe.review.dep.ref', 'adobe.review.dep.difference',
    'adobe.review.dep.searchrank', 'adobe.review.dep.fare', 'adobe.review.ret.class', 'adobe.review.ret.time', 'adobe.review.ret.id',
    'adobe.review.ret.stops', 'adobe.review.ret.ref', 'adobe.review.ret.difference', 'adobe.review.ret.searchrank', 'adobe.review.ret.fare',
    'adobe.review.flightinc','adobe.review.ret.diffrence','adobe.review.dep.diffrence','adobe.review.promodropdown','adobe.user.email','adobe.user.number']

    key = str(key)
    expected = str(expected)
    actual = str(actual)
    expected = ifNumber(expected)
    if(key in valuesFromLogs.keys()):
        print ("Expected value for Key: "+key+" needs to be extracted from Device Logs")
        expected = str(valuesFromLogs[key])
    elif(key in valuesNotInLogs):
        print ("Expected value for Key: "+key+" cannot be extracted from Device Logs. Assuming the passed value to be correct.")
        return (expected, actual, True)
    elif(("pagename" in key) and (isInt==True)):
        expected = expected.replace("dom","int")
    elif(("domestic" in expected) and (isInt==True)):
        expected = expected.replace("domestic","international")
    return (expected, actual, str(expected)==str(actual))