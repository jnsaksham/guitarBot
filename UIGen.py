
import tkinter.messagebox
import pandas as pd
import numpy as np
import csv
import ast
from queue import Queue
import logging
import UIParse

print("PLEASE READ: NOT ALL CHORDS ARE REPRESENTED, BE WARY OF ERROR MESSAGE 'INDEXING OUT OF BOUNDS")
BPM = 60
MAX_TIME = 1/3
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

def UI():
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

                        self.cell.insert(END,
                                         beats.get(timeSelection.get())[(j - 1) % len(beats.get(timeSelection.get()))])
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
        global left_arm
        global right_arm
        global mtime
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
        BeatsPerMinute = int(bpmInput.get())
        strumlen = 60 / BeatsPerMinute
        mtime = strumlen * 4
        tkinter.messagebox.showinfo("Alert", "Chords sent to GuitarBot.")

    send = Button(window, text="Send", width=4, command=collect_chord_strum_data)
    send.pack(pady=12)

    window.mainloop()

    return right_arm, left_arm, mtime

