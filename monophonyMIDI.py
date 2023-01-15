from calendar import c
import numpy as np
import os, glob
from mido import MidiFile
import mido
from midi_parser import genOnsetOffsetmasks, playMonophony, genWrapper
from GuitarBotUDP import GuitarBotUDP

def play(fpath, tempoBPM, guitar_bot_udp):
    timetrack, pitchtrack, veltrack = genWrapper(fpath, tempoBPM)
    onset_mask, offset_mask = genOnsetOffsetmasks(timetrack, pitchtrack, veltrack)
    print (f'onset mask: {onset_mask}')
    playMonophony(onset_mask, pitchtrack, veltrack, guitar_bot_udp, bot_picking_map, bot_string_map)


## GuitarBot string map
bot_string_map = {'E': 1, 'A': 2, 'D': 3, 'G': 4, 'B': 5, 'e': 6}

## GuitarBot picking map
bot_picking_map = {'o': 1, 'h': 4, 'g': 5, 'p': 2, 'd': 3}

if __name__ == '__main__':
    UDP_IP = "192.168.1.50"
    UDP_PORT = 1001
    guitar_bot_udp = GuitarBotUDP(UDP_IP, UDP_PORT)
    sleeptime = 4
    ROBOT = "xArms"
    PORT = 5004
    i = -1
    dirPath = 'midi'
    fpaths = glob.glob(os.path.join(dirPath, "*.mid"))
    # print (fpaths)
    fnum = 3
    fpath = fpaths[fnum]
    print (fpath)
    tempoBPM = 80

    play(fpath, tempoBPM, guitar_bot_udp="")