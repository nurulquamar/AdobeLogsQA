#import statements
import re
import json
from datetime import datetime
date_format = '%d/%m/%Y'

#initialize all values to blank
sessionId = platform = fsearch_flightType = fsearch_origin = fsearch_destination = fsearch_depdate = \
fsearch_arrdate = fsearch_adults = fsearch_child = fsearch_infants = fsearch_class = pmCode = qbCard = promo = ""
platform = "app android"
inscheck = promofailure = promosuccess = "0" 
insnotcheck = "1"
isRoundTrip = isInt = isPriceChanged = False
flightsFound = True
login_state_before_PaxPage = login_state_from_PaxPage = "logged-in"

#Keys which are not applicable in case of OW
valuesNotApplicable = ['adobe.fsearch.arrdate', 'adobe.fsearch.ret.resultnumber', 'adobe.review.ret.class', 'adobe.review.ret.time',
'adobe.review.ret.id', 'adobe.review.ret.date', 'adobe.review.ret.stops', 'adobe.review.ret.ref', 'adobe.review.ret.difference', 'adobe.review.ret.searchrank',
'adobe.review.ret.fare', 'adobe.review.ret.class', 'adobe.review.ret.time', 'adobe.review.ret.id', 'adobe.review.ret.date', 'adobe.review.ret.stops', 'adobe.review.ret.ref',
'adobe.review.ret.diffrence', 'adobe.review.ret.searchrank', 'adobe.review.ret.fare', 'adobe.review.ret.id']

NA_Tables = ["FlightSRP-->SRP Track Action (roundtrip case - No Search Result Found)","FlightReviewPage-->Track Action (in case of promosuccess)", "FlightReviewPage-->Track Action (in case of promofailure)",
"FlightReviewPage-->Track Action (in case of fare change shown)", "FlightReviewPage-->Track Action (in case of continue click on fare change)",
"FlightReviewPage-->Track Action (in case of select another flight on fare change)", "FlightReviewPage-->Track State (On click of GST)",
"FlightLoginPage-->Track State (Login page)", "FlightLoginPage-->Track Action (in case of guest booking or guest checkout)", 
"InternationalFlightCase-->Track State (On SRP page when click on more flights)"]

def getStatus():
    global login_state_before_PaxPage, login_state_from_PaxPage, promofailure, promosuccess, isPriceChanged
    global fileContents
    with open("AdobeLogs.txt", encoding='ISO-8859-1', errors='ignore') as f:
        fileContents = f.read()

    # Check if user was logged in before the flight pax page
    getPromoLogs = re.findall('Parameters::: {(.*?)email=,(.*?)}', fileContents)
    if(len(getPromoLogs)>=1):
        login_state_before_PaxPage = "guest"
    else:
        login_state_before_PaxPage = "logged-in"

    # Check if user was logged in after review page
    saveReviewLogs = re.findall('\"userId\":\"(.*?)\"}', fileContents, re.S)
    if ("guest" in str(saveReviewLogs)):
        login_state_before_PaxPage = login_state_from_PaxPage = "guest"
    else:
        login_state_from_PaxPage = "logged-in"

    #Check if flight results were fetched
    depFlightCount = re.findall('(?<=dep.resultnumber:)(?s)(\d+)',fileContents)
    print(" Departure Flight Count : "+str(depFlightCount))
    if(depFlightCount=="0"):
        flightsFound = False
    if(isRoundTrip):
        retFlightCount = re.findall('(?<=ret.resultnumber:)(?s)(\d+)',fileContents)
        print(" Return Flight Count : "+str(retFlightCount))
        if(retFlightCount == "0"):
            flightsFound = False

    #Check for promo validation
    promoVal = re.findall('ResponseContainer(.+)ValidatePromocode(.+)]',fileContents)
    if("Invalid promocode" in str(promoVal)):
        promofailure = "1"
    if("resCode=200" in str(promoVal)):
        promosuccess = "1"

    #Check for price Changed
    priceChanged = re.findall('responseString(.+)\"priceChanged\":true',fileContents)
    if(len(priceChanged)>0):
        isPriceChanged = True


def isTableNA():
    global NA_Tables
    #Remove those tables from NA_Tables which are applicable
    print(" ------------------- Executed --------------- ")

    #If flight results are found, the "No results found" table is NA
    if not(flightsFound):
        NA_Tables.remove("FlightSRP-->SRP Track Action (roundtrip case - No Search Result Found)")

    #If promo validation did not fail
    if not(promofailure=="0"):
        NA_Tables.remove("FlightReviewPage-->Track Action (in case of promofailure)")

    #If promo validation did not succeed
    if not(promosuccess=="0"):
        NA_Tables.remove("FlightReviewPage-->Track Action (in case of promosuccess)")

    #if Dom flow
    if (isInt==True):
        NA_Tables.remove("InternationalFlightCase-->Track State (On SRP page when click on more flights)")

    #If price was changed
    if(isPriceChanged == True):
        NA_Tables.remove("FlightReviewPage-->Track Action (in case of fare change shown)")
        NA_Tables.remove("FlightReviewPage-->Track Action (in case of continue click on fare change)")
        NA_Tables.remove("FlightReviewPage-->Track Action (in case of select another flight on fare change)")

    if(login_state_from_PaxPage=="guest"):
        NA_Tables.remove("FlightLoginPage-->Track Action (in case of guest booking or guest checkout)")


