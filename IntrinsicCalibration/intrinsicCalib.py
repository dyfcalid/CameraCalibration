import argparse
import cv2
import numpy as np
import os

parser = argparse.ArgumentParser(description="Camera Intrinsic Calibration")
parser.add_argument('-input', '--INPUT_TYPE', default='camera', type=str, help='Input Source: camera/video/image')
parser.add_argument('-type', '--CAMERA_TYPE', default='fisheye', type=str, help='Camera Type: fisheye/normal')
parser.add_argument('-id', '--CAMERA_ID', default=1, type=int, help='Camera ID')
parser.add_argument('-path', '--INPUT_PATH', default='./data/', type=str, help='Input Video/Image Path')
parser.add_argument('-video', '--VIDEO_FILE', default='video.mp4', type=str, help='Input Video File Name (eg.: video.mp4)')
parser.add_argument('-image', '--IMAGE_FILE', default='img_raw', type=str, help='Input Image File Name Prefix (eg.: img_raw)')
parser.add_argument('-mode', '--SELECT_MODE', default='auto', type=str, help='Image Select Mode: auto/manual')
parser.add_argument('-fw','--FRAME_WIDTH', default=1280, type=int, help='Camera Frame Width')
parser.add_argument('-fh','--FRAME_HEIGHT', default=720, type=int, help='Camera Frame Height')
parser.add_argument('-bw','--BORAD_WIDTH', default=9, type=int, help='Chess Board Width (corners number)')
parser.add_argument('-bh','--BORAD_HEIGHT', default=6, type=int, help='Chess Board Height (corners number)')
parser.add_argument('-size','--SQUARE_SIZE', default=10, type=int, help='Chess Board Square Size (mm)')
parser.add_argument('-num','--CALIBRATE_NUMBER', default=5, type=int, help='Least Required Calibration Frame Number')
parser.add_argument('-delay','--FRAME_DELAY', default=8, type=int, help='Capture Image Time Interval (frame number)')
parser.add_argument('-store','--STORE_CAPTURE', default=False, type=bool, help='Store Captured Images (Ture/False)')
parser.add_argument('-crop','--FRAME_CROP', default=False, type=bool, help='Crop Input Video/Image to (fw,fh) (Ture/False)')
parser.add_argument('-resize','--FRAME_RESIZE', default=False, type=bool, help='Resize Input Video/Image to (fw,fh) (Ture/False)')
cfgs = parser.parse_args()

CHESS_BOARD_PATTERN = (cfgs.BORAD_WIDTH, cfgs.BORAD_HEIGHT)
BOARD = np.array([ [(j * cfgs.SQUARE_SIZE, i * cfgs.SQUARE_SIZE, 0.)]
                  for i in range(cfgs.BORAD_HEIGHT) for j in range(cfgs.BORAD_WIDTH) ],dtype=np.float32)

class CalibData:
    def __init__(self):
        self.type = None
        self.camera_mat = None
        self.dist_coeff = None
        self.rvecs = None
        self.tvecs = None
        self.map1 = None
        self.map2 = None
        self.reproj_err = None
        self.ok = False

class CornerData:
    def __init__(self, raw_frame):
        self.raw_frame = raw_frame
        self.corners = None
        self.ok = False
        self.ok, self.corners = cv2.findChessboardCorners(self.raw_frame, CHESS_BOARD_PATTERN,
                                flags = cv2.CALIB_CB_ADAPTIVE_THRESH|cv2.CALIB_CB_NORMALIZE_IMAGE|cv2.CALIB_CB_FAST_CHECK)
        if not self.ok: return
        gray = cv2.cvtColor(self.raw_frame, cv2.COLOR_BGR2GRAY)
        self.corners = cv2.cornerSubPix(gray, self.corners, (11, 11), (-1, -1),
                        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.01))
        cv2.drawChessboardCorners(self.raw_frame, CHESS_BOARD_PATTERN, self.corners, self.ok)

