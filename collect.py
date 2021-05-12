import argparse
import cv2
import numpy as np
import os

parser = argparse.ArgumentParser(description="Control Camera to Collect Data (Image/Video)")
parser.add_argument('-type', '--DATA_TYPE', default='image', type=str, help='Collect Data Type: image/video')
parser.add_argument('-id', '--CAMERA_ID', default=0, type=int, help='Camera ID')
parser.add_argument('-path', '--SAVE_PATH', default='./data/', type=str, help='Save Video/Image Path')
parser.add_argument('-name', '--SAVE_NAME', default='test', type=str, help='Save Video/Image Name')
parser.add_argument('-fw','--FRAME_WIDTH', default=1280, type=int, help='Camera Frame Width')
parser.add_argument('-fh','--FRAME_HEIGHT', default=720, type=int, help='Camera Frame Height')
parser.add_argument('-fps','--VIDEO_FPS', default=25, type=int, help='Camera Video Frame per Second')
cfgs = parser.parse_args()

class Flags:                                      # 标定数据类
    def __init__(self):
        self.READ_FAIL_CTR = 0                    # 读取超时计数
        self.frame_id = 0                         # 读入帧数的ID
        self.ready = False                        # 就绪标志位

def main():        
    DATA = np.empty([0,cfgs.FRAME_HEIGHT,cfgs.FRAME_WIDTH,3])                   # 收集的数据 
    flags = Flags()

    cap = cv2.VideoCapture(cfgs.CAMERA_ID)                      # 开启相机
    if not cap.isOpened(): 
        raise Exception("camera {} open failed".format(cfgs.CAMERA_ID))       # 开启失败报错
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfgs.FRAME_WIDTH)                       # 设置相机分辨率
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfgs.FRAME_HEIGHT)

    win1 = "camera_{}_frame".format(cfgs.CAMERA_ID)
    win2 = "press y/n to validate"
    index = 0
    while True:                                                               # 视频输入标定
        key = cv2.waitKey(1)                                                  # 获取键盘输入
        ok, raw_frame = cap.read()                                            # 从相机读入原始帧
        if not ok:
            flags.READ_FAIL_CTR += 1
            if flags.READ_FAIL_CTR >= 20:                                     # 读取视频超时
                raise Exception("camera read failed")
        else:
            flags.READ_FAIL_CTR = 0
            flags.frame_id += 1
        
        if cfgs.DATA_TYPE == 'image':
            if key == 32:                                                     # 按空格键采集该帧图像     
                img = raw_frame.copy()                                        # 暂时存储该帧图像
                flags.ready = True

            if flags.ready:
                cv2.namedWindow(win2, flags = cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
                cv2.imshow(win2, img)
                if key in (ord("y"), ord("Y")):
                    cv2.imwrite(cfgs.SAVE_PATH + 'camera{}_'.format(cfgs.CAMERA_ID) + cfgs.SAVE_NAME + '{}.jpg'.format(len(DATA)),img)
                    DATA = np.append(DATA, [img], axis=0)
                    print(len(DATA))                                           # 显示目前采集数据数量
                    flags.ready = False
                    cv2.destroyWindow(win2)
                elif key in (ord("n"), ord("N")):
                    flags.ready = False
                    cv2.destroyWindow(win2)

        elif cfgs.DATA_TYPE == 'video':

            if key == 32:                                                         # 按空格键开始采集视频   
                if not flags.ready:
                    videoWrite = cv2.VideoWriter(cfgs.SAVE_PATH + 'camera{}_'.format(cfgs.CAMERA_ID) + cfgs.SAVE_NAME + '{}.mp4'.format(index), 
                                         cv2.VideoWriter_fourcc('M','P','4','V'), cfgs.VIDEO_FPS, (cfgs.FRAME_WIDTH,cfgs.FRAME_HEIGHT))
                    flags.ready = True 
                else:
                    flags.ready = False
                    videoWrite.release()
                    cv2.destroyWindow(win1)
                    win1 = "camera_{}_frame".format(cfgs.CAMERA_ID)
                    print(index+1)
                    index += 1 

            if flags.ready:
                win1 = "camera_{}_frame_COLLECTING......".format(cfgs.CAMERA_ID)
                img = cv2.cvtColor(raw_frame, cv2.COLOR_RGB2BGR)
                videoWrite.write(img)

        cv2.namedWindow(win1, flags = cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
        cv2.imshow(win1, raw_frame)    
        if key == 27: break                                                   # ESC退出

    cap.release()
    cv2.destroyAllWindows() 
    
if __name__ == '__main__':
    main()