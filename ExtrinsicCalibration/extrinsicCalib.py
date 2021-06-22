import argparse
import cv2
import numpy as np
import os

parser = argparse.ArgumentParser(description="Homography from Source to Destination Image")
parser.add_argument('-id', '--CAMERA_ID', default=1, type=int, help='Camera ID')
parser.add_argument('-path', '--INPUT_PATH', default='./data/', type=str, help='Input Source/Destination Image Path')
parser.add_argument('-bw','--BORAD_WIDTH', default=7, type=int, help='Chess Board Width (corners number)')
parser.add_argument('-bh','--BORAD_HEIGHT', default=6, type=int, help='Chess Board Height (corners number)')
parser.add_argument('-src', '--SOURCE_IMAGE', default='img_src', type=str, help='Source Image File Name Prefix (eg.:img_src)')
parser.add_argument('-dst', '--DEST_IMAGE', default='img_dst', type=str, help='Destionation Image File Name Prefix (eg.:img_dst)')
parser.add_argument('-size','--SCALED_SIZE', default=10, type=int, help='Scaled Chess Board Square Size (image pixel)')
parser.add_argument('-subpix_s','--SUBPIX_REGION_SRC', default=3, type=int, help='Corners Subpix Region of img_src')
parser.add_argument('-subpix_d','--SUBPIX_REGION_DST', default=3, type=int, help='Corners Subpix Region of img_dst')
parser.add_argument('-center','--CENTER_FLAG', default=False, type=bool, help='Center Image Manually (Ture/False)')
parser.add_argument('-scale','--SCALE_FLAG', default=False, type=bool, help='Scale Image to Fix Board Size (Ture/False)')
parser.add_argument('-store','--STORE_FLAG', default=False, type=bool, help='Store Centerd/Scaled Images (Ture/False)')
parser.add_argument('-store_path', '--STORE_PATH', default='./data/', type=str, help='Path to Store Centerd/Scaled Images')
args = parser.parse_args()

class CenterImage:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.param = {'tl': None, 'br': None, 'current_pos': None,'complete': False}
        self.display = "CLICK image center and press Y/N to validate, ESC to stay original"

    def mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            img = self.raw_frame.copy()
            param['current_pos'] = (x, y)
            if param['tl'] is None:
                param['tl'] = param['current_pos'] 
        if event == cv2.EVENT_MOUSEMOVE and param['tl'] is not None and not param['complete']:
            img = self.raw_frame.copy()
            param['current_pos'] = (x, y)
            cv2.rectangle(img, param['tl'], param['current_pos'], (0, 0, 255))
            cv2.imshow(self.display, img)
        if event == cv2.EVENT_LBUTTONUP and param['tl'] is not None:
            img = self.raw_frame.copy()
            param['br'] = (x, y)
            param['complete'] = True
            cv2.rectangle(img, param['tl'], param['br'], (0, 0, 255))
            cv2.imshow(self.display, img)
            self.x = (param['tl'][0] + param['br'][0] ) // 2
            self.y = (param['tl'][1] + param['br'][1] ) // 2
            text = " %d,%d? (y/n)" % (self.x, self.y)
            cv2.circle(img, (self.x, self.y), 1, (0, 0, 255), thickness = 2)
            cv2.putText(img, text, (self.x, self.y), cv2.FONT_HERSHEY_PLAIN,1.0, (0, 0, 0), thickness = 1)
            cv2.imshow(self.display, img)
        self.param = param
        
    def translate(self, img):
        shift_x = img.shape[1] // 2 - self.x
        shift_y = img.shape[0] // 2 - self.y
        M = np.float32([[1,0,shift_x],[0,1,shift_y]])
        img_dst = cv2.warpAffine(img,M,img.shape[1::-1])
        return img_dst
        
    def __call__(self, raw_frame):   
        self.raw_frame = raw_frame
        cv2.namedWindow(self.display, flags = cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
        cv2.setMouseCallback(self.display, self.mouse, self.param)
        while True:
            cv2.imshow(self.display, self.raw_frame)
            key = cv2.waitKey(0)
            if key in (ord("y"), ord("Y")):
                break
            elif key in (ord("n"), ord("N")):
                self.x = 0
                self.y = 0
                self.param['tl'] = None
                self.param['br'] = None
                self.param['current_pos'] = None
                self.param['complete'] = None
            elif key == 27: 
                self.x = 0
                self.y = 0
                break
        cv2.destroyAllWindows()
        if not (self.x == 0 and self.y == 0):
            return self.translate(self.raw_frame)
        else:
            return self.raw_frame

class ScaleImage:
    def __init__(self, corners):        
        self.calc_dist(corners)
        print('scale image from {} to {}'.format(self.dist_square,args.SCALED_SIZE))
        self.scale_factor = args.SCALED_SIZE / self.dist_square
        
    def calc_dist(self, corners):
        dist_total = 0
        for i in range(args.BORAD_HEIGHT):
            dist = cv2.norm(corners[i * args.BORAD_WIDTH,:], corners[(i+1) * args.BORAD_WIDTH-1,:], cv2.NORM_L2)
            dist_total += dist / (args.BORAD_WIDTH - 1)
        self.dist_square = dist_total / args.BORAD_HEIGHT

    def padding(self, img, width, height):
        H = img.shape[0]
        W = img.shape[1]
        top = (height - H) // 2 
        bottom = (height - H) // 2 
        if top + bottom + H < height:
            bottom += 1
        left = (width - W) // 2 
        right = (width - W) // 2 
        if left + right + W < width:
            right += 1
        return cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value = (0,0,0))  

    def center_crop(self, img, width, height):
        H = img.shape[0]
        W = img.shape[1]
        top = (H - height) // 2
        bottom = (H - height) // 2 + height
        left = (W - width) // 2
        right = (W - width) // 2 + width
        return img[top:bottom, left:right]          
    
    def __call__(self, raw_frame):
        width = raw_frame.shape[1]
        height = raw_frame.shape[0]
        raw_frame = cv2.resize(raw_frame, (0,0), fx=self.scale_factor, fy=self.scale_factor)  # 图像缩放
        if self.scale_factor < 1:
            raw_frame = self.padding(raw_frame, width, height)
        else:                     
            raw_frame = self.center_crop(raw_frame, width, height)
        return raw_frame

