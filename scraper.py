#from email.policy import default
from fileinput import close
from logging import exception
import requests
#from bs4 import BeautifulSoup
import re
import json
from requests.api import request
import os
from os import path
import pymongo
import database
import asyncio

clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

staionInformationURL    = "https://plan.navcanada.ca/weather/api/search/en?include_polygons=true&filter[value]="
wxDataURL               = ""

stationControl = []
stationProducts = {
    "stationPrint" : [],
    "stationSave"  : []

}
#Obtain new staion information to write to local database
def add_to_database(): 

    stationControl.append(0) #set variable and defult to 0
    newStation = ""

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
                
                while True: #validate input
                    try: #enterd a valid input
                        stationControl[0] = int(input("Please pick from list: "))
                        if stationControl[0] < newStationDataLength: #yes the < is correct no suposed to be <=
                            break

                        else:#did not pick form list
                            print("Please pick from list")
                            print()

                    except: #input wasnt a number
                        print("Please enter a number: ")
                        print()



                break #break out of new staion select loop set up loop

            case 1: #see if api returned 1
                break #break out of new staion select loop set up loop

            case 0: #nothing found
                print("No Data Returned By API") #tell user nothing found and ask again

            case _: #i dont know what happend
                print("Unexspected Error") #tell user err and ask again
      

    while True:

        clearConsole()
        print(newStationData[stationControl[0]]["properties"]["displayName"])
        setUpQuestions = ["METAR","TAF","NOTAM"]
        setUpPrintStore = ["Print","Save"]

        #enable staion
        while True: 
            match (str.lower(input("Enable: "))):

                case "yes"|"y":
                    stationControl.append(True)
                    print()

                    #test for number input
                    while True:
                        try: #enterd a number
                            stationControl.append(int(input("Search Radius in NM: ")))
                            break
                        except: #did not enter a number
                            print("Must be a number")
                            print()

                    for op in setUpPrintStore: #loop through setup queston with print then store
                        done = False
                        for idx, x in enumerate(setUpQuestions):#loop through setup queston metar, taf, notam

                                while True:
                                    print()
                                    match str.lower(input(op + " " + setUpQuestions[idx] + ": ")):

                                        case "all":
                                            for _ in range(2):
                                                stationProducts[f"station{op}"].append(True)

                                            done = True
                                            break

                                        case "yes"|"y":
                                            stationProducts[f"station{op}"].append(True)
                                            break
                                            
                                        case "n"|"no":
                                            stationProducts[f"station{op}"].append(False)
                                            break

                                        case _:
                                            print("Invalid Entry Reply With [y/n]")
                                            print()
                            
                                if done == True: break
                                    

                    break #exit enable station loop
                            
                case "n"|"no":
                    for _ in range(3):
                        stationProducts[f"stationPrint"].append(False)
                        stationProducts[f"stationSave"].append(False)
                        stationControl.append(False)
                    
                    stationControl[3] = 0
                    break
                
                case "all":
                    for _ in range(3):
                        stationProducts[f"stationPrint"].append(False)
                        stationProducts[f"stationSave"].append(False)
                        stationControl.append(False)
                
                    #test for number input
                    while True:
                        try: #enterd a number
                            stationControl.append(int(input("Search Radius in NM: ")))
                            break
                        except: #did not enter a number
                            print("Must be a number")
                            print()
                    break 

                case _:
                    print("Invalid Entry Reply With [y/n]")
                    print()
        
     
        asyncio.run(database.add_new_station(stationControl, stationProducts["stationPrint"], stationProducts["stationSave"], newStationData))
        break
   
clearConsole()
add_to_database()