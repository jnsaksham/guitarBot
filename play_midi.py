from calendar import c
import numpy as np
import os, glob
from midi_parser import playMIDI
import time
from queue import Queue
from threading import Thread
# from xarm.wrapper import XArmAPI
from sj_utils import rightHand, parser, chords, setup
# from GuitarBotUDP import GuitarBotUDP
import mido
from mido import MidiFile

## GuitarBot string map
bot_string_map = {'E': 1, 'A': 2, 'D': 3, 'G': 4, 'B': 5, 'e': 6}
## GuitarBot picking map
bot_picking_map = {'o': 1, 'h': 4, 'g': 5, 'p': 2, 'd': 3}

# def handle_note_odd(fpath, tempoBPM):
#     tempo = mido.bpm2tempo(tempoBPM)
#     mid = MidiFile(fpath)
#     pitchtrack = []
#     timetrack = []
#     veltrack = []
#     track = mid.tracks[0]
#     for msg in track:
#         if msg.type == 'note_on':



if __name__ == '__main__':
    guitar_bot_udp = ""
    strumq = Queue()
    # # Networking
    # UDP_IP = "192.168.1.50"
    # UDP_PORT = 1001
    # guitar_bot_udp = GuitarBotUDP(UDP_IP, UDP_PORT)
    # sleeptime = 4
    # ROBOT = "GuitarBot"
    # PORT = 5004
    # i = -1
    #
    # # Arm calibration
    # initial_pose = [684.3, 246.8, 377.7, -90, 0, -0]  # 287.6-5
    # final_pose = [684.3, 287.6, 299.2, -90, 0, -0]  # 78.5 delta
    #
    # go_out_d = 5
    #
    # chords(0, guitar_bot_udp)
    # strumq = Queue()
    # fingerq = Queue()
    # midiq = Queue()
    # global arm1
    # arm1 = XArmAPI('192.168.1.215')
    #
    # arms = [arm1]
    # totalArms = len(arms)
    #
    # setup(arms, initial_pose)
    # print("setup")
    # input("get ready to start")
    #
    # global strings
    # global stringsy
    # ofs = 16.5
    # # OLD VALUES strings = [342.7, 333.5, 322.5, 311.9, 302.4, 292.3]# deltas are 9.2, 20.2, 30.8, 40.3,50.4
    # strings = [371.6-ofs, 362.4-ofs, 351.4-ofs, 340.8-ofs, 331.3-ofs, 321.4-ofs, initial_pose[2]] # offset because we calibrated maxon at 0
    # stringsy = [279.8, 279.8, 279.8, 280.1, 280.6, 282.0]
    # xArm = Thread(target=rightHand, args=(strumq, arm1, initial_pose, go_out_d, guitar_bot_udp, strings, fingerq, final_pose))
    # parsing = Thread(target=parser, args=(midiq,))
    #
    # xArm.start()
    # parsing.start()
    # strumq.put(1)
    # initial = initial_pose[2]

    dirPath = 'midi'
    fpaths = glob.glob(os.path.join(dirPath, "*.mid"))
    fnum = 3
    fpath = fpaths[fnum]
    print (fpaths)
    print (fpath)
    tempoBPM = 50

    # handle_note_odd(fpath, tempoBPM)
    
    playMIDI(fpath, tempoBPM, bot_picking_map, guitar_bot_udp, strumq)

    # try:
    #     playMIDI(fpath, tempoBPM, bot_picking_map, guitar_bot_udp, strumq)
    #     guitar_bot_udp.send_msg_left([1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1])
    # except KeyboardInterrupt:
    #     guitar_bot_udp.send_msg_left([1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1])