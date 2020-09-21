#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from ba_definitions import ROOT_DIR

#---------------------------
#   [Required] Script Information
#   TODO: Some stuff from here should be moved to a GUI settings file later
#---------------------------

ScriptName = "🏦 Bankaccount"
Website = "https://twitch.tv/rialDave/"
Description = "A bank account functionality to 'deposit' chatbot currency to your bank account."
Creator = "rialDave"
Version = "0.1.0-dev"

#---------------------------
#   Global Variables
#   Some stuff from here should be moved to a GUI settings file later
#---------------------------
DataFolder = "data"
DataFilename = "bankdata.json"
DataFilepath = os.path.join(ROOT_DIR, DataFolder, DataFilename)
DataBackupFolder = "archive" # inside data path
DataBackupFilePrefix = "bankdata_bak-"
DataBackupPath = os.path.join(ROOT_DIR, DataFolder, DataBackupFolder)

VariableChannelName = "$channelName"
VariableUser = "$user"
ChannelId = "159000697"
AppClientId = "znnnk0lduw7lsppls5v8kpo9zvfcvd"

# Configuration of keys in json file
JSONVariablesBalance = "balance"
JSONVariablesHighestBalance = "highest_balance"
JSONVariablesHighestBalanceDate = "highest_balance_date"
JSONVariablesLatestDeposit = "latest_deposit"
JSONVariablesLatestDepositDate = "latest_deposit_date"
JSONVariablesLatestWithdrawal = "latest_withdrawal"
JSONVariablesLatestWithdrawalDate = "latest_withdrawal_date"

#---------------------------
#   Command settings and responses (caution: some of the response texts are overwritten later / not refactored yet)
#---------------------------

CommandMain = "!bank"
CommandHelp = "help"
CommandDeposit = "deposit"
CommandWithdraw = "withdraw"
CommandTop10Richest = "top10richest"
CommandTop10RichestAllTime = "top10richestalltime"

ResponseDeposit = "Successfully transferred rialpoints to bank account: "
ResponseWithdraw = "You've successfully transferred rialPoints to wallet: "
ResponseTop10Richest = "Here are the top 10 richest persons of this stream:"
ResponseTop10RichestAlltime = "Oh, the richest of all time? Alright, here are the top 10 richest persons of ALL-TIME:"

ResponsePermissionDeniedMod = "Permission denied: You have to be a Moderator to use this command!"