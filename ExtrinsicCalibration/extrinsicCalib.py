import argparse
import cv2
import numpy as np
import os

parser = argparse.ArgumentParser(description="Homography from Source to Destination Image")
parser.add_argument('-id', '--CAMERA_ID', default=1, type=int, help='Camera ID')
parser.add_argument('-path', '--INPUT_PATH', default='./data/', type=str, help='Input Source/Destination Image Path')
parser.add_argument('-fw','--FRAME_WIDTH', default=1280, type=int, help='Camera Frame Width')
parser.add_argument('-fh','--FRAME_HEIGHT', default=720, type=int, help='Camera Frame Height')
parser.add_argument('-bw','--BORAD_WIDTH', default=9, type=int, help='Chess Board Width (corners number)')
parser.add_argument('-bh','--BORAD_HEIGHT', default=6, type=int, help='Chess Board Height (corners number)')
parser.add_argument('-src', '--SOURCE_IMAGE', default='src', type=str, help='Source Image File Name Prefix (eg.:img_src)')
parser.add_argument('-dst', '--DEST_IMAGE', default='dst', type=str, help='Destionation Image File Name Prefix (eg.:img_dst)')
parser.add_argument('-size','--SCALED_SIZE', default=15, type=int, help='Scaled Chess Board Square Size (image pixel)')
parser.add_argument('-center','--CENTER_FLAG', default=True, type=bool, help='Center Image Manually (Ture/False)')
parser.add_argument('-scale','--SCALE_FLAG', default=True, type=bool, help='Scale Image to Fix Board Size (Ture/False)')
parser.add_argument('-store','--STORE_IMAGE', default=False, type=bool, help='Store Centerd/Scaled Images (Ture/False)')
cfgs = parser.parse_args()

CHESS_BOARD_PATTERN = (cfgs.BORAD_WIDTH, cfgs.BORAD_HEIGHT)

class CenterImage:
    def __init__(self, raw_frame):
        self.raw_frame = raw_frame
        self.x = 0
        self.y = 0
        self.param = {'tl': None, 'br': None, 'current_pos': None,'complete': False} 
        self.display = "CLICK image center and press Y/N to validate, ESC to stay original"
        self._operate()
    
    def _mouse(self, event, x, y, flags, param):
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
        
    def _translate(self, img):
        shift_x = img.shape[1] // 2 - self.x
        shift_y = img.shape[0] // 2 - self.y
        M = np.float32([[1,0,shift_x],[0,1,shift_y]])
        img_dst = cv2.warpAffine(img,M,img.shape[1::-1])
        return img_dst
        
    def _operate(self):   
        cv2.namedWindow(self.display)
        cv2.setMouseCallback(self.display, self._mouse, self.param)
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
            self.raw_frame = self._translate(self.raw_frame)

class ScaleImage:
    def __init__(self, raw_frame, corners):        
        self.raw_frame = raw_frame
        self._calc_dist(corners)
        self.scale_factor = cfgs.SCALED_SIZE / self.dist_square
        self._operate()

    def _calc_dist(self,corners):
        dist_total = 0
        for i in range(cfgs.BORAD_HEIGHT):
            dist = cv2.norm(corners[i * cfgs.BORAD_WIDTH,:], corners[(i+1) * cfgs.BORAD_WIDTH-1,:], cv2.NORM_L2)
            dist_total += dist / cfgs.BORAD_WIDTH
        self.dist_square = dist_total / cfgs.BORAD_HEIGHT
    
    def _operate(self):
        self.raw_frame = cv2.resize(self.raw_frame, (0,0), fx=self.scale_factor, fy=self.scale_factor)
        H = self.raw_frame.shape[0]
        W = self.raw_frame.shape[1]
        if self.scale_factor < 1:      
            top = (cfgs.FRAME_HEIGHT - H) // 2 
            bottom = (cfgs.FRAME_HEIGHT - H) // 2 
            if top + bottom + H < cfgs.FRAME_HEIGHT:
                bottom += 1
            left = (cfgs.FRAME_WIDTH - W) // 2 
            right = (cfgs.FRAME_WIDTH - W) // 2 
            if left + right + W < cfgs.FRAME_WIDTH:
                right += 1
            self.raw_frame = cv2.copyMakeBorder(self.raw_frame, top, bottom, left, right, cv2.BORDER_CONSTANT, value = (0,0,0))
        else:                     
            top = (H - cfgs.FRAME_HEIGHT) // 2
            bottom = (H - cfgs.FRAME_HEIGHT) //2 + cfgs.FRAME_HEIGHT
            left = (W - cfgs.FRAME_WIDTH) // 2
            right = (W - cfgs.FRAME_WIDTH) // 2 + cfgs.FRAME_WIDTH
            self.raw_frame = self.raw_frame[top:bottom, left:right]

