#import statements
from xlrd import open_workbook
import xlsxwriter
import GetValues as values

#Mapping Pagename values in tables to SheetNames in Workbook
sheetNameMap = {"yt:flight:home":"FlightHome",
                "yt:flight:home:origin":"FlightHome",
                "yt:flight:home:destination":"FlightHome",
                "yt:flight:home:calendar":"FlightHome",
                "yt:flight:dom:srp":"FlightSRP",
                "yt:flight:dom:srp:filter":"FlightSRP",
                "yt:flight:dom:checkout:review":"FlightReviewPage",
                "yt:flight:dom:checkout:review:fare rules":"FlightReviewPage",
                "yt:flight:dom:checkout:review:gst":"FlightReviewPage",
                "yt:flight:dom:checkout:travellers":"FlightTravellersPage",
                "yt:flight:dom:checkout:payment":"FlightPaymentPage",
                "yt:flight:dom:checkout:payment:wallets":"FlightPaymentPage",
                "yt:flight:int:srp":"FlightSRP",
                "yt:flight:int:srp:filter":"FlightSRP",
                "yt:flight:int:checkout:review":"FlightReviewPage",
                "yt:flight:int:checkout:review:fare rules":"FlightReviewPage",
                "yt:flight:int:checkout:review:gst":"FlightReviewPage",
                "yt:flight:int:checkout:travellers":"FlightTravellersPage",
                "yt:flight:int:checkout:payment":"FlightPaymentPage",
                "yt:flight:int:checkout:payment:wallets":"FlightPaymentPage"
                }

wb_input = open_workbook('Flights.xlsx')
wb_output = xlsxwriter.Workbook('Results_Flights.xlsx')
sheet_names = wb_input.sheets()
names = {}
COLUMN = 0
PASSED = FAILED = TOTAL = BLANK = 0
ROW_PAGE_NAME = 2
ROW_CLICK_NAME = 8
event_not_resolved = []
table_not_logged = []

#Set Formatting in the sheet
format_fail = wb_output.add_format({'bold': True, 'font_color': 'red','border':1})
format_pass = wb_output.add_format({'bold': True, 'font_color': 'green','border':1})
format_NA = wb_output.add_format({'bold': True, 'font_color': '#5DADE2','border':1})
format_bold = wb_output.add_format({'bold': True})
format_heading1 = wb_output.add_format({'bold': True,'bg_color':'#82C1EB','border':2,'align': 'center'})
format_heading2 = wb_output.add_format({'bold': True,'bg_color':'#8DE1F0','border':2})
format_border = wb_output.add_format({'border':1})
format_bold_border = wb_output.add_format({'border':1, 'bold':True})

def getAllTableNames():
    for s in range(0,len(sheet_names)):
        currentSheet = wb_input.sheet_by_index(s)
        for c in range(0,currentSheet.ncols):
            if("Track" in currentSheet.cell(0,c).value):
                table_not_logged.append(sheet_names[s].name+"-->"+str(currentSheet.cell(0,c).value))

#Write the summary of total events in a new sheet named Summary
def writeSummary():
    print("Writing values in Summary Sheet...")
    global PASSED, FAILED, TOTAL, BLANK
    worksheet = wb_output.add_worksheet("Summary")
    # worksheet.set_column(1, 0, 25)
    worksheet.merge_range(0, 0, 0, 1, "Summary", format_heading1)
    worksheet.write(1, 0, "Total Events Passed", format_heading2)
    worksheet.set_column(1, 0, 25)
    worksheet.write(1, 1, TOTAL, format_bold_border)
    worksheet.write(2, 0, "Correct Events Passed", format_heading2)
    worksheet.set_column(2, 0, 25)
    worksheet.write(2, 1, PASSED, format_bold_border)
    worksheet.write(3, 0, "Incorrect Events Passed", format_heading2)
    worksheet.set_column(3, 0, 25)
    worksheet.write(3, 1, FAILED, format_bold_border)
    worksheet.write(4, 0, "Blank Events Passed", format_heading2)
    worksheet.set_column(4, 0, 25)
    worksheet.write(4, 1, BLANK, format_bold_border)
    worksheet.write(6, 0, "Following logs didn't match the tables:",format_heading1)
    worksheet.set_column(6, 0, 40)
    for i in range(0,len(event_not_resolved)):
        worksheet.write(7+i, 0, event_not_resolved[i],format_fail)
    worksheet.write(9+i, 0, "Following tables didn't match the logs:",format_heading1)
    for j in range(0,len(table_not_logged)):
        worksheet.write(10+i+j, 0, table_not_logged[j],format_fail)

    #create pie chart
    chart = wb_output.add_chart({'type': 'pie'})
    chart.add_series({
        'categories': '=Summary!$A$3:$A$5',
        'values':     '=Summary!$B$3:$B$5',
        'data_labels': {'value': True},
        'points': [
            {'fill': {'color': '#58D68D'}},
            {'fill': {'color': '#EC7063'}},
            {'fill': {'color': '#CACFD2'}},
        ],
    })
    worksheet.insert_chart('C3', chart)

