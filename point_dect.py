import sensor, image, time,pyb,lcd
import ustruct
from pyb import UART
from pid import PID
#from pyb import Servo

#pan_servo=Servo(1)
#tilt_servo=Servo(2)
uart = UART(3, 9600,timeout_char=3000)
#pan_servo.calibration(500,2500,500)
#tilt_servo.calibration(500,2500,500)

red_threshold  = (0, 100, 12, 127, -3, 127)

pan_pid = PID(p=0.0732, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
tilt_pid = PID(p=0.06, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
#pan_pid = PID(p=0.07, i=0.03, imax=90)#在线调试使用这个PID
#tilt_pid = PID(p=0.06, i=0.03, imax=90)#在线调试使用这个PID
RED_LED_PIN = 1
BLUE_LED_PIN = 3
lcd.init()
sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # use RGB565.
sensor.set_framesize(sensor.QQVGA2) # use QQVGA for speed.
sensor.skip_frames(10) # Let new settings take affect.
sensor.set_auto_whitebal(False) # turn this off.
sensor.set_auto_gain(False) # 颜色跟踪必须关闭自动增益
clock = time.clock() # Tracks FPS.

def sending_data(cx,cy,cw,ch):
    global uart;
    data = ustruct.pack("<bbhhhhb",      #格式为俩个字符俩个短整型(2字节)
                   0x2C,                      #帧头1
                   0x12,                      #帧头2
                   int (cx), # up sample by 4    #数据26
                   int (cy),
                   1,
                   1,
                   0x5B)
    uart.write(data);   #必须要传入一个字节数组
def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob


while(True):
    pyb.LED(RED_LED_PIN).on()
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot().replace(vflip=1,hmirror=1,transpose=0) # Take a picture and return the image.
    blobs = img.find_blobs([red_threshold])
    if blobs:
        max_blob = find_max(blobs)
        pan_error = max_blob.cx()-img.width()/2
        tilt_error = max_blob.cy()-img.height()/2
        #print("pan_error: ", pan_error
        img.draw_rectangle(max_blob.rect()) # rect
        #img.draw_cross(max_blob.cx(), max_blob.cy()) # cx, cy
        pan_output=pan_pid.get_pid(pan_error,1)/2
        tilt_output=tilt_pid.get_pid(tilt_error,1)
        print("pan_output",pan_output)
        print("tilt_output",tilt_output)
        #pan_servo.angle(pan_servo.angle()+pan_output)
        #tilt_servo.angle(tilt_servo.angle()-tilt_output)
        cx=(int)(pan_output*10)
        cy=(int)(tilt_output*10)
        print(cx)
        print(cy)
        flag = 0
        if max_blob:
            flag = 1
        else :
            flag = 0
        FH=bytearray([0x2C,0x12,cx,cy,flag,1,0x5B])
        uart.write(FH)
        cx=0
        cy=0
