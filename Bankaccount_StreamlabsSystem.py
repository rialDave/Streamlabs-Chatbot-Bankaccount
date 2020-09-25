#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------
#   Import Libraries
#---------------------------
import os
import sys
import json
import time
import collections
from pprint import pprint
from shutil import copyfile

import clr
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

# Load own modules
sys.path.append(os.path.dirname(__file__)) # point at current folder for classes / references
sys.path.append(os.path.join(os.path.dirname(__file__), "ba_lib")) # point at lib folder for classes / references

from ba_definitions import ROOT_DIR
import ba_config
import miscLib


#---------------------------
#   [Required] Script Information (must be existing in this main file)
#   TODO: Some stuff from here should be moved to a GUI settings file later
#---------------------------
ScriptName = ba_config.ScriptName
Website = ba_config.Website
Description = ba_config.Description
Creator = ba_config.Creator
Version = ba_config.Version

#############################################
# START: Generic Chatbot functions
#############################################

#---------------------------
#   [Required] Initialize Data (Only called on load of script)
#---------------------------
def Init():
    # generate data and archive directory if they don't exist (uses DataBackupPath because it includes the data path)
    if (False == os.path.isdir(ba_config.DataBackupPath)):
        os.makedirs(ba_config.DataBackupPath)

    # Creates an empty data file if it doesn't exist
    if (False == os.path.isfile(ba_config.DataFilepath)):
        # generate empty data file and save it
        data = {}
        with open(ba_config.DataFilepath, 'w') as f:
            json.dump(data, f, indent=4)
    
    Log("Bankaccount script successfully initialized")

    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):
    response = "Error, try '!bank help' for more information"

    # bankaccount command called
    if (data.IsChatMessage() and data.GetParam(0).lower() == ba_config.CommandMain):
        userPoints = int(Parent.GetPoints(data.User))
        userAccountbalance = GetBalance(data.User)
        
        bankCommand = data.GetParam(1).lower()
        pointsAmount = data.GetParam(2)

        if (bankCommand == ba_config.CommandHelp):
            Parent.SendStreamMessage(ba_config.ResponseHelp)
            return

        if (bankCommand == ba_config.CommandBalance):
            Log(GetBalance(data.User))
            if ("error" != GetBalance(data.User)):
                response = "Your current bank account balance: " + miscLib.FormatThousandsSeparator(GetBalance(data.User)) + " " + ba_config.CurrencyName
            else:
                response = "Error: you don't have a bank account yet!"

            Parent.SendStreamMessage(response)
            return

        if (bankCommand == ba_config.CommandTop10Richest):
            Parent.SendStreamMessage(ba_config.ResponseTop10Richest + GetTop10RichestWithData(False))
            return    

        if (bankCommand == ba_config.CommandTop10RichestAllTime):
            Parent.SendStreamMessage(ba_config.ResponseTop10Richest + GetTop10RichestWithData(True))
            return

        if (pointsAmount and not pointsAmount.isdigit()):
            Parent.SendStreamMessage("Error: Only numbers you silly!")
            return

        if (bankCommand == ba_config.CommandDeposit):
            if (pointsAmount > 0):
                # check if user has enough points to deposit
                if (int(userPoints) >= int(pointsAmount)):
                    UpdateDatafile(bankCommand, data)
                    response = "Successfully deposited " + pointsAmount + " " + ba_config.CurrencyName + "! | Current cash: " + miscLib.FormatThousandsSeparator(Parent.GetPoints(data.User)) + " " + ba_config.CurrencyName + " | Current balance: " + miscLib.FormatThousandsSeparator(GetBalance(data.User)) + " " + ba_config.CurrencyName
                else:
                    response = "Error: not enough cash to deposit " + miscLib.FormatThousandsSeparator(pointsAmount) + " " + ba_config.CurrencyName + "! | Current cash: " + str(userPoints)

        if (bankCommand == ba_config.CommandWithdraw):
            if (int(pointsAmount) > 0):
                # check if user has enough account balance for withdrawal
                if (userAccountbalance >= int(pointsAmount)):
                    UpdateDatafile(bankCommand, data)
                    response = "Successfully withdrawn " + miscLib.FormatThousandsSeparator(pointsAmount) + " " + ba_config.CurrencyName + "! | Current cash: " + miscLib.FormatThousandsSeparator(Parent.GetPoints(data.User)) + " " + ba_config.CurrencyName + " | Current balance: " + miscLib.FormatThousandsSeparator(GetBalance(data.User)) + " " + ba_config.CurrencyName
                else:
                    response = "Insufficient account balance for withdrawal of " + miscLib.FormatThousandsSeparator(pointsAmount) + " " + ba_config.CurrencyName + "! | Current balance: " + miscLib.FormatThousandsSeparator(userAccountbalance) + " " + ba_config.CurrencyName

        Parent.SendStreamMessage(response) # Send your message to chat

    return

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#   Runs basically every millisecond since the script is activated^^
#---------------------------
def Tick():
    return

