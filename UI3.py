import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *
from tkinter.ttk import *
import tkinter.messagebox
import pandas as pd
import numpy as np
import time
import csv
import ast
import matplotlib.pyplot as plt
from typing import NamedTuple
import threading
import logging
from queue import Queue
from GuitarBotUDP import GuitarBotUDP
from xarm.wrapper import XArmAPI
# from pymidi import server
# import GBotData as gbd
# from rtpmidi import RtpMidi
# import pretty_midi
# from pythonosc.dispatcher import Dispatcher
# from pythonosc import osc_server
import logging
from chordPlayback import generate_chord_trajectory
from dict_maps import fret_distances

print("PLEASE READ: NOT ALL CHORDS ARE REPRESENTED, BE WARY OF ERROR MESSAGE 'INDEXING OUT OF BOUNDS")
BPM = 60

UDP_IP = "192.168.1.50"
XARM_IP = '192.168.1.215'
UDP_PORT = 1001
pre_count = 1
STRUM_LEN = 60 / BPM
measure_time = STRUM_LEN * 4
OFFSET = 20.5
STRUM_PT = [372.7, 357.7, 347.7, 337.7, 327.7, 317.7, 292.7]
PICK_PT = [371.6 - OFFSET, 362.4 - OFFSET, 351.4 - OFFSET, 340.8 - OFFSET, 331.3 - OFFSET, 321.4 - OFFSET]
INIT_POSE = [684.3, 246.8, 367.7, -90, 0, 0]
SYNC_RATE = 250
move_time = 0.1
ipickeracc = 200
ipickvel = 50
pgain = 8000
right_information = []
Measure_Timings = STRUM_LEN * 4
fretnum = []
fretplay = []
Rhythm = ""
rhythm = []
onsets = [4, 8, 12, 16, 20, 24]

firstc = []
left_arm = []

repeat = 2
is_play = False

left_queue = Queue()
pick_queue = Queue()
robot_queue = Queue()
# left hand cmd trigger in sec
left_hand_timing = onsets * 1000
HEADER = '/guitar'
chords_dir = "Chords - Chords.csv"

# left_hand_timing[6] -= 150
# left_hand_timing[12] -= 150
# left_hand_timing[18] -= 150
for i in range(7):
    left_hand_timing = np.insert(left_hand_timing, 3 + i * 3 + i, left_hand_timing[2 + i * 3 + i] + 750)

left_hand_timing = np.append(1000, left_hand_timing)
left_hand_timing[-1] += 5000
for i in range(len(left_hand_timing)):
    left_hand_timing[i] = np.ceil(left_hand_timing[i])

print(left_hand_timing)
# right hand pick cmd trigger in sec
pick_timing = np.array([0, 1]) * 1000
robot_timing = 5000
# song length in sec
song_length = 25
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *
from tkinter.ttk import *
import tkinter.messagebox

window = tk.Tk(className=' GuitarBot')
window.geometry("1300x600")

timeFrame = Frame(window)
timeFrame.pack()
tabFrame = Frame(window)
tabFrame.pack()

timeSigs = [
    "2/4",
    "3/4",
    "4/4"
]

beats = {
    "2/4": ["1", "+", "2", "+"],
    "3/4": ["1", "+", "2", "+", "3", "+"],
    "4/4": ["1", "+", "2", "+", "3", "+", "4", "+"]
}

strumOptions = [
    "Custom",
    "Strum1",
    "Strum2",
    "Strum3",
]

strumPatterns = {
    "Strum1": ["D", "U"],
    "Strum2": ["D", ""],
    "Strum3": ["", "U"]
}

timeSelection = StringVar(window)
numMeasures = StringVar(window)
strumSelection = StringVar(window)


