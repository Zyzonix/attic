#!/usr/bin/python3
#
# written by @author ZyzonixDev
# published by ZyzonixDevelopments 
# -
# date      | 07/08/2021
# python-v  | 3.8.3
# -
# file      | sqliteManipulator.py
# project   | sqliteManipulator
# project-v | 0.2 
#

import sqlite3 

table = "air_quality"
dbLoc = "/home/dietzmpe/dev/2021-08-02.db"
column = "timestamp"

connection = sqlite3.connect(dbLoc)
cursor = connection.cursor()
# row counter 
rowL = 1
# loop through rows
for row in list(cursor.execute("SELECT " + column + " FROM " + table)):
    formattedRow = list(row)
    print(len(formattedRow))
    for element in formattedRow:
        elementArray = element.split("_")
        splitElementArray = elementArray[0].split("-")
        splitElementArray[2] = "03"
        finalString = "'" + splitElementArray[0] + "-" + splitElementArray[1] + "-" +  splitElementArray[2]  + "_" +   elementArray[1] + "'" 
        print(finalString)
        cmd = str("UPDATE " + table + " SET timestamp=" + finalString + " WHERE ROWID=" + str(rowL))
        print(cmd)
        cursor.execute(cmd)
    rowL += 1
connection.commit()
connection.close()
