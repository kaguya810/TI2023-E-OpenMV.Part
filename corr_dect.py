from machine import Pin
import sensor, image, time
import pyb
import ustruct
from pyb import UART
#import seekfree, pyb

# 初始化TFT180屏幕
#lcd = seekfree.LCD180(3)

# 初始化摄像头
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE) # 设置图像色彩格式为RGB565格式
sensor.set_framesize(sensor.QVGA)  # 设置图像大小为160*120
sensor.set_auto_whitebal(True)      # 设置自动白平衡
sensor.set_brightness(3000)         # 设置亮度为3000
sensor.skip_frames(time = 20)       # 跳过帧
sensor.set_windowing(44,55,200,170)
clock = time.clock()
corner = 0
uart = UART(3, 9600,timeout_char=3000)

while(True):
    clock.tick()
    img = sensor.snapshot().lens_corr(0.7).replace(vflip=1,hmirror=1,transpose=0).binary([(0, 50, -11, 20, -14, 20)])

# -----矩形框部分-----
    # 在图像中寻找矩形
    for r in img.find_rects(threshold = 10000):
        # 判断矩形边长是否符合要求
        if r.w() > 50 and r.h() > 50 and r.w() < 100 and r.h() < 100:
            # 在屏幕上框出矩形
            img.draw_rectangle(r.rect(), color = (255, 0, 0), scale = 4)
            # 获取矩形角点位置
            corner = r.corners()
            # 在屏幕上圈出矩形角点
            sorted(corner,key=(lambda x:x[1]))
            img.draw_circle(corner[0][0], corner[0][1], 5, color = (0, 0, 255), thickness = 2, fill = False)
            img.draw_circle(corner[1][0], corner[1][1], 5, color = (0, 0, 255), thickness = 2, fill = False)
            img.draw_circle(corner[2][0], corner[2][1], 5, color = (0, 0, 255), thickness = 2, fill = False)
            img.draw_circle(corner[3][0], corner[3][1], 5, color = (0, 0, 255), thickness = 2, fill = False)


        # 打印四个角点坐标, 角点1的数组是corner[0], 坐标就是(corner[0][0],corner[0][1])
        # 角点检测输出的角点排序每次不一定一致，矩形左上的角点有可能是corner0,1,2,3其中一个（几乎为逆时针）
            corner1_str = f"corner1 = ({corner[0][0]},{corner[0][1]})"
            corner2_str = f"corner2 = ({corner[1][0]},{corner[1][1]})"
            corner3_str = f"corner3 = ({corner[2][0]},{corner[2][1]})"
            corner4_str = f"corner4 = ({corner[3][0]},{corner[3][1]})"
            print(corner1_str + "\n" + corner2_str + "\n" + corner3_str + "\n" + corner4_str)




        # 按照逆时针遍历，以左下角点为入口
        # 0,3,2,1返回坐标
            FH = bytearray([0x2C,0x12,corner[3][0], corner[3][1],corner[2][0],corner[2][1],corner[1][0],corner[1][1],corner[0][0],corner[0][1],0x5B])
            uart.write(FH)