def main():
    srcFilePath = [os.path.join(cfgs.INPUT_PATH, x) for x in os.listdir(cfgs.INPUT_PATH) 
                if any(x.endswith(extension) for extension in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'])
               ]                                                                       
    srcfiles = [srcfile for srcfile in srcFilePath if cfgs.SOURCE_IMAGE in srcfile] 
    if len(srcfiles) == 0:
        raise Exception("from {} read source images failed".format(cfgs.INPUT_PATH))

    dstFilePath = [os.path.join(cfgs.INPUT_PATH, x) for x in os.listdir(cfgs.INPUT_PATH) 
                if any(x.endswith(extension) for extension in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'])
               ]                                                                      
    dstfiles = [dstfile for dstfile in dstFilePath if cfgs.DEST_IMAGE in dstfile] 
    if len(dstfiles) == 0:
        raise Exception("from {} read destination images failed".format(cfgs.INPUT_PATH))

    if len(srcfiles) != len(dstfiles):
        raise Exception("numbers of source and destination images should be equal")
    
    src_corners_total = np.empty([0,1,2])
    dst_corners_total = np.empty([0,1,2])
    for i in range(len(srcfiles)):    
        src_raw = cv2.imread(srcfiles[i])
        dst_raw = cv2.imread(dstfiles[i])
        print(srcfiles[i])
        print(dstfiles[i])
        
        ret2, dst_corners = cv2.findChessboardCorners(dst_raw, CHESS_BOARD_PATTERN,
                                                      flags = cv2.CALIB_CB_ADAPTIVE_THRESH|cv2.CALIB_CB_NORMALIZE_IMAGE|cv2.CALIB_CB_FAST_CHECK)
        if not ret2:
            raise Exception("failed to find corners in destination image")
        dst_gray = cv2.cvtColor(dst_raw, cv2.COLOR_BGR2GRAY)
        dst_corners = cv2.cornerSubPix(dst_gray, dst_corners, (11, 11), (-1, -1), (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.01))

        if cfgs.CENTER_FLAG:
            centerImg = CenterImage(dst_raw)
            dst_raw = centerImg.raw_frame
            cv2.imshow("Centered Image", dst_raw)
            key = cv2.waitKey(0)
            cv2.destroyAllWindows()
        if cfgs.SCALE_FLAG:
            scaleImg = ScaleImage(dst_raw, dst_corners)
            dst_raw = scaleImg.raw_frame 
            cv2.imshow("Scaled Image", dst_raw)
            key = cv2.waitKey(0)
            cv2.destroyAllWindows()  
        if cfgs.STORE_IMAGE:
            cv2.imwrite('./data/img_dst{}.jpg'.format(i), dst_raw)
        
        ret1, src_corners = cv2.findChessboardCorners(src_raw, CHESS_BOARD_PATTERN,
                                                      flags = cv2.CALIB_CB_ADAPTIVE_THRESH|cv2.CALIB_CB_NORMALIZE_IMAGE|cv2.CALIB_CB_FAST_CHECK)
        if not ret1:
            raise Exception("failed to find corners in source image")
        src_gray = cv2.cvtColor(src_raw, cv2.COLOR_BGR2GRAY)
        src_corners = cv2.cornerSubPix(src_gray, src_corners, (11, 11), (-1, -1), (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.01))
        src_img = cv2.drawChessboardCorners(src_raw, CHESS_BOARD_PATTERN, src_corners, ret1)

        ret2, dst_corners = cv2.findChessboardCorners(dst_raw, CHESS_BOARD_PATTERN,
                                                      flags = cv2.CALIB_CB_ADAPTIVE_THRESH|cv2.CALIB_CB_NORMALIZE_IMAGE|cv2.CALIB_CB_FAST_CHECK)
        if not ret2:
            raise Exception("failed to find corners in destination image")
        dst_gray = cv2.cvtColor(dst_raw, cv2.COLOR_BGR2GRAY)
        dst_corners = cv2.cornerSubPix(dst_gray, dst_corners, (11, 11), (-1, -1), (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.01)) 
        dst_img = cv2.drawChessboardCorners(dst_raw, CHESS_BOARD_PATTERN, dst_corners, ret2)

        src_corners_total = np.append(src_corners_total, src_corners, axis = 0)
        dst_corners_total = np.append(dst_corners_total, dst_corners, axis = 0)

        homography, _ = cv2.findHomography(src_corners_total, dst_corners_total, method = cv2.RANSAC)
        print("Homography Matrix is: ") 
        print(homography)
        
        np.save('camera_{}_homography.npy'.format(cfgs.CAMERA_ID),homography)
        
        src_warp = cv2.warpPerspective(src_raw, homography, (src_raw.shape[1], src_raw.shape[0]))

        img_draw_warp = cv2.hconcat([src_raw, dst_raw, src_warp])
        cv2.namedWindow("Source View / Destination View / Warped Source View", flags = cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
        cv2.imshow("Source View / Destination View / Warped Source View", img_draw_warp )

        while True:
            key = cv2.waitKey(0)
            if key == 27: break
        cv2.destroyAllWindows()
    
           
if __name__ == '__main__':
    main()    
