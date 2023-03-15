import UIGen
import UIParse
import RobotController
import pandas as pd

UI_Out_rightHand, UI_Out_leftHand, measure_time = UIGen.UI()
# print (f'UI_out_rh: {UI_Out_rightHand}, UI_out_lh: {UI_Out_leftHand}, measure_time: {measure_time}')


numStrings = 6
inversions = 0
df = pd.read_csv(f'all_chords_9frets_v2_{numStrings}str_inv{inversions}.csv')


ri, initStrum = UIParse.parseright_M(UI_Out_rightHand, measure_time)
li, firstc  = UIParse.parseleft_S(UI_Out_leftHand, df)

print("ri", ri)
print("li", li)

print("firstc: ", firstc)

# RobotController.main(ri, li, firstc, measure_time)