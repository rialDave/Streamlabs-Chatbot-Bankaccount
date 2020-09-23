#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------
# miscLib Module
#
# Contains some helpful miscellaneous functions
#---------------------------

import os
import time
from datetime import datetime

#---------------------------
#   returns the formatted date of current day 
#---------------------------
def GetCurrentDayFormattedDate():
    currenttimestamp = int(time.time())
    return datetime.fromtimestamp(currenttimestamp).strftime('%Y-%m-%d')

#---------------------------
#   returns the formatted string of an int value with thousands separator
#   param: value (int)
#---------------------------
def FormatThousandsSeparator(value):
    return str('{:,}'.format(int(value)).replace(',','.'))