# class for the chart module with chords and strumming inputs
# TODO: scroll bar, tab to add measure
class Table:
    def __init__(self, root):
        self.root = root
        self.barCount = 0
        self.lastCol = 0

    def buildTable(self, num_cols, timeSelection, numMeasures):
        # build chords/strum chart
        barCount = 1
        for i in range(4):
            j = 0
            while j <= num_cols:
                if i == 0 and barCount <= int(numMeasures.get()):
                    # MEASURE LABELS
                    labelText = "Bar " + str(barCount)
                    self.cell = Label(self.root, width=4, text=labelText)
                    self.cell.grid(row=i, column=j + int(timeSelection.get()[0]), sticky=W,
                                   columnspan=int(timeSelection.get()[0]) * 2)
                    j += int(timeSelection.get()[0]) * 2
                    barCount += 1
                    continue
                elif i == 1:
                    # BEAT LABELS
                    if j == 0:
                        # add empty label at beginning of row (placeholder to align w/ below rows)
                        self.cell = Label(self.root, width=6, text="")
                        self.cell.grid(row=i, column=j)
                        j += 1
                        continue

                    self.cell = Entry(self.root, width=2, font=('Arial', 16, 'bold'))

                    # add space after last beat of measure
                    if j != 0 and j % len(beats.get(timeSelection.get())) == 0:
                        self.cell.grid(row=i, column=j, padx=(0, 30))
                    else:
                        self.cell.grid(row=i, column=j)

                    self.cell.insert(END, beats.get(timeSelection.get())[(j - 1) % len(beats.get(timeSelection.get()))])
                    self.cell.config(state=DISABLED)
                elif i == 2:
                    # CHORD INPUTS
                    if j == 0:
                        # add "Chords: " label at beginning of row
                        self.cell = Label(self.root, width=6, text="Chords: ")
                        self.cell.grid(row=i, column=j)
                        j += 1
                        continue

                    self.cell = Entry(self.root, width=6, font=('Arial', 16))

                    # add space after last beat of measure
                    if j != 0 and j % len(beats.get(timeSelection.get())) == 0:
                        self.cell.grid(row=i, column=j, sticky=W, columnspan=2, padx=(5, 30))
                    else:
                        self.cell.grid(row=i, column=j, sticky=W, columnspan=2)

                    self.cell.insert(END, "")
                    j += 1
                elif i == 3:
                    # STRUM INPUTS
                    if j == 0:
                        # add "Strum Pattern: " dropdown at beginning of row
                        if strumSelection.get() == "":
                            strumSelection.set("Strum: ")

                        self.cell = OptionMenu(self.root, strumSelection, strumSelection.get(), *strumOptions,
                                               command=self.fillStrumPattern)
                        self.cell.grid(row=i, column=j)
                        j += 1
                        continue

                    self.cell = Entry(self.root, width=2, font=('Arial', 16))

                    # add spacing after last beat of measure
                    if j != 0 and j % len(beats.get(timeSelection.get())) == 0:
                        self.cell.grid(row=i, column=j, padx=(0, 30))
                    else:
                        self.cell.grid(row=i, column=j)

                    self.cell.insert(END, "")
                j += 1

        # update table fields barCount, lastCol
        self.barCount = barCount - 1
        self.lastCol = num_cols

        # place clear button
        self.cell = Button(self.root, text="Clear", width=4, command=self.clearTable)
        self.cell.grid(row=5, column=j - 3, columnspan=2, sticky=W)

    def addMeasure(self):
        # TODO
        print("add measure")

    def removeMeasure(self):
        # delete all components in last measure
        for i in range(int(timeSelection.get()[0]) * 2):
            for e in self.root.grid_slaves(column=self.lastCol - i):
                e.grid_forget()

        # update last column
        self.lastCol = self.lastCol - int(timeSelection.get()[0]) * 2
        self.barCount -= 1

        # put bar label back
        labelText = "Bar " + str(self.barCount)
        self.cell = Label(self.root, width=4, text=labelText)
        self.cell.grid(row=0, column=self.lastCol - int(timeSelection.get()[0]), sticky=W,
                       columnspan=int(timeSelection.get()[0]) * 2)

        # put clear button back
        self.cell = Button(self.root, text="Clear", width=4, command=self.clearTable)
        self.cell.grid(row=5, column=self.lastCol - 2, columnspan=2, sticky=W)

    def editTable(self, num_cols, timeSelection, numMeasures):
        # delete prev rows
        for w in self.root.grid_slaves():
            w.grid_forget()

        self.buildTable(num_cols, timeSelection, numMeasures)

    def clearTable(self):
        count = 0
        for e in reversed(self.root.grid_slaves(row=2)):
            if count != 0:
                e.delete(0, END)
            count += 1

        count = 0
        for e in reversed(self.root.grid_slaves(row=3)):
            if count != 0:
                e.delete(0, END)
            count += 1

        print("table cleared")

    def fillStrumPattern(self, strumSelection):
        count = 0

        for e in reversed(self.root.grid_slaves(row=3)):
            if count != 0:
                e.delete(0, END)
                if strumSelection != "Custom":
                    e.insert(END, strumPatterns.get(strumSelection)[(count + 1) % 2])
            count += 1

    def buildChordStrumData(self, timeSelection):
        leftArm = []
        rightArm = []
        numBeatsPerMeasure = (int)(timeSelection.get()[0])
        bpm = (int)(bpmInput.get())

        # generate left arm data
        currMeasure = []
        count = 0
        for e in reversed(self.root.grid_slaves(row=2)):
            # print("count: ", count)
            # print("value: ", e.get())
            # print("numbeats: ", numBeatsPerMeasure)

            if count != 0:
                currMeasure.append(e.get())
                if count == numBeatsPerMeasure:
                    leftArm.append(currMeasure)
                    currMeasure = []
                    count = 1
                    continue

            count += 1

        # generate right arm data
        currMeasure = []
        count = 0
        duration = (60 / bpm) / (numBeatsPerMeasure * 2)  # calculate duration of each strum
        for e in reversed(self.root.grid_slaves(row=3)):
            # code for appending duration to each strum stroke:
            # if (e.get() != ""):
            #     currMeasure.append((e.get(), duration))
            # else:
            #     currMeasure.append("")

            if count != 0:
                currMeasure.append(e.get())  # delete this line if using above code
                if count == numBeatsPerMeasure * 2:
                    rightArm.append(currMeasure)
                    currMeasure = []
                    count = 1
                    continue

            count += 1

        return (leftArm, rightArm)


