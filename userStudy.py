import UIGen
import UIParse
import RobotController
import pandas as pd


# Setup
systemOwner = 'Saksham'
bpm = 90
measure_time = 4*60/bpm  # seconds. measure_time = 4*60/BPM
chordsDB = 'Bot'    # Bot, Human
optimizer = ''      # 'random', 'viterbi', 'greedy'

## Rhythms
UI_Out_rightHand = [['D', 'U', 'D', '', 'D', 'U', 'D', ''], ['D', 'U', 'D', '', 'D', 'U', 'D', ''], ['D', 'U', 'D', '', 'D', 'U', 'D', ''], ['D', 'U', 'D', '', 'D', 'U', 'D', '']]
### Test1
# UI_Out_rightHand = [['D', '', 'D', '', 'D', '', 'D', ''], ['D', '', 'D', '', 'D', '', 'D', ''], ['D', '', 'D', '', 'D', '', 'D', ''], ['D', '', 'D', '', 'D', '', 'D', '']]
### Test2
# UI_Out_rightHand = [['D', 'U', 'D', '', 'D', 'U', 'D', ''], ['D', 'U', 'D', '', 'D', 'U', 'D', ''], ['D', 'U', 'D', '', 'D', 'U', 'D', ''], ['D', 'U', 'D', '', 'D', 'U', 'D', '']]
### Test3
# UI_Out_rightHand = [['D', '', 'D', '', 'D', '', '', ''], ['D', '', 'D', '', 'D', '', '', ''], ['D', '', 'D', '', 'D', '', '', ''], ['D', '', 'D', '', 'D', '', '', '']]
### Test4
# UI_Out_rightHand = [['D', 'U', 'D', 'U', 'D', 'U', 'D', 'U'], ['D', 'U', 'D', 'U', 'D', 'U', 'D', 'U'], ['D', 'U', 'D', 'U', 'D', 'U', 'D', 'U'], ['D', 'U', 'D', 'U', 'D', 'U', 'D', 'U']]

## Test chords
UI_Out_leftHand = [['C M', 'C M', 'C M', 'C M'], ['A m', 'A m', 'A m', 'A m'], ['F M', 'F M', 'F M', 'F M'], ['G M', 'G M', 'G M', 'G M']]
### Test1
# UI_Out_leftHand = [['C M', 'C M', 'C M', 'C M'], ['A m', 'A m', 'A m', 'A m'], ['F M', 'F M', 'F M', 'F M'], ['G M', 'G M', 'G M', 'G M']]
### Test2
# UI_Out_leftHand = [['B m7', 'B m7', 'B m7', 'B m7'], ['G M', 'G M', 'G M', 'G M'], ['A M', 'A M', 'A M', 'A M'], ['B m7', 'B m7', 'B m7', 'B m7']]
### Test3
# UI_Out_leftHand = [['F M', 'F M', 'F M', 'F M'], ['G M', 'G M', 'G M', 'G M'], ['E m', 'E m', 'E m', 'E m'], ['A m', 'A m', 'A m', 'A m']]
### Test4
# UI_Out_leftHand = [['C M7', 'C M7', 'C M7', 'C M7'],['F M7', 'F M7', 'F M7', 'F M7'] ,['C M7', 'C M7', 'C M7', 'C M7'] , ['G M', 'G M', 'G M', 'G M']]
print (f'UI_out_rh: {UI_Out_rightHand}, UI_out_lh: {UI_Out_leftHand}, measure_time: {measure_time}, chordsDB: {chordsDB}, optimizer: {optimizer}')

numStrings = 6
inversions = 0
if chordsDB == 'Bot':
    df = pd.read_csv(f'all_chords_9frets_v2_{numStrings}str_inv{inversions}.csv')
    # df = pd.read_csv(f'all_chords_9frets_v2.csv')
else:
    df = pd.read_csv(f'humanPlayable_9frets_sixstrings.csv')

ri, initStrum = UIParse.parseright_M(UI_Out_rightHand, measure_time)
li, firstc  = UIParse.parseleft_S(UI_Out_leftHand, df, optimizer, chordsDB)

print (li)
print (ri)

try:    
    RobotController.main(ri, li, firstc, measure_time)

    ri = [['', '', '', '', '', '', '', '']]
    li = [[[[5, 5, 5, 5, 5, 5], [1, 1, 1, 1, 1, 1]], '', '', '']]
    firstc = [[5, 5, 5, 5, 5, 5], [1, 1, 1, 1, 1, 1]]

    RobotController.main(ri, li, firstc, measure_time)

except KeyboardInterrupt:
    ri = [['', '', '', '', '', '', '', '']]
    li = [[[[5, 5, 5, 5, 5, 5], [1, 1, 1, 1, 1, 1]], '', '', '']]
    firstc = [[5, 5, 5, 5, 5, 5], [1, 1, 1, 1, 1, 1]]
    
    RobotController.main(ri, li, firstc, measure_time)
    print ('KeyboardInterrupt')