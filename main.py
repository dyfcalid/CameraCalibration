import cv2
import os
import numpy as np
from ExtrinsicCalibration import ExCalibrator
from IntrinsicCalibration import InCalibrator, CalibMode


def runInCalib_1():
    calibrator = InCalibrator('fisheye')
    PATH = './IntrinsicCalibration/data/'
    images = os.listdir(PATH)
    for img in images:
        print(PATH + img)
        raw_frame = cv2.imread(PATH + img)
        result = calibrator(raw_frame)

    print("Camera Matrix is : {}".format(result.camera_mat.tolist()))
    print("Distortion Coefficient is : {}".format(result.dist_coeff.tolist()))
    print("Reprojection Error is : {}".format(np.mean(result.reproj_err)))

    raw_frame = cv2.imread('./IntrinsicCalibration/data/img_raw0.jpg')
    cv2.imshow("Raw Image", raw_frame)
    undist_img = calibrator.undistort(raw_frame)
    cv2.imshow("Undistorted Image", undist_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def runInCalib_2():
    args = InCalibrator.get_args()
    args.INPUT_PATH = './IntrinsicCalibration/data/'
    InCalibrator.edit_args(args)
    calibrator = InCalibrator('fisheye')
    calib = CalibMode(calibrator, 'image', 'auto')
    result = calib()

    print("Camera Matrix is : {}".format(result.camera_mat.tolist()))
    print("Distortion Coefficient is : {}".format(result.dist_coeff.tolist()))
    print("Reprojection Error is : {}".format(np.mean(result.reproj_err)))

    raw_frame = cv2.imread('./IntrinsicCalibration/data/img_raw0.jpg')
    cv2.imshow("Raw Image", raw_frame)
    undist_img = calibrator.undistort(raw_frame)
    cv2.imshow("Undistort Image", undist_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def runExCalib():
    exCalib = ExCalibrator()

    src_raw = cv2.imread('./ExtrinsicCalibration/data/img_src_back.jpg')
    dst_raw = cv2.imread('./ExtrinsicCalibration/data/img_dst_back.jpg')

    homography = exCalib(src_raw, dst_raw)
    print("Homography Matrix is:")
    print(homography.tolist())

    src_warp = exCalib.warp()

    cv2.namedWindow("Source View", flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.imshow("Source View", src_raw)
    cv2.namedWindow("Destination View", flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.imshow("Destination View", dst_raw)
    cv2.namedWindow("Warped Source View", flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.imshow("Warped Source View", src_warp)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main():
    # runInCalib_1()
    runInCalib_2()
    runExCalib()


if __name__ == '__main__':
    main()