class Fisheye:
    def __init__(self):
        self.data = CalibData()
        self.inited = False

    def update(self, corners, frame_size):
        board = [BOARD] * len(corners)
        if not self.inited:
            self._update_init(board, corners, frame_size)
            self.inited = True
        else:
            self._update_refine(board, corners, frame_size)
        self._calc_reproj_err(corners)

    def _update_init(self, board, corners, frame_size):
        data = self.data
        data.type = "FISHEYE"
        data.camera_mat = np.eye(3, 3)
        data.dist_coeff = np.zeros((4, 1))
        data.ok, data.camera_mat, data.dist_coeff, data.rvecs, data.tvecs = cv2.fisheye.calibrate(
            board, corners, frame_size, data.camera_mat, data.dist_coeff,
            flags=cv2.fisheye.CALIB_FIX_SKEW|cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC,
            criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 1e-6)) 
        data.ok = data.ok and cv2.checkRange(data.camera_mat) and cv2.checkRange(data.dist_coeff)

    def _update_refine(self, board, corners, frame_size):
        data = self.data
        data.ok, data.camera_mat, data.dist_coeff, data.rvecs, data.tvecs = cv2.fisheye.calibrate(
            board, corners, frame_size, data.camera_mat, data.dist_coeff,
            flags=cv2.fisheye.CALIB_FIX_SKEW|cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC|cv2.CALIB_USE_INTRINSIC_GUESS,
            criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 10, 1e-6))
        data.ok = data.ok and cv2.checkRange(data.camera_mat) and cv2.checkRange(data.dist_coeff)

    def _calc_reproj_err(self, corners):
        if not self.inited: return
        data = self.data
        data.reproj_err = []
        for i in range(len(corners)):
            corners_reproj, _ = cv2.fisheye.projectPoints(BOARD, data.rvecs[i], data.tvecs[i], data.camera_mat, data.dist_coeff)
            err = cv2.norm(corners_reproj, corners[i], cv2.NORM_L2) / len(corners_reproj)
            data.reproj_err.append(err)

class Normal:
    def __init__(self):
        self.data = CalibData()
        self.inited = False
        
    def update(self, corners, frame_size):
        board = [BOARD] * len(corners)
        if not self.inited:
            self._update_init(board, corners, frame_size)
            self.inited = True
        else:
            self._update_refine(board, corners, frame_size)
        self._calc_reproj_err(corners)
        
    def _update_init(self, board, corners, frame_size):
        data = self.data
        data.type = "NORMAL"
        data.camera_mat = np.eye(3, 3)
        data.dist_coeff = np.zeros((5, 1))
        data.ok, data.camera_mat, data.dist_coeff, data.rvecs, data.tvecs = cv2.calibrateCamera(
            board, corners, frame_size, data.camera_mat, data.dist_coeff, 
            criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 1e-6))
        data.ok = data.ok and cv2.checkRange(data.camera_mat) and cv2.checkRange(data.dist_coeff)
        
    def _update_refine(self, board, corners, frame_size):
        data = self.data
        data.ok, data.camera_mat, data.dist_coeff, data.rvecs, data.tvecs = cv2.calibrateCamera(
            board, corners, frame_size, data.camera_mat, data.dist_coeff,  
            flags = cv2.CALIB_USE_INTRINSIC_GUESS,
            criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 10, 1e-6))
        data.ok = data.ok and cv2.checkRange(data.camera_mat) and cv2.checkRange(data.dist_coeff)
        
    def _calc_reproj_err(self, corners):
        if not self.inited: return
        data = self.data
        data.reproj_err = []
        for i in range(len(corners)):
            corners_reproj, _ = cv2.projectPoints(BOARD, data.rvecs[i], data.tvecs[i], data.camera_mat, data.dist_coeff)
            err = cv2.norm(corners_reproj, corners[i], cv2.NORM_L2) / len(corners_reproj)
            data.reproj_err.append(err)

class History:
    def __init__(self):
        self.corners = []
        self.updated = False
    def append(self, current):
        if not current.ok: return
        self.corners.append(current.corners)
        self.updated = True
    def removei(self, i):
        if not 0 <= i < len(self): return
        del self.corners[i]
        self.updated = True
    def __len__(self):
        return len(self.corners)
    def get_corners(self):
        self.updated = False
        return self.corners

class Flags:
    def __init__(self):
        self.READ_FAIL_CTR = 0
        self.frame_id = 0
        self.ready = False

