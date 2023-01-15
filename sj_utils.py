import os
import sys
import time
import numpy as np
import math
# from GuitarBotUDP import GuitarBotUDP
from queue import Queue
from threading import Thread
# from xarm.wrapper import XArmAPI
# from rtpmidi import RtpMidi
from pymidi import server


# def third_poly(q_i, q_f, time):
#     traj_t = np.arange(0, time, 0.005)
#     dq_i = 0
#     dq_f = 0
#     a0 = q_i
#     a1 = dq_i
#     a2 = 3 * (q_f - q_i) / (time ** 2)
#     a3 = 2 * (q_i - q_f) / (time ** 3)
#     traj_pos = a0 + a1 * traj_t + a2 * traj_t ** 2 + a3 * traj_t ** 3
#     return traj_pos

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
                    print("YEYE START")
                    key = command.params.key.__int__()
                    velocity = command.params.velocity
                    if velocity == 60:
                        velocity = 0
                    midiq.put([key, velocity])


def soundToP(db):
    pGain = 0.0072 * math.exp(0.1572 * db)
    return pGain


def parser(parse):
    string = [2, 3, 3, 3, 3, 3, 4, 3, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 4]
    # string = [ 1, 2, 3, 4, 5, 6, 6, 5, 4, 3, 2, 1]
    for x in range(5):
        for s in string:
            [key, velocity] = parse.get()
            ifret = [3, 3, 3, 3, 3, 3]
            icommand = [3, 3, 3, 3, 3, 3]

            fret = key - 24
            command = velocity
            pythonSucks = s-1
            ifret[pythonSucks] = fret
            icommand[pythonSucks] = velocity
            print(icommand)
            strumq.put(pythonSucks)
            time.sleep(0.08)
            guitarbot_udp.send_msg_left(icommand, ifret)
            fingerq.get()




def strumBot(arm1, trajx,trajy,trajz):
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


def chords(chord, guitarbot_udp):
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


def setup(arms, initial_pose):
    for a in arms:
        a.set_simulation_robot(on_off=False)
        a.motion_enable(enable=True)
        a.clean_warn()
        a.clean_error()
        a.set_mode(0)
        a.set_state(0)
        a.set_position(*initial_pose, wait=True)