#---------------------------
#   [Optional] Parse method (Allows you to create your own custom $parameters)
#   Here's where the magic happens, all the strings are sent and processed through this function
#   
#   Parent.FUNCTION allows to use functions of the Chatbot and other outside APIs (see: https://github.com/AnkhHeart/Streamlabs-Chatbot-Python-Boilerplate/wiki/Parent)
#
# ORIGINAL DEF: def Parse(parseString, userid, username, targetid, targetname, message):
#---------------------------
def Parse(parseString, command, data):
    # after every necessary variable was processed: return the whole parseString, if it wasn't already
    return parseString

#---------------------------
#   [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
#---------------------------
def ReloadSettings(jsonData):
    return

#---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
#---------------------------
def Unload():
    Log("Script unloaded")
    BackupDataFile()
    return

#---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
#---------------------------
def ScriptToggled(state):
    return

#############################################
# END: Generic Chatbot functions
#############################################

#---------------------------
#   Log helper (For logging into Script Logs of the Chatbot)
#   Note that you need to pass the "Parent" object and use the normal "Parent.Log" function if you want to log something inside of a module
#---------------------------
def Log(message):
    Parent.Log(ScriptName, str(message))
    return

#---------------------------
#   UpdateDataFile: Function for modfiying the file which contains the data, see data/bankdata.json
#   returns the parseString for parse(Function)
#---------------------------
def UpdateDatafile(command, data):
    currentday = miscLib.GetCurrentDayFormattedDate()
    success = False

    userId = str(data.User)
    userName = str(data.UserName.lower())
    pointsAmount = int(data.GetParam(2))

    # this loads the data of file bankdata.json into variable "data"
    with open(ba_config.DataFilepath, 'r') as f:
        data = json.load(f)

        # check if the given data.user exists in data. -> user doesnt exist yet, create array of the default user data, which will be stored in bankdata.json
        if (True == IsNewUser(userName)):
            data[userName] = {}
            data[userName][ba_config.JSONVariablesBalance] = 0
            data[userName][ba_config.JSONVariablesLatestDeposit] = 0
            data[userName][ba_config.JSONVariablesLatestDepositDate] = ""
            data[userName][ba_config.JSONVariablesLatestWithdrawal] = 0
            data[userName][ba_config.JSONVariablesLatestWithdrawalDate] = ""
            data[userName][ba_config.JSONVariablesHighestBalance] = 0
            data[userName][ba_config.JSONVariablesHighestBalanceDate] = ""

        if (command == ba_config.CommandDeposit):
            data[userName][ba_config.JSONVariablesBalance] += pointsAmount
            data[userName][ba_config.JSONVariablesLatestDeposit] = pointsAmount
            data[userName][ba_config.JSONVariablesLatestDepositDate] = currentday
            Parent.RemovePoints(userId,userName,pointsAmount)
            success = True
            
            # if new balance is higher than old balance
            if (int(data[userName][ba_config.JSONVariablesBalance]) > int(data[userName][ba_config.JSONVariablesHighestBalance])):
                data[userName][ba_config.JSONVariablesHighestBalance] = data[userName][ba_config.JSONVariablesBalance]
                data[userName][ba_config.JSONVariablesHighestBalanceDate] = currentday

        if (command == ba_config.CommandWithdraw):
            data[userName][ba_config.JSONVariablesBalance] -= pointsAmount
            data[userName][ba_config.JSONVariablesLatestWithdrawal] = pointsAmount
            data[userName][ba_config.JSONVariablesLatestWithdrawalDate] = currentday
            Parent.AddPoints(userId,userName,pointsAmount)
            success = True

    # after everything was modified and updated, we need to write the stuff from our "data" variable to the bankdata.json file 
    os.remove(ba_config.DataFilepath)
    with open(ba_config.DataFilepath, 'w') as f:
        json.dump(data, f, indent=4)

    return success

