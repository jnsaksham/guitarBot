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
import logging

BPM = 60
MAX_TIME = 1 / 3
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

        # while not is_play:
        #     time.sleep(0.001)
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
        return 0

    def pick_move(self):
        # while not is_play:
        #     time.sleep(0.001)
        pick_queue.get()
        pick_queue.get()
        angle = 4
        self.guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=1200, dgain=100,
                                           ipickerpos=angle,
                                           ipickervel=ipickvel, ipickeracc=ipickeracc, isliderpos=-15)

        return 0

    def traj_generationUser(self, ri):
        # Strum len will change according to different ranges of BPM
        strumlen = .20
        # strumlen = measure_time/(timeattopoftimesig)
        posZ = []
        posY = []
        prev = 0
        if ri[0][0][0] == 'D':
            time.sleep(3)
        else:
            pos_y, pos_z = self.get_traj_p2p(STRUM_PT[0],
                                             STRUM_PT[6], 3)
            posZ = np.append(posZ, pos_z)
            posY = np.append(posY, pos_y)

        for measure in ri:
            for beat in measure:
                if len(beat) != 0:
                    if beat[0] == "D" and beat[1] == "N":
                        pos_y, pos_z = self.get_traj_p2p(STRUM_PT[0],
                                                         STRUM_PT[6], strumlen)
                        posZ = np.append(posZ, pos_z)
                        posY = np.append(posY, pos_y)
                        prev = 6
                        pos_y, pos_z = self.get_traj_p2p(STRUM_PT[prev],
                                                         STRUM_PT[prev], measure_time / 8 - strumlen)
                        posZ = np.append(posZ, pos_z)
                        posY = np.append(posY, pos_y)
                    if beat[0] == "D" and beat[1] == "C":
                        pos_y, pos_z = self.get_traj_p2p(STRUM_PT[0],
                                                             STRUM_PT[6], strumlen)
                        posZ = np.append(posZ, pos_z)
                        posY = np.append(posY, pos_y)
                        pos_y, pos_z = self.get_traj_ellipse(STRUM_PT[6],
                                                         STRUM_PT[0], beat[3] - strumlen)
                        posZ = np.append(posZ, pos_z)
                        posY = np.append(posY, pos_y)
                        prev = 0
                    if beat[0] == "U" and beat[1] == "N":
                        pos_y, pos_z = self.get_traj_p2p(STRUM_PT[6],
                                                         STRUM_PT[0], strumlen)

                        posZ = np.append(posZ, pos_z)
                        posY = np.append(posY, pos_y)
                        prev = 0
                        pos_y, pos_z = self.get_traj_p2p(STRUM_PT[prev],
                                                         STRUM_PT[prev], measure_time / 8 - strumlen)
                        posZ = np.append(posZ, pos_z)
                        posY = np.append(posY, pos_y)
                    if beat[0] == "U" and beat[1] == "C":
                        pos_y, pos_z = self.get_traj_p2p(STRUM_PT[6],
                                                             STRUM_PT[0], strumlen)
                        posZ = np.append(posZ, pos_z)
                        posY = np.append(posY, pos_y)
                        pos_y, pos_z = self.get_traj_ellipse(STRUM_PT[0],
                                                         STRUM_PT[6], beat[3] - strumlen)
                        posZ = np.append(posZ, pos_z)
                        posY = np.append(posY, pos_y)
                        prev = 6
                # Come back to this to reimplement rests
                # else:
                #     pos_y, pos_z = self.get_traj_p2p(STRUM_PT[prev],
                #                                      STRUM_PT[prev], measure_time / 8)  # Time of subdivision
                #     posZ = np.append(posZ, pos_z)
                #     posY = np.append(posY, pos_y)
        # To show plot
        # fig = plt.figure()
        # plt.plot(posZ)
        # plt.show()
        return posY, posZ

    def robot_move(self):
        # while not is_play:
        #     time.sleep(0.001)
        posY, posZ = self.traj_generationUser(right_information)
        # robot_queue.get()
        for i in range(len(posZ)):
            start = time.time()
            new_pose = [INIT_POSE[0], posY[i], posZ[i], INIT_POSE[3], INIT_POSE[4], INIT_POSE[5]]
            self.xarm.set_servo_cartesian(new_pose)
            tts = 0.004 - (time.time() - start)
            if tts > 0:
                time.sleep(tts)


# -----------------------
# To Show Plot
# def main(ri, li, initStrum, mt):
#     global right_information
#     global measure_time
#     global firstc
#     global left_arm
#     left_arm = li
#     right_information = ri
#     firstc = initStrum
#     measure_time = mt
#     grc = GuitarRobotController()
#     # print('testestestest')
#     grc.traj_generationUser(right_information)
# -----------------------

# -----------------------
# To Play
def main(ri, li, initStrum, mt):
    global right_information
    global measure_time
    global firstc
    global left_arm
    left_arm = li
    right_information = ri
    firstc = initStrum
    measure_time = mt
    grc = GuitarRobotController()
    # osc_reader = OSCserver()
    # osc_reader.listen2max()

    # grc.traj_generation(rhythm)
    grc.robot_init()
    time.sleep(1)
    grc.xarm_start()
    time.sleep(1)
    grc.thread_start()

    t_init = time.time()
    endOfSong = t_init + song_length
    # print(endOfSong)
    # print(t_init)
    Pi = 0
    Li = 0
    Ri = 0
    time_stamp = 0
    logging.info("start")
    logging.info(left_hand_timing)
    while time_stamp < song_length * 1000:
        t_i = time.time()
        if time_stamp == left_hand_timing[Li]:
            print("left hand triggered")
            print(time_stamp)
            left_queue.put(Li)
            Li += 1
            Li = Li % len(left_hand_timing)
        if time_stamp == pick_timing[Pi]:
            pick_queue.put(Pi)
            Pi += 1
            Pi = Pi % len(pick_timing)
        if time_stamp == robot_timing:
            robot_queue.put(1)

        time_stamp += 5
        # logging.info(time_stamp)
        time.sleep(0.005 - (time.time() - t_i))

        # print(time_stamp)
    logging.info("end")
    grc.thread_end()


# --------------------

if __name__ == '__main__':
    main()


# PLAN FOR DELTAT:

# 1. Pick a strum speed according to BPM (done, fine-tuning will be done when finished)
# 2. If the next strum doesn't need to auto correct, play strum and pass the remainder of the beat through traj function (done)
#  - SideQuest: Reformat ri so that it knows the next beat. (Done)
#  - Add initial location to ri. (Done)
#  - for all played beats, move 'N' and 'C' so that it reflects if the CURRENT strum needs to change. (Done)
# 3. Otherwise, the current beat strums with set strum speed. Add remainder time to current deltaT. Use remainder time to go to next beat (Done)
# 4. Fix number 3 so it uses a fixed auto correct time then pass remainder of deltaT to the traj function.