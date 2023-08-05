from machine import Pin
import sensor, image, time
import pyb
from pid import PID
import ustruct
from pyb import UART
#import seekfree, pyb

# 初始化TFT180屏幕
#lcd = seekfree.LCD180(3)

# 初始化摄像头
sensor.reset()
sensor.set_pixformat(sensor.RGB565) # 设置图像色彩格式为RGB565格式
sensor.set_framesize(sensor.VGA)  # 设置图像大小为160*120
sensor.set_auto_whitebal(True)      # 设置自动白平衡
sensor.set_brightness(3000)         # 设置亮度为3000
sensor.skip_frames(time = 20)       # 跳过帧
sensor.set_windowing(170,193,240,250)
clock = time.clock()
corner = 0
uart = UART(3, 9600,timeout_char=3000)
i = 0
red_threshold  = (6, 100, 5, 127, 0, 127)

pan_pid = PID(p=0.05, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
tilt_pid = PID(p=0.014, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID

def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob


while(True):
    clock.tick()
    img = sensor.snapshot().lens_corr(0.7).replace(vflip=1,hmirror=1,transpose=0).binary([(0, 35, -39, 64, -8, 23)])
# -----矩形框部分-----
    # 在图像中寻找矩形
    for r in img.find_rects(threshold = 10000):
        # 判断矩形边长是否符合要求
        if r.w() > 20 and r.h() > 20 :
            # 在屏幕上框出矩形
            # 获取矩形角点位置
            corner = r.corners()
            # 在屏幕上圈出矩形角点
            sorted(corner,key=(lambda x:x[1]))
            #img.draw_cross(corner[0][0], corner[0][1])
            #img.draw_cross(corner[1][0], corner[1][1])
            #img.draw_cross(corner[2][0], corner[2][1])
            #img.draw_cross(corner[3][0], corner[3][1])


        # 打印四个角点坐标, 角点1的数组是corner[0], 坐标就是(corner[0][0],corner[0][1])
        # 角点检测输出的角点排序每次不一定一致，矩形左上的角点有可能是corner0,1,2,3其中一个（几乎为逆时针）
            corner1_str = f"corner1 = ({corner[0][0]},{corner[0][1]})"
            corner2_str = f"corner2 = ({corner[1][0]},{corner[1][1]})"
            corner3_str = f"corner3 = ({corner[2][0]},{corner[2][1]})"
            corner4_str = f"corner4 = ({corner[3][0]},{corner[3][1]})"
            print(corner1_str + "\n" + corner2_str + "\n" + corner3_str + "\n" + corner4_str)
            while(i<4):
                img = sensor.snapshot().lens_corr(0.7).replace(vflip=1,hmirror=1,transpose=0)
                blobs = img.find_blobs([red_threshold])
                if blobs:
                    max_blob = find_max(blobs)
                    pan_error = max_blob.cx()-corner[3-i][0]
                    tilt_error = max_blob.cy()-corner[3-i][1]
                    #img.draw_rectangle(max_blob.rect()) # rect
                    img.draw_cross(max_blob.cx(), max_blob.cy()) # cx, cy
                    pan_output=pan_pid.get_pid(pan_error,1)/2
                    tilt_output=tilt_pid.get_pid(tilt_error,1)
                    print("pan_output",pan_output)
                    print("tilt_output",tilt_output)
                    #pan_servo.angle(pan_servo.angle()+pan_output)
                    #tilt_servo.angle(tilt_servo.angle()-tilt_output)
                    cx=(int)(-pan_output*10)
                    cy=(int)(-tilt_output*10)
                    print(cx)
                    print(cy)
                    FH=bytearray([0x2C,0x12,cx,cy,1,1,0x5B])
                    uart.write(FH)
                    if cx == 0 and cy == 0 :
                        i=i+1
                        if i == 4 :
                            i = 0
                            break
                    cx=0
                    cy=0


        # 按照逆时针遍历，以左下角点为入口
        # 0,3,2,1返回坐标
            #FH = bytearray([0x2C,0x12,corner[3][0], corner[3][1],corner[2][0],corner[2][1],corner[1][0],corner[1][1],corner[0][0],corner[0][1],0x5B])
            #uart.write(FH)
