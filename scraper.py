#from email.policy import default
from fileinput import close
import requests
#from bs4 import BeautifulSoup
import re
import json
from requests.api import request
from os import path


staionInformationURL    = "https://plan.navcanada.ca/weather/api/search/en?include_polygons=true&filter[value]="
wxDataURL               = ""

localDatabaseFile = "configure.json"
localDatabase = ""

#Obtain new staion information to write to local database
def add_to_database(): 

    #see if local database file exsists
    if path.isfile(localDatabaseFile) is False:
        print("Local Database Missing!!!")
        return

    desiredNewStaion = 0 #set variable and defult to 0
    newStation = ""

    #new staion template
    newStationJSON = {
            "use"   : {
                "useStation" : False,
                "rapid"     : False,
                "print"     : {
                    "metar"     : False,
                    "taf"       : False,
                    "notam"     : False
                },
                "store"     : {
                    "metar"     : False,
                    "taf"       : False,
                    "notam"     : False
                }
            },
            "type"  : "",
            "coordinates": ["-000.000", "00.000"],
            "hasMetar" : False,
            "hasTaf"   : False,
            "radius"   : 0

        }


    #New staion select loop
    while True:

        print() #print blank line to look nice
        newStation = str.upper(input("Enter ICAO ID: ")) #obtain user input as capitals

        newStationData = requests.get(staionInformationURL+newStation).json()["data"] #Query Nav Canada using user input and save to variable
        newStationDataLength = (len(newStationData)) #get json array length to know how many results were returned
        match newStationDataLength:
        
            case newStationDataLength if newStationDataLength > int(1): #see if API returned multiple items

                #if API returned multiple items see if any are NAVAIDS by seeimg if there is an actual Type field in JSON
                print("Possible matches shown please select item:")
                for newStaionQueryResult in newStationData: #newStaionQueryResult shortend to nsqr
                    
                    nsqrOption = "  " + str(newStationData.index(newStaionQueryResult)) + " " + newStaionQueryResult["properties"]["groupIdentifier"] #set up string prefix

                    if "actualType" in newStaionQueryResult["properties"]: #see if there is an actual type field. If yes use insted of product name (not site)
                        
                        print(nsqrOption + "  - " + newStaionQueryResult["properties"]["actualType"]) #add relevnt data
                        
                    else: #station only has a product name (site)
                        print(nsqrOption + " - " + newStaionQueryResult["properties"]["productName"]) #add relevent data

                print() #add blank line to look nice
                desiredNewStaion = input() #override defult
                break #break out of new staion select loop set up loop

            case 1: #see if api returned 1
                break #break out of new staion select loop set up loop

            case 0: #nothing found
                print("No Data Returned By API") #tell user nothing found and ask again

            case _: #i dont know what happend
                print("Unexspected Error") #tell user err and ask again


    #see if staion is already in database
    f = open(localDatabaseFile)
    localDatabase = json.load(f) #load in local dataBase
    f.close()       

    while True:

        #alert user that staion is already in database
        if newStationData[int(desiredNewStaion)]["properties"]["groupIdentifier"] in localDatabase["stationData"]:
            print("Already in data base.")
            break # exit loop
        
        #begin set up and write changes to jason
        else:
            print()
            setUpQuestions = ["METAR","TAF","NOTAM"]
            setUpPrintStore = ["Print","Store"]
            
            #enable staion
            while True: 
                match (str.lower(input("Enable: "))):

                    case "yes"|"y":
                        newStationJSON["use"]["useStation"] = True
    
                        for op in setUpPrintStore: #loop through setup queston with print then store
                            done = False
                            for idx, x in enumerate(setUpQuestions):#loop through setup queston metar, taf, notam

                                    while True:
                                        print("control: " + str.lower(x))
                                        match str.lower(input(op + " " + setUpQuestions[idx] + ": ")):

                                            case "all":
                                                newStationJSON["use"][str.lower(op)]["metar"] = True
                                                newStationJSON["use"][str.lower(op)]["taf"] = True
                                                newStationJSON["use"][str.lower(op)]["notam"] = True
                                                done = True
                                                break

                                            case "yes"|"y":
                                                newStationJSON["use"][str.lower(op)][str.lower(x)] = True
                                                break
                                                
                                            case "n"|"no":
                                                newStationJSON["use"][str.lower(op)][str.lower(x)] = False
                                                break

                                            case _:
                                                print("Invalid Entry Reply With [y/n]")
                                                print()
                                
                                    if done == True: break
                                        

                        break #exit enable station loop
                                
                    case "n"|"no":
                        newStationJSON["use"]["useStation"] = False
                        break

                    case _:
                        print("Invalid Entry Reply With [y/n]")
                        print()
            
                break
            break
    #begin write
    newStationEntry = {
        str(newStationData[int(desiredNewStaion)]["properties"]["groupIdentifier"]): {}
    } #set up an object with the station ID as key

    try:
        with open(localDatabaseFile, "r+") as f: 
            localDatabase = json.load(f)
            localDatabase["stationData"].update(newStationEntry) #add the staion key
            localDatabase["stationData"][newStationData[int(desiredNewStaion)]["properties"]["groupIdentifier"]].update(newStationJSON) #add station data to new key
            f.seek(0) #curser to start
            json.dump(localDatabase, f, indent = 4) #add back
            f.close()
        print()
        print("New Station Added")
    except:

        print()
        print("DB WRITE ERR OCCURED")
        print()
            
            
    
add_to_database()