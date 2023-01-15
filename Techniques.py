import os
import sys
import time
import numpy as np
import math
from GuitarBotUDP import GuitarBotUDP
from queue import Queue
from threading import Thread
from xarm.wrapper import XArmAPI
from rtpmidi import RtpMidi
from pymidi import server



class MyHandler(server.Handler):

    def on_peer_connected(self, peer):
        # Handler for peer connected
        print('Peer connected: {}'.format(peer))

    def on_peer_disconnected(self, peer):
        # Handler for peer disconnected
        print('Peer disconnected: {}'.format(peer))

    def on_midi_commands(self, peer, command_list):
        # Handler for midi msgs
        for command in command_list:
            chn = command.channel
            if chn == 1:  # this means its channel 14!!!!!
                if command.command == 'note_on':
                    # print("YEYE START")

                    fingerq.put(1)




def soundToP(db):
    pGain = 0.0072 * math.exp(0.1572 * db)
    return pGain


def modeSwitch(mode):
    timetoSwitch = 0.1
    arm1.set_position(*initial_pose, wait=True)
    toPick = fifth_poly(initial_pose[1], initial_pose[1]-5, timetoSwitch)
    toStrum = toPick[::-1]
    x = [initial_pose[0]] * len(toPick)
    z = [initial_pose[2]] * len(toPick)
    if mode == 0:  # Strumming
        strumBot(x, toStrum, z)
    if mode == 1:  # Picking
        strumBot(x, toPick, z)


def strumBot(trajx,trajy,trajz):
    # print("go")
    # start
    track_time = time.time()
    initial_time = time.time()
    for i in range(len(trajx)):

        # run command
        movepose = [trajx[i], trajy[i], trajz[i], -90, 0, -0]
        arm1.set_servo_cartesian(movepose)
        while track_time < initial_time + RESOLUTION:
            track_time = time.time()
            time.sleep(0.0001)

        # print(f"time elapsed: {track_time} sec")
        initial_time += RESOLUTION


def fifth_poly(q_i, q_f, time):
    # np.linspace
    # time/0.005
    traj_t = np.arange(0, time, RESOLUTION)
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


def strumPattern():

    strumq.put(0)
    fingerq.get()


    strumq.put(3)
    fingerq.get()

    strumq.put(0)
    fingerq.get()

    strumq.put(1)
    fingerq.get()

    strumq.put(2)
    fingerq.get()

    strumq.put(1)
    fingerq.get()

    strumq.put(0)
    fingerq.get()

    strumq.put(1)
    fingerq.get()


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
    if chord ==5:  # Cool ending
        ifretnumber = [8, 5, 2, 2, 5, 8]
        iplaycommand = [3, 3, 3, 3, 3, 3]
        guitarbot_udp.send_msg_left(iplaycommand, ifretnumber)


def picking(qplay):
    fingerq.get()
    for i in range(4):
        strumPattern()


#     star = 74
#     end = 92
#     dp = 10
#     timet = 0.6  # time to go to string
#     timet2 = 0.3 #time to go in
#     initial = initial_pose[2]
#     outIn = fifth_poly(initial_pose[1], initial_pose[1]+go_out_d, timet2/2)
#     inOut = outIn[::-1]
#     pNdsy = []
#     pNdsy = np.append(pNdsy, outIn)
#     pNdsy = np.append(pNdsy, inOut)
#
#     # time.sleep(5)
#     while True:
#
#         # input("startagain")
#         pp = 5000
#         dd = 50
#
#         pos = -10
#         guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=pp, dgain=dd, ipickerpos=pos,
#                                       ipickervel=5, ipickeracc=100)  # strum down
#         i = 1
#         # print("started")
#         for repeat in range(100):
#             string = int(qplay.get())
#             final = strings[string]
#             # strum_range = abs(final - initial)
#             dz = fifth_poly(initial, final, timet)
#             dx = np.zeros((1,(len(dz)))) + initial_pose[0]
#             dy = np.zeros((1,(len(dz)))) + initial_pose[1]
#
#             lastsection = len(outIn)
#             # print(lastsection)
#             ypick = dy[0][0:(len(dy[0])-lastsection)]
#             ypick= np.append(ypick, outIn)
#             # print(ypick)
#             print(len(dx[0]),len(ypick))
#             print("receive")
#             time.sleep(5)
#             strumBot(dx[0], ypick, dz)
#
#             # newp = (-1)**i
#             # npos = pos*newp
#             guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=pp, dgain=dd, ipickerpos=-pos, ipickervel = 2, ipickeracc=100)
#             # strum down
#
#
#             lst = np.zeros((1,(len(pNdsy)))) + initial_pose[0]
#             lst2 = np.zeros((1,(len(pNdsy)))) + final
#             # print(lst, lst2)
#             strumBot(lst[0], pNdsy, lst2[0])
#             guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=pp, dgain=dd, ipickerpos=pos,
#                                           ipickervel=2, ipickeracc=100)
#             i += 1
#             initial = strings[string]


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
        init = time.time()
        # guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=5000, dgain=50, ipickerpos=0,
        #                               ipickervel=5, ipickeracc=100)
        if int(strumType) == 0:  # DOWN strum NOISE

            guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=4500, dgain=50, ipickerpos=-10,
                                          ipickervel=20, ipickeracc=200)  # strum down
            strumBot(dsx, dsy, dsz)
        if int(strumType) == 1:  # UP strum NOISE

            guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=4500, dgain=50, ipickerpos=10,
                                          ipickervel=20, ipickeracc=200)  # strum down
            strumBot(dsx, dsy, usz)
        if int(strumType) == 2:  # DOWN strum SILENT

            guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=4500, dgain=50, ipickerpos=-10,
                                          ipickervel=20, ipickeracc=200)  # strum down
            strumBot(dsx, Ndsy, dsz)
        if int(strumType) == 3:  # UP strum SILENT

            guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=4500, dgain=50, ipickerpos=10,
                                          ipickervel=20, ipickeracc=200)  # strum down
            strumBot(dsx, Ndsy, usz)
        fin = time.time()
        print(fin-init)

        # fingerq.put(1)