tab = Table(tabFrame)


def create_table(timeSelection, numMeasures):
    # set default values if needed
    if len(timeSelection.get()) == 0:
        timeSelection.set("4/4")
    if len(numMeasures.get()) == 0:
        numMeasures.set("1")

    num_cols = int(timeSelection.get()[0]) * (int)(numMeasures.get()) * 2
    tab.buildTable(num_cols, timeSelection, numMeasures)
    print("table created")


def update_table(event):
    print("got these values", timeSelection.get(), numMeasures.get())
    # set default values if needed
    if len(timeSelection.get()) == 0:
        timeSelection.set("4/4")
    if len(numMeasures.get()) == 0:
        numMeasures.set("4")

    num_cols = int(timeSelection.get()[0]) * (int)(numMeasures.get()) * 2
    tab.editTable(num_cols, timeSelection, numMeasures)
    print("table updated")


def fill_strum_pattern(event):
    tab.fillStrumPattern(strumSelection)


def add_measure():
    numMeasures.set(int(numMeasures.get()) + 1)

    # tab.addMeasure()
    update_table(None)

    # update display
    measuresDisplay.config(state="ENABLED")
    measuresDisplay.delete(0, END)
    measuresDisplay.insert(END, numMeasures.get())
    measuresDisplay.config(state=DISABLED)


def remove_measure():
    if int(numMeasures.get()) > 1:
        numMeasures.set(int(numMeasures.get()) - 1)

        tab.removeMeasure()

        # update display
        measuresDisplay.config(state="ENABLED")
        measuresDisplay.delete(0, END)
        measuresDisplay.insert(END, numMeasures.get())
        measuresDisplay.config(state=DISABLED)


