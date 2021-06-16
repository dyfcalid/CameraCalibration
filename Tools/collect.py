import argparse
import cv2
import numpy as np
import os

# 在这里修改各参数值
parser = argparse.ArgumentParser(description="Control Camera to Collect Data (Image/Video)")
parser.add_argument('-type', '--DATA_TYPE', default='image', type=str, help='Collect Data Type: image/video')
parser.add_argument('-id', '--CAMERA_ID', default=0, type=int, help='Camera ID')
parser.add_argument('-path', '--SAVE_PATH', default='./data/', type=str, help='Save Video/Image Path')
parser.add_argument('-name', '--SAVE_NAME', default='test', type=str, help='Save Video/Image Name')
parser.add_argument('-fw','--FRAME_WIDTH', default=1280, type=int, help='Camera Frame Width')
parser.add_argument('-fh','--FRAME_HEIGHT', default=720, type=int, help='Camera Frame Height')
parser.add_argument('-fps','--VIDEO_FPS', default=25, type=int, help='Camera Video Frame per Second')
args = parser.parse_args()

def main():        
    if not os.path.exists(args.SAVE_PATH):                                      # 检查路径
        raise Exception("save path not exist")  
    DATA = np.empty([0,args.FRAME_HEIGHT,args.FRAME_WIDTH,3])                   # 已收集的数据 
    flag = False                                                                # 采集图像标志

    cap = cv2.VideoCapture(args.CAMERA_ID)                                      # 开启相机
    if not cap.isOpened(): 
        raise Exception("camera {} open failed".format(args.CAMERA_ID))         # 开启失败报错
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.FRAME_WIDTH)                         # 设置相机分辨率
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, args.VIDEO_FPS)                                   # 设置相机帧率,请确认相机是否支持
    
    win1 = "camera_{}_frame".format(args.CAMERA_ID)
    win2 = "press y/n to validate"
    index = 0
    while True:                                                                 # 视频输入标定
        key = cv2.waitKey(1)                                                    # 获取键盘输入
        ok, raw_frame = cap.read()                                              # 从相机读入原始帧
        if not ok:                               
            raise Exception("camera read failed")                               # 读取视频失败
        
        if args.DATA_TYPE == 'image':                                           # 【图像采集模式】
            if key == 32:                                                       # 按空格键采集该帧图像     
                img = raw_frame.copy()                                          # 暂时存储该帧图像
                flag = True
            if flag:
                cv2.namedWindow(win2, flags = cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
                cv2.imshow(win2, img)
                if key in (ord("y"), ord("Y")):                                  # 按Y确认采集该图像
                    cv2.imwrite(args.SAVE_PATH + 'camera{}_'.format(args.CAMERA_ID) + args.SAVE_NAME + '{}.jpg'.format(len(DATA)),img)
                    DATA = np.append(DATA, [img], axis=0)
                    print(len(DATA))                                             # 显示目前采集数据数量
                    flag = False
                    cv2.destroyWindow(win2)
                elif key in (ord("n"), ord("N")):                                # 按N丢弃该图像，重新采集
                    flag = False
                    cv2.destroyWindow(win2)

        elif args.DATA_TYPE == 'video':                                          # 【视频采集模式】
            if key == 32:                                                        # 按空格键开始录制视频   
                if not flag:
                    videoWrite = cv2.VideoWriter(args.SAVE_PATH + 'camera{}_'.format(args.CAMERA_ID) + args.SAVE_NAME + '{}.mp4'.format(index), 
                                         cv2.VideoWriter_fourcc('M','P','4','V'), args.VIDEO_FPS, (args.FRAME_WIDTH,args.FRAME_HEIGHT))
                    flag = True 
                else:
                    flag = False                                                 # 再次按空格键结束录制
                    videoWrite.release()
                    cv2.destroyWindow(win1)
                    win1 = "camera_{}_frame".format(args.CAMERA_ID)
                    print(index+1)
                    index += 1 
            if flag:
                win1 = "camera_{}_frame_COLLECTING......".format(args.CAMERA_ID)
                videoWrite.write(raw_frame)

        cv2.namedWindow(win1, flags = cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)  # 可以手动拖动窗口大小
        cv2.imshow(win1, raw_frame)    
        if key == 27: break                                                      # ESC退出

    cap.release()
    cv2.destroyAllWindows() 
    
if __name__ == '__main__':
    main()