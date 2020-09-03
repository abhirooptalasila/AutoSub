#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime

def write_to_file(file_handle, infered_text, line_count, limits):
    d = str(datetime.timedelta(seconds=float(limits[0])))
    try:
        from_dur = "0" + str(d.split(".")[0]) + "," + str(d.split(".")[-1][:2])
    except:
        from_dur = "0" + str(d) + "," + "00"
        
    d = str(datetime.timedelta(seconds=float(limits[1])))
    try:
        to_dur = "0" + str(d.split(".")[0]) + "," + str(d.split(".")[-1][:2])
    except:
        to_dur = "0" + str(d) + "," + "00"
        
    file_handle.write(str(line_count) + "\n")
    file_handle.write(from_dur + " --> " + to_dur + "\n")
    file_handle.write(infered_text + "\n\n")