# load default table
create_table(timeSelection, numMeasures)

# time signature / bpm / measure dropdowns
timeMenu = OptionMenu(timeFrame, timeSelection, "4/4", *timeSigs, command=update_table)
timeLabel = Label(timeFrame, text="Time Signature: ")
timeLabel.pack(side=LEFT)
timeMenu.pack(side=LEFT)

bpmInput = Entry(timeFrame, width=2, font=('Arial', 16))
bpmInput.insert(END, "60")  # set default bpm
bpmLabel = Label(timeFrame, text="bpm: ")
bpmLabel.pack(side=LEFT)
bpmInput.pack(side=LEFT)

measuresLabel = Label(timeFrame, text="Measures: ")
measuresDisplay = Entry(timeFrame, width=2, font=('Arial', 16))

# set default numMeasures to 1 if not initialized
if numMeasures.get() == "":
    numMeasures.set("1")

measuresDisplay.insert(END, numMeasures.get())
measuresDisplay.config(state=DISABLED)

removeMeasureBtn = Button(timeFrame, text="-", width=1, command=remove_measure)
addMeasureBtn = Button(timeFrame, text="+", width=1, command=add_measure)

measuresLabel.pack(side=LEFT)
removeMeasureBtn.pack(side=LEFT)
measuresDisplay.pack(side=LEFT)
addMeasureBtn.pack(side=LEFT)