#---------------------------
#   returns the string formatted balance
#---------------------------
def GetBalance(username):

    with open(ba_config.DataFilepath, 'r') as f:
        data = json.load(f)

        if str(username.lower()) not in data:
            balanceResponse = "error"
        else:
            balanceResponse = data[username.lower()][ba_config.JSONVariablesBalance]

    return balanceResponse

#---------------------------
#   IsNewUser
#---------------------------
def IsNewUser(username):
    # this loads the data of file bankdata.json into variable "data"
    with open(ba_config.DataFilepath, 'r') as f:
        data = json.load(f)

        if str(username.lower()) not in data:
            return True
        else:
            return False

#---------------------------
# BackupDataFile
#
# Backups the data file in the "archive" folder with current date and timestamp for ease of use
#---------------------------
def BackupDataFile():
    if (True == os.path.isfile(ba_config.DataFilepath)):

        if (False == os.path.isdir(ba_config.DataBackupPath)):
            os.makedirs(ba_config.DataBackupPath)

        dstFilename = ba_config.DataBackupFilePrefix + str(miscLib.GetCurrentDayFormattedDate()) + "_" + str(int(time.time())) + ".json"
        dstFilepath = os.path.join(ba_config.DataBackupPath, dstFilename)
        copyfile(ba_config.DataFilepath, dstFilepath)
    
    return

#---------------------------
# GetTop10Richest
#
# Returns a list of all top 10 richest users sorted by balance to be iterated
# Param: "alltime = TRUE" returns the alltime top10richest (highest balance ever)
#---------------------------
def GetTop10Richest(alltime):
    with open(ba_config.DataFilepath, 'r') as f:
        data = json.load(f)

        # build sortableDict with user and balances like "user: balance"
        sortableRichestDict = {}
        for user in data:
            # different list if alltime = True
            if (True == alltime):
                sortableRichestDict[user] = data[user][ba_config.JSONVariablesHighestBalance]
            else:
                sortableRichestDict[user] = data[user][ba_config.JSONVariablesBalance]

    # sort it by checkins and put it in a list of max 10 items
    sortedRichestList = sorted(sortableRichestDict.items(), key=lambda x: x[1], reverse=True)
    sortedRichestDict = collections.OrderedDict(sortedRichestList)
    
    # only the first 10 items
    return sortedRichestDict.keys()[:10]

#---------------------------
# GetTop10RichestWithData
#
# Returns a complete string of all top 10 richest users sorted by balance and with data
# Param: bool "alltime = TRUE" returns the alltime top10richest (highest balance ever)
#---------------------------
def GetTop10RichestWithData(alltime):
    top10richest = GetTop10Richest(alltime)

    top10RichestWithData = ""

    # get data for response
    with open(ba_config.DataFilepath, 'r') as f:
        data = json.load(f)

        position = 0
        for richestUser in top10richest:
            position += 1
            top10RichestWithData += "#" + str(position) + " "
            top10RichestWithData += str(richestUser)
            top10RichestWithData += " ("
            # different output, when alltime = True
            if (True == alltime):
                top10RichestWithData += miscLib.FormatThousandsSeparator(data[richestUser][ba_config.JSONVariablesHighestBalance]) + " " + ba_config.CurrencyName + " at " + str(data[richestUser][ba_config.JSONVariablesHighestBalanceDate])
            else:
                top10RichestWithData += miscLib.FormatThousandsSeparator(data[richestUser][ba_config.JSONVariablesBalance]) + " " + ba_config.CurrencyName

            top10RichestWithData += ")"
            
            # only display dash below last position
            if (position < 10):
                 top10RichestWithData += " - "

    return top10RichestWithData
