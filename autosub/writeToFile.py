#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime

def write_to_file(file_handle, inferred_text, line_count, limits, vtt, cues):
    """Write the inferred text to SRT file
    Follows a specific format for SRT files

    Args:
        file_handle : SRT file handle
        inferred_text : text to be written
        line_count : subtitle line count 
        limits : starting and ending times for text
    """

    sep = '.' if vtt else ','
    
    d = str(datetime.timedelta(seconds=float(limits[0])))
    try:
        from_dur = "0" + str(d.split(".")[0]) + sep + str(d.split(".")[-1][:2])
    except:
        from_dur = "0" + str(d) + sep + "00"
        
    d = str(datetime.timedelta(seconds=float(limits[1])))
    try:
        to_dur = "0" + str(d.split(".")[0]) + sep + str(d.split(".")[-1][:2])
    except:
        to_dur = "0" + str(d) + sep + "00"

    if not vtt:    
        file_handle.write(str(line_count) + "\n")
        file_handle.write(from_dur + " --> " + to_dur + "\n")
        file_handle.write(inferred_text + "\n\n")
    else:
        file_handle.write(from_dur + " --> " + to_dur + "  align:start position:0%\n")
        file_handle.write(inferred_text + "\n")
        
        words = [f"<c> {x}</c>" for x in inferred_text.split(" ")]
        cue_tags = [f"<{str(datetime.timedelta(seconds=cue))}>" for cue in cues]
        words_cues_mixed = [val for pair in zip(cue_tags, words) for val in pair][1:]
        file_handle.write(''.join(words_cues_mixed) + "\n\n")
