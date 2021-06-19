import cv2
from ExtrinsicCalibration import ExCalibrator

def testExCalib():
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

    while True:
        key = cv2.waitKey(0)
        if key == 27: break
    cv2.destroyAllWindows()


def main():
    testExCalib()


if __name__ == '__main__':
    main()