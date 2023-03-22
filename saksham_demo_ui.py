import UIGen
import UIParse
import RobotController
import pandas as pd

systemOwner = 'Saksham'
UI_Out_rightHand, UI_Out_leftHand, measure_time, chordsDB = UIGen.UI(systemOwner)
# print (f'UI_out_rh: {UI_Out_rightHand}, UI_out_lh: {UI_Out_leftHand}, measure_time: {measure_time}, chordsDB: {chordsDB}')

numStrings = 6
inversions = 0
if chordsDB == 'Bot':
    df = pd.read_csv(f'all_chords_9frets_v2_{numStrings}str_inv{inversions}.csv')
    # df = pd.read_csv(f'all_chords_9frets_v2.csv')
else:
    df = pd.read_csv(f'humanPlayable_9frets.csv')

ri, initStrum = UIParse.parseright_M(UI_Out_rightHand, measure_time)
li, firstc  = UIParse.parseleft_S(UI_Out_leftHand, df)

print("ri", ri)
print("li", li)

print("firstc: ", firstc)

try:
    # RobotController.main(ri, li, firstc, measure_time)

    # ri = [['', '', '', '', '', '', '', '']]
    # li = [[[[5, 5, 5, 5, 5, 5], [1, 1, 1, 1, 1, 1]], '', '', '']]
    # firstc = [[5, 5, 5, 5, 5, 5], [1, 1, 1, 1, 1, 1]]

    # RobotController.main(ri, li, firstc, measure_time)
    print (f'tried')

except KeyboardInterrupt:
    # ri = [['', '', '', '', '', '', '', '']]
    # li = [[[[5, 5, 5, 5, 5, 5], [1, 1, 1, 1, 1, 1]], '', '', '']]
    # firstc = [[5, 5, 5, 5, 5, 5], [1, 1, 1, 1, 1, 1]]
    
    # RobotController.main(ri, li, firstc, measure_time)
    print ('KeyboardInterrupt')