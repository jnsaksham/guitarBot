import os
import sys
import time
import numpy as np
import math
from GuitarBotUDP import GuitarBotUDP
from queue import Queue
from threading import Thread
from xarm.wrapper import XArmAPI


def soundToP(db):
    # angle = (5* (10 ** (-5))) * math.exp(0.158 * db)-30  # EQUATION TO INPUT dB and get angle
    vel = 6.3 * db - 408.5
    P = 293073*math.exp(0.03364*vel)/1000 +500
    return P

def soundToAngle(db):
    angle = (5* (10 ** (-5))) * math.exp(0.158 * db) - 30  # EQUATION TO INPUT dB and get angle
    #vel = 6.3 * db - 408.5
    #P = 293073*math.exp(0.03364*vel)/1000
    return angle


def strumBot(trajx,trajy,trajz):
    for i in range(len(trajx)):

        # run command
        start_time = time.time()
        movepose = [trajx[i], trajy[i], trajz[i], -90, 0, -0]
        arm1.set_servo_cartesian(movepose)
        tts = time.time() - start_time
        sleep = 0.002 - tts
        # print(movepose)
        if tts > 0.002:
            sleep = 0
        time.sleep(sleep)


def fifth_poly(q_i, q_f, time):
    # np.linspace
    # time/0.005
    traj_t = np.arange(0, time, 0.002)
    dq_i = 0
    dq_f = 0
    ddq_i = 0
    ddq_f = 0
    a0 = q_i
    a1 = dq_i
    a2 = 0.5 * ddq_i
    a3 = 1 / (2 * time ** 3) * (20 * (q_f - q_i) - (8 * dq_f + 12 * dq_i) * time - (3 * ddq_f - ddq_i) * time ** 2)
    a4 = 1 / (2 * time ** 4) * (30 * (q_i - q_f) + (14 * dq_f + 16 * dq_i) * time + (3 * ddq_f - 2 * ddq_i) * time ** 2)
    a5 = 1 / (2 * time ** 5) * (12 * (q_f - q_i) - (6 * dq_f + 6 * dq_i) * time - (ddq_f - ddq_i) * time ** 2)
    traj_pos = a0 + a1 * traj_t + a2 * traj_t ** 2 + a3 * traj_t ** 3 + a4 * traj_t ** 4 + a5 * traj_t ** 5
    return traj_pos


def setup():
    for a in arms:
        a.set_simulation_robot(on_off=False)
        a.motion_enable(enable=True)
        a.clean_warn()
        a.clean_error()
        a.set_mode(0)
        a.set_state(0)
        a.set_position(*initial_pose, wait=True)


def dynamicStrum(p,angle):
    # d = int(p/100)
    d = 20
    p = int(p)
    for i in range(4):
        guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=p, dgain=d, ipickerpos=angle,
                                      ipickervel=20, ipickeracc=200)  # strum down
        strumq.put(0)
        pickq.get()
        guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=p, dgain=d, ipickerpos=angle,
                                      ipickervel=20, ipickeracc=200)  # strum down

        strumq.put(3)
        pickq.get()

    fingerq.put(1)


# def strumPattern():
#     strumq.put(0)
#     fingerq.get()
#     strumq.put(3)
#     fingerq.get()
#
#     strumq.put(0)
#     fingerq.get()
#
#     strumq.put(1)
#     fingerq.get()
#
#     strumq.put(2)
#     fingerq.get()
#
#     strumq.put(1)
#     fingerq.get()
#
#     strumq.put(0)
#     fingerq.get()
#
#     strumq.put(1)
#     fingerq.get()


def chords(chord):
    if chord == 1: #E chord

        ifretnumber = [1, 2, 2, 1, 1, 1]
        iplaycommand = [1, 2, 2, 2, 1, 1]
        guitarbot_udp.send_msg_left(iplaycommand, ifretnumber)
    if chord == 2:  #A chord

        ifretnumber = [1, 1, 2, 2, 2, 1]
        iplaycommand = [3, 1, 2, 2, 2, 1]
        guitarbot_udp.send_msg_left(iplaycommand, ifretnumber)
    if chord == 3: # D chord
        ifretnumber = [1, 1, 1, 2, 3, 2]
        iplaycommand = [3, 3, 1, 2, 2, 2]
        guitarbot_udp.send_msg_left(iplaycommand, ifretnumber)
    if chord == 0: #Open everything
        ifretnumber = [1, 1, 1, 1, 1, 1]
        iplaycommand = [1, 1, 1, 1, 1, 1]
        guitarbot_udp.send_msg_left(iplaycommand, ifretnumber)

    if chord ==5:  # Cool endging
        ifretnumber = [8, 5, 2, 2, 5, 8]
        iplaycommand = [3, 3, 3, 3, 3, 3]
        guitarbot_udp.send_msg_left(iplaycommand, ifretnumber)


