import cv2
import os
import numpy as np
from ExtrinsicCalibration import ExCalibrator
from IntrinsicCalibration import InCalibrator, CalibMode
from SurroundBirdEyeView import BevGenerator


def runInCalib_1():
    print("Intrinsic Calibration ......")
    calibrator = InCalibrator('fisheye')                # 初始化内参标定器
    PATH = './IntrinsicCalibration/data/'
    images = os.listdir(PATH)
    for img in images:
        print(PATH + img)
        raw_frame = cv2.imread(PATH + img)
        result = calibrator(raw_frame)                  # 每次读入一张原始图片 更新标定结果

    print("Camera Matrix is : {}".format(result.camera_mat.tolist()))
    print("Distortion Coefficient is : {}".format(result.dist_coeff.tolist()))
    print("Reprojection Error is : {}".format(np.mean(result.reproj_err)))

    raw_frame = cv2.imread('./IntrinsicCalibration/data/img_raw0.jpg')
    cv2.imshow("Raw Image", raw_frame)
    undist_img = calibrator.undistort(raw_frame)        # 使用undistort方法得到去畸变图像
    cv2.imshow("Undistorted Image", undist_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def runInCalib_2():
    print("Intrinsic Calibration ......")
    args = InCalibrator.get_args()                      # 获取内参标定args参数
    args.INPUT_PATH = './IntrinsicCalibration/data/'    # 修改为新的参数
    calibrator = InCalibrator('fisheye')                # 初始化内参标定器
    calib = CalibMode(calibrator, 'image', 'auto')      # 选择标定模式
    result = calib()                                    # 开始标定

    print("Camera Matrix is : {}".format(result.camera_mat.tolist()))
    print("Distortion Coefficient is : {}".format(result.dist_coeff.tolist()))
    print("Reprojection Error is : {}".format(np.mean(result.reproj_err)))

    raw_frame = cv2.imread('./IntrinsicCalibration/data/img_raw0.jpg')
    # calibrator.draw_corners(raw_frame)                  # 画出角点
    cv2.imshow("Raw Image", raw_frame)
    undist_img = calibrator.undistort(raw_frame)        # 使用undistort方法得到去畸变图像
    cv2.imshow("Undistort Image", undist_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def runExCalib():
    print("Extrinsic Calibration ......")
    exCalib = ExCalibrator()                            # 初始化外参标定器

    src_raw = cv2.imread('./ExtrinsicCalibration/data/img_src_back.jpg')
    dst_raw = cv2.imread('./ExtrinsicCalibration/data/img_dst_back.jpg')

    homography = exCalib(src_raw, dst_raw)              # 输入对应的两张去畸变图像 得到单应性矩阵
    print("Homography Matrix is:")
    print(homography.tolist())

    src_warp = exCalib.warp()                           # 使用warp方法得到原始图像的变换结果

    cv2.namedWindow("Source View", flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.imshow("Source View", src_raw)
    cv2.namedWindow("Destination View", flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.imshow("Destination View", dst_raw)
    cv2.namedWindow("Warped Source View", flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.imshow("Warped Source View", src_warp)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def runBEV():
    print("Generating Surround BEV ......")
    front = cv2.imread('./SurroundBirdEyeView/data/front/front.jpg')
    back = cv2.imread('./SurroundBirdEyeView/data/back/back.jpg')
    left = cv2.imread('./SurroundBirdEyeView/data/left/left.jpg')
    right = cv2.imread('./SurroundBirdEyeView/data/right/right.jpg')

    args = BevGenerator.get_args()                      # 获取环视鸟瞰args参数
    args.CAR_WIDTH = 200
    args.CAR_HEIGHT = 350                               # 修改为新的参数

    bev = BevGenerator(blend=True, balance=True)        # 初始化环视鸟瞰图生成器
    surround = bev(front, back, left, right)            # 输入前后左右四张原始相机图像 得到拼接后的鸟瞰图

    cv2.namedWindow('surround', flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.imshow('surround', surround)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def main():
    # runInCalib_1()
    runInCalib_2()
    runExCalib()
    runBEV()

if __name__ == '__main__':
    main()

