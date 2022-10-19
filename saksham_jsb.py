import numpy as np
import os, glob, time
from jsb_parser import load_npz, play_chorale
from GuitarBotUDP import GuitarBotUDP
from queue import Queue
from threading import Thread
from xarm.wrapper import XArmAPI
from sj_utils import rightHand, parser, chords, setup
from notes import playnote
from rtpmidi import RtpMidi
from pymidi import server

## GuitarBot string map
bot_string_map = {'E': 1, 'A': 2, 'D': 3, 'G': 4, 'B': 5, 'e': 6}

## GuitarBot picking map
bot_picking_map = {'o': 1, 'h': 4, 'g': 5, 'p': 2, 'd': 3}

## Define note mappings
# note_dict = {'C2': 36, 'C#2': 37, 'D2': 38, 'D#2': 39, 'E2': 40, 'F2': 41, 'F#2': 42, 'G2': 43, 'G#2': 44, 'A2': 45, 'A#2': 46, 'B2': 47, 'C3': 48, 'C#3': 49, 'D3': 50, 'D#3': 51, 'E3': 52, 'F3': 53, 'F#3': 54, 'G3': 55, 'G#3': 56, 'A3': 57, 'A#3': 58, 'B3': 59,'C4': 60, 'C#4': 61, 'D4': 62, 'D#4': 63, 'E4': 64, 'F4': 65, 'F#4': 66, 'G4': 67, 'G#4': 68, 'A4': 69, 'A#4': 70, 'B4': 71, 'C5': 72, 'C#5': 73, 'D5': 74, 'D#5': 75, 'E5': 76, 'F5': 77, 'F#5': 78, 'G5': 79, 'G#5': 80, 'A5': 81, 'A#5': 82, 'B5': 83}
# note_dict = {v: k for k, v in note_dict.items()}

fpath = 'Jsb16thSeparated.npz'
setType = 'valid'
idx = 7
chorales = load_npz(fpath)
chorale = chorales[setType][idx]
tempo = 50

if __name__ == "__main__":
    # guitar_bot_udp = 'xx'
    UDP_IP = "192.168.1.50"
    UDP_PORT = 1001
    guitar_bot_udp = GuitarBotUDP(UDP_IP, UDP_PORT)
    sleeptime = 4
    ROBOT = "GuitarBot"
    PORT = 5004
    i = -1

    # Arm calibration
    initial_pose = [684.3, 246.8, 377.7, -90, 0, -0]  # 287.6-5
    final_pose = [684.3, 287.6, 299.2, -90, 0, -0]  # 78.5 delta

    go_out_d = 5

    chords(0, guitar_bot_udp)
    strumq = Queue()
    fingerq = Queue()
    midiq = Queue()
    global arm1
    arm1 = XArmAPI('192.168.1.215')

    arms = [arm1]
    totalArms = len(arms)

    setup(arms, initial_pose)
    print("setup")
    input("get ready to start")

    global strings
    global stringsy
    ofs = 18.5
    # OLD VALUES strings = [342.7, 333.5, 322.5, 311.9, 302.4, 292.3]# deltas are 9.2, 20.2, 30.8, 40.3,50.4
    strings = [371.6 - ofs, 362.4 - ofs, 351.4 - ofs, 340.8 - ofs, 331.3 - ofs,
               321.4 - ofs]  # offset because we calibrated maxon at 0
    stringsy = [279.8, 279.8, 279.8, 280.1, 280.6, 282.0]
    xArm = Thread(target=rightHand, args=(strumq, arm1, initial_pose, go_out_d, guitar_bot_udp, strings, fingerq))
    parsing = Thread(target=parser, args=(midiq,))

    xArm.start()
    parsing.start()
    strumq.put(1)
    initial = initial_pose[2]

    try:
        input("start arpeggiator")
        time.sleep(4)
        play_chorale(chorale, tempo, bot_string_map, bot_picking_map, guitar_bot_udp, strumq)

        # time.sleep(3)
        # for x in range(6):
        #     for y in range(5):
        #         string = x
        #         # else:
        #         strumq.put(string)
        #         time.sleep(0.3)
            # input("next")
            # initial = strings[string]
        #input("sequence")

    except KeyboardInterrupt:
        guitar_bot_udp.send_msg_left([1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1])

    guitar_bot_udp.send_msg_left([1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1])