def rightHand(qplay):
    arm1.set_mode(1)
    arm1.set_state(0)
    # input("startagain")
    star = 74
    end = 92
    dp = 10
    data = np.linspace(star, end, dp)
    lastMode = 0

    # time.sleep(5)
    while True:
        strumType = int(qplay.get())
        # guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=5000, dgain=50, ipickerpos=0,
        #                               ipickervel=5, ipickeracc=100)
        if int(strumType) == 0:  # DOWN strum NOISE


            strumBot(dsx, dsy, dsz)
        if int(strumType) == 1:  # UP strum NOISE


            strumBot(dsx, dsy, usz)
        if int(strumType) == 2:  # DOWN strum SILENT

            strumBot(dsx, Ndsy, dsz)
        if int(strumType) == 3:  # UP strum SILENT

            strumBot(dsx, Ndsy, usz)
        pickq.put(1)








initial_pose = [684.3, 287.6, 393.7, -90, 0, -0]
final_pose = [684.3, 287.6, 295.2, -90, 0, -0]#78.5 delta
go_out_d = 12

if __name__ == "__main__":
    UDP_IP = "192.168.1.50"
    UDP_PORT = 1001
    guitarbot_udp = GuitarBotUDP(UDP_IP, UDP_PORT)
    sleeptime = 4
    ROBOT = "xArms"
    PORT = 5004
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))


    strumq = Queue()
    fingerq = Queue()
    pickq = Queue()
    global arm1
    arm1 = XArmAPI('192.168.1.215')

    arms = [arm1]
    totalArms = len(arms)

    setup()
    print("setup")

    timet = 0.25  # second
    timet2 = 0.25

    dsx = fifth_poly(initial_pose[0], final_pose[0], timet)
    dsy = fifth_poly(initial_pose[1], final_pose[1], timet)
    dsz = fifth_poly(initial_pose[2], final_pose[2], timet)
    dslowx = fifth_poly(initial_pose[0], final_pose[0], timet2)
    dslowy = fifth_poly(initial_pose[1], final_pose[1], timet2)
    dslowz = fifth_poly(initial_pose[2], final_pose[2], timet2)
    usx = dslowx[::-1]
    #usy = dslowy[::-1]
    usz = dslowz[::-1]

    ###########ellipse############
    elps_b = 10
    #uelps_b = 5
    strum_range = initial_pose[2] - final_pose[2]
    delps = (-elps_b/(strum_range/2)) * np.sqrt(((strum_range / 2) ** 2 - (usz - final_pose[2] - strum_range / 2) ** 2)) + initial_pose[1]
    #uelps = (uelps_b/(strum_range/2)) * np.sqrt(((strum_range / 2) ** 2 - (usz - final_pose[2] - strum_range / 2) ** 2)) + initial_pose[1]
    Ndsy = delps


    # print(Ndsy)

    global strings
    ofs = 5
    # OLD VALUES strings = [342.7, 333.5, 322.5, 311.9, 302.4, 292.3]# deltas are 9.2, 20.2, 30.8, 40.3,50.4
    strings = [371.6-ofs, 362.4-ofs, 351.4-ofs, 340.8-ofs, 331.3-ofs, 321.4-ofs] # offset because we calibrated maxon at 0

    xArm = Thread(target=rightHand, args=(strumq,))
    xArm.start()


    chords(0)
    input("Press enter to start")


    guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=5000, dgain=20, ipickerpos=-30, ipickervel=5,
                                  ipickeracc=100)

    iplaycommand = [1, 1, 1, 1, 1, 1]
    ifretnumber = [1, 1, 1, 1, 1, 1]
    guitarbot_udp.send_msg_left(iplaycommand, ifretnumber)
    # while True:
    # chords(1)
    #ranget = np.linspace(400, 50000, num=30)
    for i in range(11): #we want 65 to 85
        #pp = int(input("please enter p gain for the guitarbot"))
        #pp = i

        db = 65 + 2*i
        pp = soundToP(db)
        #pp = 5000
        #angle = -30+3*i
        #angle = soundToAngle(db)
        angle = -50
        # ang = int(input("please enter the contact angle for the maxon"))
        print(pp, angle)
        dynamicStrum(pp, int(angle))
        print(fingerq.get())
        # input("start again")
    input("DONE")


    time.sleep(3)
    chords(0)
    chords(5)






    print("done")
    input("DONE!")