#Write key, expected values, actual values and Pass/Fail to Output sheet
def writeToSheet(page,dic):
    global COLUMN, PASSED, FAILED, TOTAL, BLANK
    if(page.replace("_",":") in sheetNameMap.keys()):
        if("content.pagename" in str(dic)):
            uniqueKey = "adobe.content.pagename"
            uniqueRow = ROW_PAGE_NAME
            uniqueValue = page.replace("_",":")
        elif("link.pagename" in str(dic)):
            uniqueKey = "adobe.link.clinkname"
            uniqueRow = ROW_CLICK_NAME
            uniqueValue = dic['adobe.link.clinkname']

        #Find the sheet index to be read
        for sname in sheet_names:
            if sname.name == sheetNameMap[page.replace("_",":")]:
                sheetNumber = sheet_names.index(sname)

        #Read Sheet by Index Number
        inputSheet = wb_input.sheet_by_index(sheetNumber)

        #find the cell that has the same value as Pagename.
        for col in range(0,inputSheet.ncols - 1):
            keyCol = inputSheet.cell(uniqueRow,col).value
            ValueCol  = inputSheet.cell(uniqueRow,col+1).value
            if((values.isInt == True) and ("dom") in ValueCol):
                ValueCol = ValueCol.replace("dom","int")
            # print("Unique Key:Val--> "+uniqueKey+" : "+uniqueValue+"\tActual Key:Val-->"+keyCol+" : "+ValueCol)
            if((uniqueKey == keyCol.strip()) and (uniqueValue == ValueCol.strip())):
                print("Page Name Found at "+str(uniqueRow)+", "+str(col))
                tableHeading = inputSheet.cell(0,col).value
                print("Table Heading: "+tableHeading)
                #Create a sheet with same name as Input Sheet
                worksheetName = sheetNameMap[page.replace("_",":")]
                if wb_output.get_worksheet_by_name(worksheetName) == None:
                    print("Creating new sheet with name: "+worksheetName)
                    worksheet = wb_output.add_worksheet(worksheetName)
                    COLUMN = 0
                else:
                    print("Worksheet named: "+worksheetName+" already exists. Using the existing one.")
                    worksheet = wb_output.get_worksheet_by_name(worksheetName)

                if(worksheetName+"-->"+tableHeading in table_not_logged):
                    table_not_logged.remove(worksheetName+"-->"+tableHeading)

                #Write column headings
                print("Writing column headings in the sheet")
                worksheet.write(1, COLUMN+0, "Key",format_heading2)
                worksheet.write(1, COLUMN+1, "Expected Value",format_heading2)
                worksheet.write(1, COLUMN+2, "Actual Value",format_heading2)
                worksheet.write(1, COLUMN+3, "Pass/Fail",format_heading2)
                worksheet.merge_range(0,COLUMN,0,COLUMN+3, tableHeading, format_heading1)

                #Loop to write values in Output Sheet
                for i in range(2,inputSheet.nrows):
                    key = inputSheet.cell(i,col).value
                    #Check to avoid BLANK values
                    if(key!=""):
                        #Write the key
                        expectedValue = inputSheet.cell(i,col+1).value
                        worksheet.write(i, COLUMN+0, key, format_border)
                        worksheet.set_column(i, COLUMN+0, 20)
                        #Check if the key exists in our Dictionary
                        if key in str(dic):
                            TOTAL+= 1
                            #Validate the expected and actual values
                            EXP, ACT, PASS = values.validateValues(key,expectedValue,dic[key])
                            print(str(key)+"\t::\t"+str(EXP)+"\t::\t"+str(ACT))
                            worksheet.write(i, COLUMN+1, EXP, format_border)
                            worksheet.write(i, COLUMN+2, ACT, format_border)
                            if(PASS):
                                worksheet.write(i, COLUMN+3, "PASS", format_pass)
                                PASSED+= 1
                            else:
                                worksheet.write(i, COLUMN+3, "FAIL", format_fail)
                                FAILED+= 1
                        #Check if the value is not applicable
                        elif(key in values.valuesNotApplicable):
                            if(values.isRoundTrip==False):
                                worksheet.write(i, COLUMN+1, "NA", format_border)
                                worksheet.write(i, COLUMN+2, "NA", format_border)
                                worksheet.write(i, COLUMN+3, "NA", format_NA)
                            else:
                                worksheet.write(i, COLUMN+3, "FAIL", format_fail)
                        #Mark it Fail if we don't have the value
                        else:
                            worksheet.write(i, COLUMN+1, "", format_border)
                            worksheet.write(i, COLUMN+2, "", format_border)
                            worksheet.write(i, COLUMN+3, "FAIL", format_fail)
                            BLANK+=1
                            print("Key: "+key+" not found in current event in device logs.")
                print("*"*80)
                break
        COLUMN+= 5
    else:
        print(page+" cannot be resolved!")
        event_not_resolved.append(page)

tmp = {}
getAllTableNames()
with open("AdobeLogs.txt", encoding='utf8', errors='ignore') as f:
    for line in f:
        if "Start --" in line:
            print("Starting collecting the values...")
            tmp.clear()
        if (("key : value" in line) and ("adobe") in line):
            #Read key and value from log
            key = line.split("value ")[1].split(":")[0].replace("\n","")
            if("areadobe" in key):
                key = key.replace("areadobe","adobe")
            value = line.split("value ")[1].split(":",1)[1].replace("\n","")
            tmp[key] = value;
            # print(key+"\t:\t"+value)
        if "-- End" in line:
            print("Ending collecting the values...")
            # print("Buffer is: ")

            #Get the pagename, for track state 
            if "adobe.content.pagename" in str(tmp):
                pageName = tmp['adobe.content.pagename'].replace(":","_")
                print("Tracking type is: State Tracking")

            # Get the pagename, for track action 
            elif "adobe.link.pagename" in str(tmp):
                pageName = tmp['adobe.link.pagename'].replace(":","_")
                print("Tracking type is: Action Tracking")

            print("Page Name: "+pageName)
            print("Dictionary: ")
            print(tmp)
            writeToSheet(pageName,tmp)

writeSummary()
wb_output.close()