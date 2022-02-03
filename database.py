from array import array
from distutils.log import error
from logging import exception
import selectors
import motor.motor_asyncio
import asyncio
from os import path
import json     

conn_str = ""
# set a 5-second connection timeout



try: 
    f = open("arrguments.json")
    arrguments = json.load(f)
    conn_str = arrguments["dataBase"]

except:
    print("FAILED TO LOAD ARGUMENTS")

finally:
    f.close()

client = motor.motor_asyncio.AsyncIOMotorClient(conn_str, serverSelectionTimeoutMS=5000)

#write new station to database
async def add_new_station(control, printReport, save, raw): #see note 1

    
    #see what type we are writing SITE/NAVAID/FIR/CAMERA/UNKOWEN
    match raw[control[0]]["properties"]["productName"]:
        #write as site
        case "SITE":
            #try to write to mongoDB
            try:
                #JSON to be written  
                client.WX["Station Information"].insert_one({
                    "_id": raw[control[0]]["properties"]["groupIdentifier"],
                    "product": raw[control[0]]["properties"]["productName"],
                    "type": raw[control[0]]["properties"]["groupType"],
                    "use": {
                        "useStation": control[1],
                        "rapid": control[2],
                        "print": {
                            "metar": printReport[0],
                            "taf": printReport[1],
                            "notam": printReport[2]
                        },
                        "store": {
                            "metar": save[0],
                            "taf": save[1],
                            "notam": save[2]
                        }
                    },
                    "coordinates": raw[control[0]]["geometry"]["coordinates"],
                    "radius": control[3]
                    
                    })

            #failed to write to mongo :(
            except Exception:
                print("DATABASE WRITE ERROR")

        case "FIR":
            #try to write to mongoDB
            try:
                #JSON to be written
               
                client.WX["Station Information"].insert_one({
                    "_id": raw[control[0]]["properties"]["groupIdentifier"],
                    "product": raw[control[0]]["properties"]["productName"],
                    "type": raw[control[0]]["geometry"]["groupType"],
                    "use": {
                        "useStation": control[1],
                        "rapid": control[2],
                        "print": {
                            "sigmet" : False,
                            "airmet" : False,
                            "pirep" : False,
                            "sigmet" : False,
                            "BCVFR" : False,
                            "FDL": {
                                "YVR": True
                            },
                            "FDH": {
                                "YVR": True
                            }
                        },
                        "store": {
                            "print": {
                                "sigmet" : False,
                                "airmet" : False,
                                "pirep" : False,
                                "sigmet" : False,
                                "BCVFR" : False,
                                "FDL": {
                                    "YVR": True
                                },
                                "FDH": {
                                    "YVR": True
                                },
                            }
                        }
                    },

                    "coordinates": raw[control[0]]["geometry"]["coordinates"],
                    "radius": control[3]
                    
                    })
            

            #failed to write to mongo :(
            except Exception as e:
                print("DATABASE WRITE ERROR")
                print(e)


# NOTE 1: arrguments are
#
#     selector: what the user chose during select if there were multiple stations by defult 
#     this goes to 1 (note in future the number shown to user may not be the one repersentitive 
#     of item chosen)
#
#     data: reffers to the options the user needs to input to write
#
#     raw: refers to the raw data supplied by NAV Canada