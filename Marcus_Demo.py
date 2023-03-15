import UIGen
import UIParse
import RobotController

UI_Out_rightHand, UI_Out_leftHand, measure_time = UIGen.UI()
ri, initStrum = UIParse.parseright_M(UI_Out_rightHand, measure_time)
li, firstc = UIParse.parseleft_M(UI_Out_leftHand)

print("ri", ri)
print("li", li)

print("firstc: ", firstc)

RobotController.main(ri, li, firstc, measure_time)