def main():
    flags = Flags()                                                              
    history = History()                                                          
    
    if cfgs.CAMERA_TYPE == 'fisheye':
        camera = Fisheye()                                                      
    elif cfgs.CAMERA_TYPE == 'normal':
        camera = Normal()                                                       
    else:
        raise Exception("CAMERA TYPE should be fisheye or normal")
    
    if cfgs.INPUT_TYPE == 'camera':                                              
        cap = cv2.VideoCapture(cfgs.CAMERA_ID)                                   
        if not cap.isOpened(): 
            raise Exception("camera {} open failed".format(cfgs.CAMERA_ID))      
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfgs.FRAME_WIDTH)                      
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfgs.FRAME_HEIGHT)
    elif cfgs.INPUT_TYPE == 'video':                                             
        cap = cv2.VideoCapture(cfgs.INPUT_PATH + cfgs.VIDEO_FILE)                
        if not cap.isOpened(): 
            raise Exception("from {} read video failed".format(cfgs.INPUT_PATH + cfgs.VIDEO_FILE))
    elif cfgs.INPUT_TYPE == 'image':                                             
        filePath = [os.path.join(cfgs.INPUT_PATH, x) for x in os.listdir(cfgs.INPUT_PATH) 
                    if any(x.endswith(extension) for extension in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'])
                   ]                                                             
        filenames = [filename for filename in filePath if cfgs.IMAGE_FILE in filename] 
        if len(filenames) == 0:
            raise Exception("from {} read images failed".format(cfgs.INPUT_PATH))
    else:
        raise Exception("INPUT TYPE should be camera, video or image")
        
    if cfgs.INPUT_TYPE == 'image':                                                
        for filename in filenames:
            print(filename)
            raw_frame = cv2.imread(filename)
            if cfgs.FRAME_CROP:
                if raw_frame.shape[1]-cfgs.FRAME_WIDTH < 0 or raw_frame.shape[0]-cfgs.FRAME_HEIGHT < 0:
                    raise Exception("CROP size should be smaller than original size")
                raw_frame = raw_frame[
                    round((raw_frame.shape[0]-cfgs.FRAME_HEIGHT)/2):round((raw_frame.shape[0]-cfgs.FRAME_HEIGHT)/2)+cfgs.FRAME_HEIGHT,
                    round((raw_frame.shape[1]-cfgs.FRAME_WIDTH)/2):round((raw_frame.shape[1]-cfgs.FRAME_WIDTH)/2)+cfgs.FRAME_WIDTH ]           
            elif cfgs.FRAME_RESIZE:
                raw_frame = cv2.resize(raw_frame, (cfgs.FRAME_WIDTH, cfgs.FRAME_HEIGHT))
            current = CornerData(raw_frame)                                       
            display = "raw_frame: press SPACE to SELECT, other key to SKIP, press ESC to QUIT"
            cv2.namedWindow(display, flags = cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
            cv2.imshow(display, raw_frame)
            if len(history) > cfgs.CALIBRATE_NUMBER:                              
                undist_frame = cv2.remap(raw_frame, calib.map1, calib.map2, cv2.INTER_LINEAR)
                cv2.namedWindow("undist_frame", flags = cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
                cv2.imshow("undist_frame", undist_frame)                          
            key = cv2.waitKey(1)
            if cfgs.SELECT_MODE == 'manual':                                      
                key = cv2.waitKey(0)
            if key == 32 or cfgs.SELECT_MODE == 'auto':
                history.append(current)                                           
                if len(history) >= cfgs.CALIBRATE_NUMBER:                         
                    camera.update(history.get_corners(), raw_frame.shape[1::-1])  
                    calib = camera.data                                                
                    if cfgs.CAMERA_TYPE == 'fisheye':                             
                        calib.map1, calib.map2 = cv2.fisheye.initUndistortRectifyMap(
                            calib.camera_mat, calib.dist_coeff, np.eye(3, 3), calib.camera_mat, raw_frame.shape[1::-1], cv2.CV_16SC2)
                    else:
                        calib.map1, calib.map2 = cv2.initUndistortRectifyMap(
                            calib.camera_mat, calib.dist_coeff, np.eye(3, 3), calib.camera_mat, raw_frame.shape[1::-1], cv2.CV_16SC2)
            if key == 27: break                                                   
    else:
        while True:                                                               
            key = cv2.waitKey(1)                                                  
            ok, raw_frame = cap.read()                                            
            if not ok:
                if cfgs.INPUT_TYPE == 'video': break
                flags.READ_FAIL_CTR += 1
                if flags.READ_FAIL_CTR >= 20:                                     
                    raise Exception("video read failed")
            else:
                flags.READ_FAIL_CTR = 0
                flags.frame_id += 1
                
            if cfgs.FRAME_CROP:
                if raw_frame.shape[1]-cfgs.FRAME_WIDTH < 0 or raw_frame.shape[0]-cfgs.FRAME_HEIGHT < 0:
                    raise Exception("CROP size should be smaller than original size")
                raw_frame = raw_frame[
                    round((raw_frame.shape[0]-cfgs.FRAME_HEIGHT)/2):round((raw_frame.shape[0]-cfgs.FRAME_HEIGHT)/2)+cfgs.FRAME_HEIGHT,
                    round((raw_frame.shape[1]-cfgs.FRAME_WIDTH)/2):round((raw_frame.shape[1]-cfgs.FRAME_WIDTH)/2)+cfgs.FRAME_WIDTH ]           
            elif cfgs.FRAME_RESIZE:
                raw_frame = cv2.resize(raw_frame, (cfgs.FRAME_WIDTH, cfgs.FRAME_HEIGHT))
            
            if key == 32 or (cfgs.INPUT_TYPE == 'video' and cfgs.SELECT_MODE == 'auto'):
                flags.ready = True                                                
            
            if cfgs.SELECT_MODE == 'auto' and flags.ready and flags.frame_id % cfgs.FRAME_DELAY == 0:  
                if cfgs.STORE_CAPTURE:
                    cv2.imwrite('./data/img_raw{}.jpg'.format(len(history)),raw_frame)
                current = CornerData(raw_frame)                                   
                history.append(current)                                           
                print(len(history))                                               

            if cfgs.SELECT_MODE == 'manual' and key == 32:                        
                if cfgs.STORE_CAPTURE:
                    cv2.imwrite('./data/img_raw{}.jpg'.format(len(history)),raw_frame)
                current = CornerData(raw_frame)                                 
                history.append(current)                                          
                print(len(history))                                              
                
            if flags.ready and len(history) >= cfgs.CALIBRATE_NUMBER and history.updated:   
                camera.update(history.get_corners(), raw_frame.shape[1::-1])    
                calib = camera.data                                                      
                if cfgs.CAMERA_TYPE == 'fisheye':                               
                    calib.map1, calib.map2 = cv2.fisheye.initUndistortRectifyMap(
                        calib.camera_mat, calib.dist_coeff, np.eye(3, 3), calib.camera_mat, raw_frame.shape[1::-1], cv2.CV_16SC2)
                else:
                    calib.map1, calib.map2 = cv2.initUndistortRectifyMap(
                        calib.camera_mat, calib.dist_coeff, np.eye(3, 3), calib.camera_mat, raw_frame.shape[1::-1], cv2.CV_16SC2)

            if flags.ready and len(history) >= cfgs.CALIBRATE_NUMBER:
                undist_frame = cv2.remap(raw_frame, calib.map1, calib.map2, cv2.INTER_LINEAR); 
                cv2.namedWindow("undist_frame", flags = cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
                cv2.imshow("undist_frame", undist_frame)                        
            
            if cfgs.SELECT_MODE == 'manual':
                display = "raw_frame: press SPACE to capture image"
            elif cfgs.INPUT_TYPE == 'camera':
                display = "raw_frame: press SPACE to start calibration"
            else:
                display = "raw_frame"
            cv2.namedWindow(display, flags = cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
            cv2.imshow(display, raw_frame)
            if key == 27: break                                                 
            
        cap.release()
        
    cv2.destroyAllWindows() 
    
    if len(history) == 0:
        raise Exception("Calibration failed. Chessboard not found, check the parameters")  
    if len(history) < cfgs.CALIBRATE_NUMBER:
        raise Exception("Warning: Calibration images are not enough. At least {} images are needed.".format(cfgs.CALIBRATE_NUMBER))           

    print("Calibration Complete")
    print("Camera Matrix is : {}".format(camera.data.camera_mat.tolist()))               
    print("Distortion Coefficient is : {}".format(camera.data.dist_coeff.tolist()))      
    print("Reprojection Error is : {}".format(np.mean(camera.data.reproj_err)))          
    np.save('camera_{}_K.npy'.format(cfgs.CAMERA_ID),camera.data.camera_mat.tolist())
    np.save('camera_{}_D.npy'.format(cfgs.CAMERA_ID),camera.data.dist_coeff.tolist())
    
if __name__ == '__main__':
    main()