def collect_chord_strum_data():
    global is_play
    global left_arm
    global right_information
    global initialStrum
    # build lists with chord/strum info
    lists = tab.buildChordStrumData(timeSelection)
    left_arm = lists[0]
    right_arm = lists[1]
    # commands for getting the below values:
    # time signature -> timeSelection.get()
    # number of measures -> numMeasures.get()
    # bpm -> bpmInput.get()
    # duration of each strum = (60/bpm)/(numBeatsPerMeasure * 2)
    print("left arm: ", left_arm)
    print("right arm: ", right_arm)
    print("left arm: ", left_arm)
    print("right arm: ", right_arm)
    df = pd.read_csv('all_chords_9frets.csv')
    mcount = 0
    firstbfound = False
    firstcfound = False
    mra = 0
    bra = 0
    pmra = 0
    pbra = 0
    for measure in right_arm:
        bra = 0
        for beat in measure:
            if len(beat) != 0:
                if not firstbfound:
                    if beat == "D":
                        right_arm[mra][bra] = [beat, "N", measure_time/8]  # Change strum time here
                    if beat == "U":
                        right_arm[mra][bra] = [beat, "C", measure_time/8]  # Change strum time here
                    firstbfound = True
                    initialStrum = beat
                    pmra = mra
                    pbra = bra

                    bra += 1
                    continue
                if beat == "U":
                    right_arm[mra][bra] = [beat, "N", measure_time/8]  # Change strum time here
                    if right_arm[pmra][pbra][0] == "U":
                        right_arm[mra][bra][1] = "C"
                    pmra -= pmra
                    pmra += mra
                    pbra -= pbra
                    pbra += bra
                    print(pmra, pbra)
                if beat == "D":
                    right_arm[mra][bra] = [beat, "N", measure_time/8]  # Change strum time here
                    if right_arm[pmra][pbra][0] == "D":
                        right_arm[mra][bra][1] = "C"
                    pmra -= pmra
                    pmra += mra
                    pbra -= pbra
                    pbra += bra
                    print(pmra, pbra)
            bra += 1
        mra += 1
    right_information = right_arm
    print("ri", right_information)
    for measure in left_arm:
        bcount = 0
        roots = []
        chordTypes = []
        for chords in measure:
            roots.append(chords.split(' ')[0])
            chordTypes.append(chords.split(' ')[1])
        print (f'roots: {roots}')
        print (f'chordTypes: {chordTypes}')
        ifretplays, iplaycommands = generate_chord_trajectory(roots, chordTypes, df, fret_distances)

        for k, frets in enumerate(ifretplays):
            command = iplaycommands[k]
            if len(chords) != 0:
                left_arm[mcount][bcount] = [frets, command]
                if firstcfound == False:
                    firstc.append(frets)
                    firstc.append(command)
                    firstcfound = True

            # root = roots[0]
            # chordType = chordTypes[0]
            # print ('root: ', root)
            # print ('chordType: ', chordType)
            # if len(chords) != 0:
            #     type = "MAJOR"
            #     key = '♮'
            #     if chords[2:7] == "MAJOR":
            #         type = "MAJOR"
            #     if chords[2:7] == "MINOR":
            #         type = "MINOR"
            #         # print("MINOR CHORD")
            #     if chords[2:8] == "MAJOR7":
            #         type = "MAJOR7"
            #         # print("MAJOR7 CHORD")
            #     if chords[2:8] == "MAJOR9":
            #         type = "MAJOR9"
            #         # print("MAJOR9 CHORD")
            #     if chords[2:8] == "MINOR9":
            #         type = "MINOR9"
            #         # print("MINOR9 CHORD")
            #     if chords[2:6] == "SUS2":
            #         type = "SUS2"
            #         # print("SUS2 CHORD")
            #     if chords[2:6] == "SUS4":
            #         type = "SUS4"
            #         # print("SUS4 CHORD")
            #     if chords[2:8] == "MAJOR6":
            #         type = "MAJOR6"
            #         # print("MAJOR6 CHORD")
            #     if chords[2:7] == "FIFTH":
            #         type = "FIFTH"
            #         # print("FIFTH CHORD")
            #     if chords[2:12] == "DIMINISHED":
            #         type = "DIMINISHED"
            #         # print("DIMINISHED CHORD")
            #     if chords[2:8] == "MINOR7":
            #         type = "MINOR"
            #         # print("MINOR CHORD")
            #     if chords[2:8] == "MINOR6":
            #         type = "MINOR6"
            #         # print("MINOR6 CHORD")
            #     if chords[2:10] == "HALF-DIM":
            #         type = "HALF-DIM"
            #         # print("HALF-DIM CHORD")
            #     if chords[2:10] == "DOMINANT":
            #         type = "DOMINANT"
            #         # print("DOMINANT CHORD")
            #     frets, command, dtraj, utraj = get_chords(chords_dir, chords[0] + key, type)
                               
            print (f'bcount: {bcount}, mcount: {mcount}')
            bcount += 1
        mcount += 1
    # rhythmAppend = getRhythmInfo("FOLKANDCOUNTRY", "1", [0, 6], [6, 0])
    # rhythm.append(rhythmAppend)
    print("left arm: ", left_arm)
    tkinter.messagebox.showinfo("Alert", "Chords sent to GuitarBot.")
    is_play = True
    print("li", left_arm)
    print("measure time ", measure_time)


send = Button(window, text="Send", width=4, command=collect_chord_strum_data)
send.pack(pady=12)


# def getRhythmInfo(Name, Number, dtraj, utraj):
#     directory = "Rhythms.csv"
#     csv_file = csv.reader(open(directory, "r"), delimiter=",")
#     rhythmTraj = []
#     temp = []
#     curr = 0
#     for row in csv_file:
#         if Name == row[0] and Number == row[1]:
#             NumberOfBeats = 1
#             while NumberOfBeats != 0:
#                 count = 0
#                 CurrentBeat = ast.literal_eval(row[3 + count])
#                 # print(CurrentBeat)
#                 for x in CurrentBeat:
#                     print("This is the current beat: ", x)
#                     if len(x) == 1:
#                         temp = [1]
#                         rhythmTraj.append(temp)
#                     if len(x) == 3:
#                         # temp.append(x[0])
#                         # if x[0] == 1:
#                         #     temp.append(utraj[0])
#                         #     temp.append(utraj[1])
#                         # if x[0] == 2:
#                         #     temp.append(dtraj[0])
#                         #     temp.append(dtraj[1])
#                         # Old
#                         temp.append(x[0])
#                         temp.append(x[1])
#                         temp.append(x[2])
#                         rhythmTraj.append(temp)
#                     temp = []
#                     print(rhythmTraj)
#                     curr += 1
#                 curr = 0
#                 NumberOfBeats -= 1
#     rhythm = (rhythmTraj)
#     print(rhythmTraj)
#     return rhythmTraj