initial_pose = [684.3, 287.6, 393.7, -90, 0, -0]
final_pose = [684.3, 287.6, 295.2, -90, 0, -0]#78.5 delta
go_out_d = 12

if __name__ == "__main__":
    ROBOT = "GuitarBot"
    PORT = 5004
    UDP_IP = "192.168.1.50"
    UDP_PORT = 1001
    guitarbot_udp = GuitarBotUDP(UDP_IP, UDP_PORT)
    sleeptime = 4
    global RESOLUTION
    RESOLUTION = 0.004

    strumq = Queue()
    fingerq = Queue()
    pickq = Queue()
    global arm1
    arm1 = XArmAPI('192.168.1.215')

    arms = [arm1]
    totalArms = len(arms)

    setup()
    print("setup")

    timet = 0.2500 # 25  # second
    timet2 = 0.2500

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

    pickthread = Thread(target=picking, args=(pickq,))
    pickthread.start()
    # for x in range(12):
    #     string = int(input("desired string"))


    iplaycommand = [1, 1, 1, 1, 1, 1]
    ifretnumber = [1, 1, 1, 1, 1, 1]
    guitarbot_udp.send_msg_left(iplaycommand, ifretnumber)
    # ifretnumber = [1, 1, 1, 1, 1, 1]
    # iplaycommand = [3, 3, 3, 3, 3, 3]
    # guitarbot_udp.send_msg_left(iplaycommand, ifretnumber)
    # chords(0)
    input("Press enter to start")
    rtp_midi = RtpMidi(ROBOT, MyHandler(), PORT)
    print("test")
    rtp_midi.run()



    # guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=3000, dgain=30, ipickerpos=pos, ipickervel=5,
    #                               ipickeracc=100)

    iplaycommand = [1, 1, 1, 1, 1, 1]
    ifretnumber = [1, 1, 1, 1, 1, 1]
    # guitarbot_udp.send_msg_left(iplaycommand, ifretnumber)
    press = [2, 2, 2, 2, 2, 2]
    Hammeron = 4
    nothing = [1,1,1,1,1,1]

    # for i in range(6):
    #
    #     send = nothing.copy()
    #     send[i] = Hammeron
    #     ifretnumber = [2, 2, 2, 2, 2, 2]
    #     print(send)
    #     guitarbot_udp.send_msg_left(send, ifretnumber)
    #     input("again?")
    #
    #
    #
    #     time.sleep(2)
    # iplaycommand = [1, 1, 1, 1, 1, 1]
    # ifretnumber = [1, 1, 1, 1, 1, 1]
    # guitarbot_udp.send_msg_left(iplaycommand, ifretnumber)









    # time.sleep(3)
    # chords(0)
    # chords(5)






    print("done")
    input("DONE!")
    # for x in range(5):
    #     #
    #     iplaycommand = [1, 2, 2, 1, 2, 1]
    #     ifretnumber = [4, 3, 2, 4, 1, 4]
    #
    #     #
    #     strumq.put(1)
    #
    #     fingerq.get()
    #     # time.sleep(0.2)
    #     # guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=8000, dgain=80, ipickerpos=-10, ipickervel=5, ipickeracc=100)
    #     # time.sleep(sleeptime)
    #     ifretnumber = [4, 4, 2, 2, 2, 4]
    #     iplaycommand = [1, 1, 2, 2, 2, 1]
    #     guitarbot_udp.send_msg_left(iplaycommand, ifretnumber)
    #     strumq.put(1)
    #     fingerq.get()
    #     bstartplay = [0, 0, 0, 0, 0, 0]
    # ifretnumber = [5, 4, 3, 3, 4, 5]
    # iplaycommand = [3, 3, 3, 3, 3, 3]
    # guitarbot_udp.send_msg_left(iplaycommand, ifretnumber)
        # time.sleep(0.2)
        # guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=8000, dgain=80, ipickerpos=10, ipickervel=5,
        #                             ipickeracc=100)
        # time.sleep(sleeptime)