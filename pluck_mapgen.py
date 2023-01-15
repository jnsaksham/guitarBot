import numpy as np
import time

def strum(strumq, duration):
    """
    Strum all strings while damping the ones note needed
    """
    print ('strum')
    # strumq.put([pluck_indices, 1])
    time.sleep(duration)

def pluck(iplaycommand, strumq, duration):
    print ('pluck')
    string_num = iplaycommand.index(2) + 1
    print (f'pluck string index: {string_num}')
    # strumq.put([string_num, 0])
    time.sleep(duration)

def open(strumq, duration):
    print ('open')
    time.sleep(duration)

def rightHand(iplaycommand, ifretnumber, guitar_bot_udp, strumq, note_duration):
    # Strum - when at least one string is damped
    if 3 in iplaycommand:
        # Position left hand
        #guitar_bot_udp.send_msg_left(iplaycommand, ifretnumber)
        strum(strumq, note_duration)
        
    
    # Plucking and open condition
    elif 1 in iplaycommand:
        # Open
        if len(set(iplaycommand)) == 1:
            open(strumq, note_duration)
        
        # Plucking
        else:
            # Position left hand
            #guitar_bot_udp.send_msg_left(iplaycommand, ifretnumber)
            pluck(iplaycommand, strumq, note_duration)
    
    # Strum when no string is damped
    else:
        # Position left hand
        #guitar_bot_udp.send_msg_left(iplaycommand, ifretnumber)
        strum(strumq, note_duration)
    

def get_clusters(array, stepsize=1):
    return np.split(array, np.where(np.diff(array) != stepsize)[0]+1)

def assign_pluckStyle(clusters, fret_state, bot_picking_map):
    """
    Highest note should be plucked, lowest note should be hammered.
    If lowest note is hammered, then it shouldn't be open.
    If it is open, then try to find another location on the fretboard for it.
    If no other location is available, then ignore the note.
    Input: All the clusters from the string_state (1, 2, 3, 0, 5, 6) -> [1, 2, 3], [5, 6] (Input cluster example)
    Output: 6 dim array with individual pluckstyles encoded from the map to make it bot ready -[4, 4, 4, 1, 2, 2] in this case.
    """
    # Generate a 6 dim array with all open
    array = np.ones(6)*bot_picking_map['d']
    pluckStrings = clusters[-1]-1
    pluckType = 'p'
    array[pluckStrings] = bot_picking_map[pluckType]
    print(f'Pluck adjusted array: {array}')
    hammStrings = np.block(clusters[:-1])-1
    pluckType = 'h'
    array[hammStrings] = bot_picking_map[pluckType]
    print(f'Hamm adjusted array: {array}')
    for k, h in enumerate(hammStrings):
        if fret_state[k] == 0:
            array[k] = bot_picking_map['o']
    return array

def assign_pluckDamp(clusters, fret_state, bot_picking_map):
    """
    Highest note should be plucked, lowest note should be hammered.
    If lowest note is hammered, then it shouldn't be open.
    If it is open, then try to find another location on the fretboard for it.
    If no other location is available, then ignore the note.
    Input: All the clusters from the string_state (1, 2, 3, 0, 5, 6) -> [1, 2, 3], [5, 6] (Input cluster example)
    Output: 6 dim array with individual pluckstyles encoded from the map to make it bot ready -[4, 4, 4, 1, 2, 2] in this case.
    """
    # Generate a 6 dim array with all open
    array = np.ones(6)*bot_picking_map['d']
    indices_strings_played = np.block(clusters)
    array[indices_strings_played] = bot_picking_map['p']
    return array
    

def get_string_state(state, bot_picking_map, fret_state):
    
    # Data structure handling for state
    if len(state) == 1:
        state = state[0]
    
    # Number of strings involved
    strings = np.nonzero(state)[0]
    numStrings = len(strings)
    
    pluck_state = np.ones(6)

    if numStrings == 0:
        # Define pluck state
        pluckType = 'o'
    
    elif numStrings == 1:
        pluckType = 'p'
        pluck_state[strings] = bot_picking_map[pluckType]
        
    elif numStrings == 6:
        pluckType = 'p'
        pluck_state = [bot_picking_map[pluckType] for i in range(6)]

    else:
        # Get clusters
        clusters = get_clusters(strings)
        pluck_state = assign_pluckDamp(clusters, fret_state, bot_picking_map)

        # If multiple clusters, assign p and h
        # if len(clusters) > 1:
            ## Assign pluck/ hamm
            # pluck_state = assign_pluckStyle(clusters, fret_state, bot_picking_map)

            # Damp notes that aren't played and strum all strings.

        #
        # else:
        #     pluckType = 'p'
        #     pluck_state[strings] = bot_picking_map[pluckType]

    return pluck_state