def get_chords_costfn(roots, chordTypes, df):
    ifretnums = []
    iplaycommands = []
    return ifretnums, iplaycommands

def get_chords(directory, chord_letter, chord_type):
    df_chords = pd.read_csv(directory)
    for new_x in range(334):
        if df_chords.iloc[new_x][0] == chord_letter:
            if df_chords.iloc[new_x][1] == chord_type:
                x = new_x
                break
    ftraj = False
    dtraj = []
    utraj = []
    try:
        s1 = int(df_chords.iloc[x][3])
        dtraj = [0, 6]
        utraj = [6, 0]
        ftraj = True
    except:
        s1 = -1
    try:
        s2 = int(df_chords.iloc[x][4])
        if ftraj == False:
            dtraj = [1, 6]
            utraj = [6, 1]
            ftraj = True
    except:
        s2 = -1

    try:
        s3 = int(df_chords.iloc[x][5])
        if ftraj == False:
            dtraj = [2, 6]
            utraj = [6, 2]
            ftraj = True
    except:
        s3 = -1
    try:
        s4 = int(df_chords.iloc[x][6])
        if ftraj == False:
            dtraj = [3, 6]
            utraj = [6, 3]
            ftraj = True
    except:
        s4 = -1
    try:
        s5 = int(df_chords.iloc[x][7])
        if ftraj == False:
            dtraj = [4, 6]
            utraj = [6, 4]
            ftraj = True
    except:
        s5 = -1
    try:
        s6 = int(df_chords.iloc[x][8])
        if ftraj == False:
            dtraj = [5, 6]
            utraj = [6, 5]
            ftraj = True
    except:
        s6 = -1
    fret_numbers = [s1, s2, s3, s4, s5, s6]
    fret_play = []
    if fret_numbers[0] == 0:
        fret_numbers[0] += 1
        fret_play.append(1)
    elif fret_numbers[0] == -1:
        fret_numbers[0] = 1
        fret_play.append(3)
    else:
        fret_play.append(2)

    if fret_numbers[1] == 0:
        fret_numbers[1] += 1
        fret_play.append(1)
    elif fret_numbers[1] == -1:
        fret_numbers[1] = 1
        fret_play.append(3)
    else:
        fret_play.append(2)

    if fret_numbers[2] == 0:
        fret_numbers[2] += 1
        fret_play.append(1)
    elif fret_numbers[2] == -1:
        fret_numbers[2] = 1
        fret_play.append(3)
    else:
        fret_play.append(2)

    if fret_numbers[3] == 0:
        fret_numbers[3] += 1
        fret_play.append(1)
    elif fret_numbers[3] == -1:
        fret_numbers[3] = 1
        fret_play.append(3)
    else:
        fret_play.append(2)

    if fret_numbers[4] == 0:
        fret_numbers[4] += 1
        fret_play.append(1)
    elif fret_numbers[4] == -1:
        fret_numbers[4] = 1
        fret_play.append(3)
    else:
        fret_play.append(2)

    if fret_numbers[5] == 0:
        fret_numbers[5] += 1
        fret_play.append(1)
    elif fret_numbers[5] == -1:
        fret_numbers[5] = 1
        fret_play.append(3)
    else:
        fret_play.append(2)
    print(fret_numbers, fret_play)
    print(dtraj, utraj)
    return fret_numbers, fret_play, dtraj, utraj


# send = Button(window, text="Send", width=4, command=send_msg)
# send.pack(pady=12)


