from GuitarBotUDP import GuitarBotUDP
import csv
import pandas as pd
from sj_utils import rightHand, parser, chords, setup
from queue import Queue
from threading import Thread
from xarm.wrapper import XArmAPI


#fret number is the fret number of the string
#fret command is whether or not its press
# 1: open string (will not move fret)
# 2: press - move to the commanded fret and press

def getChordArray(df, root, chordType):
    array = df[(df['LETTER'] == root) & (df['TYPE'] == chordType)].values[0][3:9]
    fretnum = []
    fretplay = []
    for i in array:
        if i == 0:
            fretplay.append(1)
            fretnum.append(5)
        else:
            fretplay.append(2)
            fretnum.append(int(i))
    return fretnum, fretplay

if __name__ == '__main__':
    UDP_IP = "192.168.1.50"
    UDP_PORT = 1001
    guitar_bot_udp = GuitarBotUDP(UDP_IP, UDP_PORT)
    sleeptime = 2
    ROBOT = "GuitarBot"
    PORT = 5004
    i = -1


    # Strumming arm initialization
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
    ofs = 16.5
    # OLD VALUES strings = [342.7, 333.5, 322.5, 311.9, 302.4, 292.3]# deltas are 9.2, 20.2, 30.8, 40.3,50.4
    strings = [371.6-ofs, 362.4-ofs, 351.4-ofs, 340.8-ofs, 331.3-ofs, 321.4-ofs, initial_pose[2]] # offset because we calibrated maxon at 0
    # stringsy = [279.8, 279.8, 279.8, 280.1, 280.6, 282.0]
    xArm = Thread(target=rightHand, args=(strumq, arm1, initial_pose, go_out_d, guitar_bot_udp, strings, fingerq, final_pose))
    parsing = Thread(target=parser, args=(midiq,))
    
    xArm.start()
    parsing.start()
    # strumq.put(1)
    initial = initial_pose[2]

    fname = 'all_chords_sixstrings.csv'
    while True:
        root = input('A')
        chordType = 'Minor1036'
        df = pd.read_csv(fname)
        fretnum, fretplay = getChordArray(df, root, chordType)

        # fretnum = [1, 1, 1, 1, 1, 1]
        # fretplay = [1, 1, 1, 1, 1, 1]
        
        #fretnum = [2, 2, 2, 2, 1, 2]
        #fretplay = [1, 1, 2, 2, 2, 1]
        
        guitar_bot_udp.send_msg_left(iplaycommand=fretplay, ifretnumber=fretnum)
        strumq.put(1)