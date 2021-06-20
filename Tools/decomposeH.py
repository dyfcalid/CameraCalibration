import cv2
import numpy as np
import argparse

parser = argparse.ArgumentParser(description="Homography Decompose")
parser.add_argument('-path_h', default='./data/camera_0_H.npy', type=str, help='Camera H File Path')
parser.add_argument('-path_k', default='./data/camera_0_K.npy', type=str, help='Camera K File Path')
args = parser.parse_args()

def main():
    H = np.load(args.path_h)
    K = np.load(args.path_k)
    print(H)
    print(K)

    ret, R, T, norm = cv2.decomposeHomographyMat(H, K)
    for i in range(ret):
        print('-----Rotation_{}-------'.format(i))
        print(R[i])
        print('-----Translation_{}-------'.format(i))
        print(T[i])

if __name__ == '__main__':
    main()