window.mainloop()


class GuitarRobotController():
    def __init__(self):
        # self.cobot_controller = CobotController(250, INIT_POSE)
        self.xarm = XArmAPI(XARM_IP)
        self.guitarbot_udp = GuitarBotUDP(UDP_IP, UDP_PORT)
        self.left_thread = threading.Thread(target=self.lefthand_move)
        self.right_thread = threading.Thread(target=self.robot_move)
        self.pick_thread = threading.Thread(target=self.pick_move)

    def robot_init(self):
        self.xarm.set_simulation_robot(on_off=False)
        self.xarm.motion_enable(enable=True)
        self.xarm.clean_warn()
        self.xarm.set_mode(0)
        self.xarm.set_state(0)
        self.xarm.set_position(*INIT_POSE, wait=True)

    def xarm_start(self):
        self.xarm.set_mode(1)
        self.xarm.set_state(0)

    def thread_start(self):
        self.left_thread.start()
        self.right_thread.start()
        self.pick_thread.start()

    def thread_end(self):
        self.left_thread.join()
        self.right_thread.join()
        self.pick_thread.join()

    def _fifth_poly(self, q_i, q_f, time):
        # for picking, try 100 or 150 ms
        traj_t = np.linspace(0, time, int(time * SYNC_RATE))
        dq_i = 0
        dq_f = 0
        ddq_i = 0
        ddq_f = 0
        a0 = q_i
        a1 = dq_i
        a2 = 0.5 * ddq_i
        a3 = 1 / (2 * time ** 3) * (20 * (q_f - q_i) - (8 * dq_f + 12 * dq_i) * time - (3 * ddq_f - ddq_i) * time ** 2)
        a4 = 1 / (2 * time ** 4) * (
                30 * (q_i - q_f) + (14 * dq_f + 16 * dq_i) * time + (3 * ddq_f - 2 * ddq_i) * time ** 2)
        a5 = 1 / (2 * time ** 5) * (12 * (q_f - q_i) - (6 * dq_f + 6 * dq_i) * time - (ddq_f - ddq_i) * time ** 2)
        traj_pos = a0 + a1 * traj_t + a2 * traj_t ** 2 + a3 * traj_t ** 3 + a4 * traj_t ** 4 + a5 * traj_t ** 5
        return traj_pos

    def get_traj_p2p(self, note_i, note_f, move_time):
        pos_z = self._fifth_poly(note_i, note_f, move_time)

        pos_y = np.ones(len(pos_z)) * INIT_POSE[1]
        return pos_y, pos_z

    def get_traj_ellipse(self, note_i, note_f, length):
        elps_b = 10

        pos_z = self._fifth_poly(note_i, note_f, length)
        strum_range = note_i - note_f
        pos_y = -(abs((elps_b / (strum_range / 2)) * np.sqrt(
            abs((strum_range / 2) ** 2 - (pos_z - note_f - strum_range / 2) ** 2)))) + INIT_POSE[1]

        return pos_y, pos_z

    def lefthand_move(self):
        # First Two Measures
        # Figure out timing for each measure
        # Change chord shape at measure shift to inputted chord
        # Read from rhythms db to check muted

        while not is_play:
            time.sleep(0.001)
        self.guitarbot_udp.send_msg_left(iplaycommand=firstc[1], ifretnumber=firstc[0])
        time.sleep(1)
        print("3")
        time.sleep(1)
        print("2")
        time.sleep(1)
        print("1")
        for measure in left_arm:
            for chord in measure:
                if len(chord) == 0:
                    time.sleep(measure_time / 4)
                else:
                    # Change chord
                    #   left_queue.get()
                    self.guitarbot_udp.send_msg_left(iplaycommand=chord[1], ifretnumber=chord[0])
                    time.sleep(measure_time / 4)

        # Pass to tune
        # self.guitarbot_udp.send_msg_left(iplaycommand=[1, 1, 1, 1, 1, 1], ifretnumber=firstc[0])