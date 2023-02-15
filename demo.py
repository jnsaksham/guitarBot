# from GuitarBotUDP import GuitarBotUDP
import csv
import pandas as pd
# from sj_utils import rightHand, parser, chords, setup
# from queue import Queue
# from threading import Thread
# from xarm.wrapper import XArmAPI
from chordPlayback import getSingleChordArray
import time

if __name__ == '__main__':
    # UDP_IP = "192.168.1.50"
    # UDP_PORT = 1001
    # guitar_bot_udp = GuitarBotUDP(UDP_IP, UDP_PORT)
    # sleeptime = 2
    # ROBOT = "GuitarBot"
    # PORT = 5004
    # i = -1


    # # Strumming arm initialization
    # # Arm calibration
    # initial_pose = [684.3, 246.8, 377.7, -90, 0, -0]  # 287.6-5
    # final_pose = [684.3, 287.6, 299.2, -90, 0, -0]  # 78.5 delta
    
    # go_out_d = 5

    # chords(0, guitar_bot_udp)
    # strumq = Queue()
    # fingerq = Queue()
    # midiq = Queue()
    # global arm1
    # arm1 = XArmAPI('192.168.1.215')
    
    # arms = [arm1]
    # totalArms = len(arms)
    
    # setup(arms, initial_pose)
    # print("setup")
    # input("get ready to start")
    
    # global strings
    # global stringsy
    # ofs = 16.5
    # # OLD VALUES strings = [342.7, 333.5, 322.5, 311.9, 302.4, 292.3]# deltas are 9.2, 20.2, 30.8, 40.3,50.4
    # strings = [371.6-ofs, 362.4-ofs, 351.4-ofs, 340.8-ofs, 331.3-ofs, 321.4-ofs, initial_pose[2]] # offset because we calibrated maxon at 0
    # # stringsy = [279.8, 279.8, 279.8, 280.1, 280.6, 282.0]
    # xArm = Thread(target=rightHand, args=(strumq, arm1, initial_pose, go_out_d, guitar_bot_udp, strings, fingerq, final_pose))
    # parsing = Thread(target=parser, args=(midiq,))
    
    # xArm.start()
    # parsing.start()
    # # strumq.put(1)
    # initial = initial_pose[2]

    sleeptime = 1
    demoType = input("Enter the type of  demo you want to run: S for single chord, P for progression: ")
    ftype = input('Type B for bot and H for human: ')
    if ftype == 'H':
        fname = 'humanPlayable_9frets.csv'
    else:
        fname = 'all_chords_9frets.csv'
    df = pd.read_csv(fname)
    if demoType == 'S':
        try:
            while True:
                root = input("Enter root: ")
                chordType = input('Enter chordType: ')
                for i in range(4):
                    fretnum, fretplay = getSingleChordArray(df, root, chordType)
                    print (f'fretnum: {fretnum}, fretplay: {fretplay}')
                    # guitar_bot_udp.send_msg_left(iplaycommand=fretplay, ifretnumber=fretnum)
                    # strumq.put(1)
                    time.sleep(sleeptime)
        except KeyboardInterrupt:
            fretnum = [1, 1, 1, 1, 1, 1]
            fretplay = [1, 1, 1, 1, 1, 1]
            # guitar_bot_udp.send_msg_left(iplaycommand=fretplay, ifretnumber=fretnum)
    
    elif demoType == 'P':
        try:
            numChords = int(input('Enter the number of chords you want: '))
            numLoops = 10
            while True:
                counts = 4
                roots = []
                chordTypes = []
                for i in range(numChords):
                    root = input(f"Enter root of chord {i}: ")
                    chordType = input('Enter chordType: ')
                    roots.append(root)
                    chordTypes.append(chordType)
                for i in range(numLoops):
                    for i in range(numChords):
                        root = roots[i]
                        chordType = chordTypes[i]
                        fretnum, fretplay = getSingleChordArray(df, root, chordType)
                        print (f'fretnum: {fretnum}, fretplay: {fretplay}')
                        for j in range(counts):
                            # guitar_bot_udp.send_msg_left(iplaycommand=fretplay, ifretnumber=fretnum)
                            # strumq.put(1)
                            time.sleep(sleeptime)

        except KeyboardInterrupt:
            fretnum = [1, 1, 1, 1, 1, 1]
            fretplay = [1, 1, 1, 1, 1, 1]
            # guitar_bot_udp.send_msg_left(iplaycommand=fretplay, ifretnumber=fretnum)