class ExCalibrator():
    def __init__(self):
        self.src_corners_total = np.empty([0,1,2])
        self.dst_corners_total = np.empty([0,1,2])

    @staticmethod
    def get_args():
        return args

    def imgPreprocess(self, img, center, scale):
        if center:
            centerImg = CenterImage()
            img = centerImg(img)
        if scale:
            ok, corners = self.get_corners(img, subpix = args.SUBPIX_REGION_DST)
            if not ok:
                raise Exception("failed to find corners in destination image")
            scaleImg = ScaleImage(corners)
            img = scaleImg(img)
        cv2.imshow("Preprocessed Image", img)
        cv2.waitKey(0)
        return img
        
    def get_corners(self, img, subpix, draw=False):
        ok, corners = cv2.findChessboardCorners(img, (args.BORAD_WIDTH, args.BORAD_HEIGHT),
                      flags = cv2.CALIB_CB_ADAPTIVE_THRESH|cv2.CALIB_CB_NORMALIZE_IMAGE)
        if ok: 
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            corners = cv2.cornerSubPix(gray, corners, (subpix, subpix), (-1, -1),
                                       (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.01))
        if draw:
            cv2.drawChessboardCorners(img, (args.BORAD_WIDTH, args.BORAD_HEIGHT), corners, ok)
        return ok, corners
    
    def warp(self):
        src_warp = cv2.warpPerspective(self.src_img, self.homography, 
                                       (self.dst_img.shape[1], self.dst_img.shape[0])) 
        return src_warp
        
    def __call__(self, src_img, dst_img):
        ok, dst_corners = self.get_corners(dst_img, subpix = args.SUBPIX_REGION_DST, draw=True)
        if not ok:
            raise Exception("failed to find corners in destination image")
        ok, src_corners = self.get_corners(src_img, subpix = args.SUBPIX_REGION_SRC, draw=True)
        if not ok:
            raise Exception("failed to find corners in source image")
        self.dst_corners_total = np.append(self.dst_corners_total, dst_corners, axis = 0)
        self.src_corners_total = np.append(self.src_corners_total, src_corners, axis = 0)
        self.homography, _ = cv2.findHomography(self.src_corners_total, self.dst_corners_total,method = cv2.RANSAC)
        self.src_img = src_img
        self.dst_img = dst_img
        return self.homography    

def get_images(PATH, NAME):
    filePath = [os.path.join(PATH, x) for x in os.listdir(PATH)
                if any(x.endswith(extension) for extension in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'])
               ]
    filenames = [filename for filename in filePath if NAME in filename]
    if len(filenames) == 0:
        raise Exception("from {} read images failed".format(PATH))
    return filenames
    
def main():
    srcfiles = get_images(args.INPUT_PATH, args.SOURCE_IMAGE)
    dstfiles = get_images(args.INPUT_PATH, args.DEST_IMAGE)  
    if len(srcfiles) != len(dstfiles):
        raise Exception("numbers of source and destination images should be equal")
    
    exCalib = ExCalibrator()

    for i in range(len(srcfiles)):    
        src_raw = cv2.imread(srcfiles[i])
        dst_raw = cv2.imread(dstfiles[i])
        print(srcfiles[i])
        print(dstfiles[i])

        if args.CENTER_FLAG or args.SCALE_FLAG:
            dst_raw = exCalib.imgPreprocess(dst_raw, args.CENTER_FLAG, args.SCALE_FLAG)
        if args.STORE_FLAG:
            cv2.imwrite(args.STORE_PATH + 'img_dst{}.jpg'.format(i), dst_raw)  

        homography = exCalib(src_raw, dst_raw)
        print("Homography Matrix is:")
        print(homography.tolist())
        np.save('camera_{}_H.npy'.format(args.CAMERA_ID), homography)

        src_warp = exCalib.warp()
        
        cv2.namedWindow("Source View", flags = cv2.WINDOW_NORMAL|cv2.WINDOW_KEEPRATIO)
        cv2.imshow("Source View", src_raw)
        cv2.namedWindow("Destination View", flags = cv2.WINDOW_NORMAL|cv2.WINDOW_KEEPRATIO)
        cv2.imshow("Destination View", dst_raw)
        cv2.namedWindow("Warped Source View", flags = cv2.WINDOW_NORMAL|cv2.WINDOW_KEEPRATIO)
        cv2.imshow("Warped Source View", src_warp)
        
        while True:
            key = cv2.waitKey(0)
            if key == 27: break
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()    