def rightHand(qplay, arm1, initial_pose, go_out_d, guitarbot_udp, strings, fingerq, final_pose):
    qplay.get()
    arm1.set_mode(1)
    arm1.set_state(0)

    star = 74
    end = 92
    dp = 10
    timet = 0.1500 #0.25  # time to go to string
    # timet2 = 0.15 # 0.06 #time to do pick motion

    initial = initial_pose[2]
    initialy = initial_pose[1]
    lastSign = 1
    sign = -1



    # outIn = fifth_poly(initial_pose[1], initial_pose[1]+go_out_d, timet2/2)
    # inOut = outIn[::-1]
    # Ndsy = []
    # Ndsyy = []
    # Ndsy = np.append(Ndsy, outIn)
    # Ndsy = np.append(Ndsy, outIn)
    # Ndsyy = np.append(Ndsyy, inOut)
    # print(Ndsy)
    strumtdown = 0.3
    strumtup = 0.2
    dsx = fifth_poly(initial_pose[0], final_pose[0], strumtdown)
    dsy = fifth_poly(initial_pose[1], final_pose[1], strumtdown)
    dsz = fifth_poly(initial_pose[2], final_pose[2], strumtdown)
    usx = fifth_poly(final_pose[0], initial_pose[0], strumtup)
    usy = fifth_poly(final_pose[1], initial_pose[1], strumtup)
    usz = fifth_poly(final_pose[2], initial_pose[2], strumtup)
    elps_b = 10
    # uelps_b = 5
    strum_range = initial_pose[2] - final_pose[2]
    delps = (-elps_b / (strum_range / 2)) * np.sqrt(
        ((strum_range / 2) ** 2 - (usz - final_pose[2] - strum_range / 2) ** 2)) + initial_pose[1]
    # uelps = (uelps_b/(strum_range/2)) * np.sqrt(((strum_range / 2) ** 2 - (usz - final_pose[2] - strum_range / 2) ** 2)) + initial_pose[1]
    Nusy = delps

    pick_elps_b = int(go_out_d)
    Pick_range = 10
    while True:

        # input("startagain")
        pp = 15000
        dd = 100


        ###old code
        # pos = 10
        # guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=pp, dgain=dd, ipickerpos=-pos,
        #                               ipickervel=5, ipickeracc=100)  # strum down
        pos = -10
        guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=pp, dgain=dd, ipickerpos=pos,
                                      ipickervel=5, ipickeracc=100)  # strum down


        i = 1
        # print("started")

        for repeat in range(100):
            [string, mode] = qplay.get()
            string = int(string)
            mode = int(mode)
            #### If picking do this : ###
            if mode == 0: # we are picking

                ###old code
                # guitarbot_udp.send_msg_picker(ipickercommand=4, bstartpicker=1, pgain=pp, dgain=dd,
                #                               ipickerpos=int(-sign * pos),
                #                               ipickervel=20, ipickeracc=100, isliderpos=-17)
                guitarbot_udp.send_msg_picker(ipickercommand=4, bstartpicker=1, pgain=pp, dgain=dd,
                                              ipickerpos=pos,
                                              ipickervel=20, ipickeracc=100, isliderpos=-17)
                final = strings[string]

                ######TRAJECTORIES FOR STRIGHT UP AND DOWN#####
                dz = fifth_poly(initial, final, timet)
                dx = np.zeros((1, (len(dz)))) + initial_pose[0]
                dy = np.zeros((1, (len(dz)))) + initial_pose[1]

                # guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=pp, dgain=dd, ipickerpos=int(sign*pos),
                #                               ipickervel=5, ipickeracc=100)

                # print("receive")
                # time.sleep(5)
                strumBot(arm1, dx[0], dy[0], dz)
                # strumBot(xio[0], Ndsy, staticz[0])
                ###old code
                # guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pp, dgain=dd, ipickerpos=int(-sign*pos),
                #                               ipickervel=20, ipickeracc=500)

                # print(-sign*pos)
                # sign = -1 * sign
                pos = -pos
                guitarbot_udp.send_msg_picker(ipickercommand=3, bstartpicker=1, pgain=pp, dgain=dd,
                                              ipickerpos=pos,
                                              ipickervel=20, ipickeracc=500)
                print(pos)





            ### STRUMMING ####
            if mode == 1: #We are strumming
                #pos = -pos
                guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=4000, dgain=50, ipickerpos=-20,
                                              ipickervel=20, ipickeracc=200, isliderpos=-7)
                time.sleep(0.06)

                ###old code
                # guitarbot_udp.send_msg_picker(ipickercommand=4, bstartpicker=1, pgain=pp, dgain=dd,
                #                               ipickerpos=int(-pos),
                #                               ipickervel=20, ipickeracc=500, isliderpos=-15)
                guitarbot_udp.send_msg_picker(ipickercommand=4, bstartpicker=1, pgain=pp, dgain=dd,
                                              ipickerpos=pos,
                                              ipickervel=20, ipickeracc=500, isliderpos=-15)
                final = initial_pose[2]
                dz = fifth_poly(initial, final, timet)
                dx = np.zeros((1, (len(dz)))) + initial_pose[0]
                dy = np.zeros((1, (len(dz)))) + initial_pose[1]

                strumBot(arm1, dx[0], dy[0], dz)

                guitarbot_udp.send_msg_picker(ipickercommand=4, bstartpicker=1, pgain=4000, dgain=50, ipickerpos=-20,
                                              ipickervel=20, ipickeracc=500, isliderpos=-7)

                 # strum down
                strumBot(arm1, dsx, dsy, dsz) # DOWN strum NOISE

                #pos = -pos
                guitarbot_udp.send_msg_picker(ipickercommand=4, bstartpicker=1, pgain=pp, dgain=dd,
                                              ipickerpos=pos,
                                              ipickervel=20, ipickeracc=500, isliderpos=-15)
                strumBot(arm1, usx, Nusy, usz) #Up strum SILENT
                sign = -1

            i+=1

            ##### If strumming do this
            initial = float(final)
            # initialy = float(finaly)
            # sign = -1*sign

            fingerq.put(1)

            # print("up")
            # guitarbot_udp.send_msg_picker(ipickercommand=1, bstartpicker=1, pgain=pp, dgain=10, ipickerpos=30, ipickervel=5, ipickeracc=100)