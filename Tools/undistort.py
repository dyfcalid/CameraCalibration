import argparse
import os
import numpy as np
import cv2

parser = argparse.ArgumentParser(description="Camera Undistortion")
parser.add_argument('-width', default=1280, type=int, help='Camera Frame Width')
parser.add_argument('-height', default=720, type=int, help='Camera Frame Height')
parser.add_argument('-focal', default=340, type=float, help='Camera Focal')
parser.add_argument('-focalscale', default=1, type=float, help='Camera Focal Scale')
parser.add_argument('-offset', default=0, type=float, help='Vertical Offset of Height')
parser.add_argument('-load', default=False, type=bool, help='Load New Camera K/D Data (False/True)')
parser.add_argument('-srcformat', default='png', type=str, help='Original Image Format (jpg/png)')
parser.add_argument('-dstformat', default='jpg', type=str, help='Final Image Format (jpg/png)')
parser.add_argument('-quality', default=90, type=int, help='Save Image Quality (jpg:0-100, png:9-0 (low-high))')
parser.add_argument('-name', default=None, type=str, help='Save Image Name')
args = parser.parse_args()

if not args.load:
    camera_mat = np.array([[497.3139490867237, 0.0, 640.5701329565902], 
                           [0.0, 498.67020043459905, 355.66144092075626],
                           [0.0, 0.0, 1.0]])
    dist_coeff = np.array([[-0.044727798721999834], [-0.00615346609772098], 
                           [0.006405910082274002], [0.00032741189211588117]])
else:
    camera_mat = np.load('./camera_K.npy')
    dist_coeff = np.load('camera_D.npy')

args.focal *= args.focalscale 
cam_mat_dst = np.array([[args.focal, 0,          args.width / 2],
                        [0,          args.focal, args.height / 2 + args.offset],
                        [0,          0,          1]])
map1, map2 = cv2.fisheye.initUndistortRectifyMap(
                camera_mat, dist_coeff, np.eye(3, 3), cam_mat_dst,
                (args.width, args.height), cv2.CV_16SC2)

def main():
    filenames = os.listdir('.')
    index = 1
    for filename in filenames:
        if filename[-4:] == '.' + args.srcformat:
            img = cv2.imread(filename)
            img = cv2.remap(img, map1, map2, cv2.INTER_LINEAR)
            
            if not args.name is None:
                filename = args.name + '_{:04d}.'.format(index) + args.srcformat
                index += 1
                
            if args.dstformat == 'jpg':
                cv2.imwrite(filename[:-4] + '.' + args.dstformat, img, [cv2.IMWRITE_JPEG_QUALITY, args.quality])
            elif args.dstformat == 'png':
                cv2.imwrite(filename[:-4] + '.' + args.dstformat, img, [cv2.IMWRITE_PNG_COMPRESSION, args.quality])
            else:
                cv2.imwrite(filename[:-4] + '.' + args.dstformat, img)

if __name__ == '__main__':
    main()
    