def printInfo():
    maxSize = 40
    print('+' + '-'*48 + '+')
    if(isInt):
        print('| %-*.*s |' % (maxSize, maxSize, "\tSector : International"))
        # print()
    else:
        print('| %-*.*s |' % (maxSize, maxSize, "\tSector : Domestic"))
    if(isRoundTrip):
        print('| %-*.*s |' % (maxSize, maxSize, "\tType : RoundTrip"))
    else:
        print('| %-*.*s |' % (maxSize, maxSize, "\tType : OneWay"))
    print('| %-*.*s |' % (maxSize, maxSize, "\tOrigin : "+fsearch_origin.upper()))
    print('| %-*.*s |' % (maxSize, maxSize, "\tDestination : "+fsearch_destination.upper()))
    print('| %-*.*s |' % (maxSize, maxSize, "\tDepart Date : "+fsearch_depdate))
    if(isRoundTrip):
        print('| %-*.*s |' % (maxSize, maxSize, "\tArrival Date : "+fsearch_arrdate))
    print('| %-*.*s |' % (maxSize, maxSize, "\t"+str(fsearch_adults)+" Adults || "+str(fsearch_child)+" Children || "+str(fsearch_infants)+" Infants"))
    if(login_state_before_PaxPage == "logged-in"):
        print('| %-*.*s |' % (maxSize, maxSize, "\tUser was already logged-in throughout the flow "))
    elif(login_state_from_PaxPage == "guest"):
        print('| %-*.*s |' % (maxSize, maxSize, "\tUser continued as Guest "))
    else:
        print('| %-*.*s |' % (maxSize, maxSize, "\tUser was logged-in during the flow."))
    print('+' + '-'*48+ '+')
    print("\n\n")

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
                # print("This is a Round Trip Flow...................")
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
        elif("onOptionalAddOnClicked :: Insurance is checked" in line):
            # print("Insurance is selected.")
            inscheck = "1"
            insnotcheck = "0"
        elif("cybersourceFingerprintId" in line and "Post Method Request String is" in line):
            pmCode = line.split("payop%3D")[1].split("%7")[0]
            if("saveQBCard%3Dtrue" in line):
                saveQBCard = "yes"
            else:
                saveQBCard = "no"

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

def validateValues(key, expected, actual, sheetName):
    global login_state_from_PaxPage, login_state_before_PaxPage
    #Key:Value pairs which can  be cross-verified from the device logs
    valuesFromLogs = {'adobe.content.platform':platform,'adobe.content.sessionid':sessionId,
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
    'adobe.review.flightinc','adobe.review.ret.diffrence','adobe.review.dep.diffrence','adobe.review.promodropdown','adobe.user.email','adobe.user.number','adobe.sort.sorttype']

    key = str(key)
    expected = str(expected)
    actual = str(actual)
    expected = ifNumber(expected)
    if(key in valuesFromLogs.keys()):
        # print ("Expected value for Key: "+key+" needs to be extracted from Device Logs")
        expected = str(valuesFromLogs[key])
    elif(key in valuesNotInLogs):
        # print ("Expected value for Key: "+key+" cannot be extracted from Device Logs. Assuming the passed value to be correct.")
        return (expected, actual, True)
    elif(("pagename" in key) and (isInt==True)):
        expected = expected.replace("dom","int")
    elif(("domestic" in expected) and (isInt==True)):
        expected = expected.replace("domestic","international")
    #Check the login cases
    if(key == "adobe.user.loginstatus" or key == "adobe.review.checkouttype"):
        #If the user went till bank page as guest, then pass the value as guest for all pages.
        if(login_state_from_PaxPage == "guest"):
            expected = "guest"
        #If the user was logged in while making the search, then pass the value as logged-in for all pages.
        elif(login_state_before_PaxPage == "logged-in"):
            expected = "logged-in"
        #If the used logged-in or registered during the flow then pass the value accordingly on all pages.
        elif(login_state_before_PaxPage=="guest" and login_state_from_PaxPage=="logged-in"):
            # print("Sheet name: "+sheetName)
            if(sheetName in ["FlightHome","FlightSRP","FlightReviewPage"]):
                expected = "guest"
            else:
                expected = "logged-in"
    return (expected, actual, str(expected)==str(actual))
