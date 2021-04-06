import argparse
import cv2
import numpy as np
from easydict import EasyDict
from pdb import set_trace as b

parser = argparse.ArgumentParser(description="Fisheye Camera Calibration")
parser.add_argument('-id','--CAMERA_ID', default=1, type=int, help='Camera ID')
parser.add_argument('-fw','--FRAME_WIDTH', default=1280, type=int, help='Camera Frame Width')
parser.add_argument('-fh','--FRAME_HEIGHT', default=720, type=int, help='Camera Frame Height')
parser.add_argument('-bw','--N_CHESS_BORAD_WIDTH', default=6, type=int, help='Chess Board Width (corners number)')
parser.add_argument('-bh','--N_CHESS_BORAD_HEIGHT', default=8, type=int, help='Chess Board Height (corners number)')
parser.add_argument('-square','--SQUARE_SIZE_MM', default=20, type=int, help='Chess Board Square Size (mm)')
parser.add_argument('-calibrate','--N_CALIBRATE_SIZE', default=10, type=int, help='Required Calibration Frame Number')
parser.add_argument('-delay','--FIND_CHESSBOARD_DELAY_MOD', default=4, type=int, help='Find Chessboard Delay (frame number)')
parser.add_argument('-read','--MAX_READ_FAIL_CTR', default=10, type=int, help='Max Read Image Failed Criteria (frame number)')
cfgs = parser.parse_args()

cfgs.CHESS_BOARD_SIZE = lambda: (cfgs.N_CHESS_BORAD_WIDTH, cfgs.N_CHESS_BORAD_HEIGHT)
flags = EasyDict()
flags.READ_FAIL_CTR = 0                 
flags.frame_id = 0
flags.ok = False

BOARD = np.array([ [(j * cfgs.SQUARE_SIZE_MM, i * cfgs.SQUARE_SIZE_MM, 0.)]
    for i in range(cfgs.N_CHESS_BORAD_HEIGHT) for j in range(cfgs.N_CHESS_BORAD_WIDTH) ])

class calib_t(EasyDict):
    def __init__(self):
        super().__init__({
        "type":None,
        "camera_mat":None,
        "dist_coeff":None,
        "rvecs":None,
        "tvecs":None,
        "map1":None,
        "map2":None,
        "reproj_err":None,
        "ok":False,
        })
        
class Fisheye:
    def __init__(self):
        self.data = calib_t()
        self.inited = False
        
    def update(self, corners, frame_size):
        board = [BOARD] * len(corners)
        if not self.inited:
            self._update_init(board, corners, frame_size)
            self.inited = True
        else:
            self._update_refine(board, corners, frame_size)
#         self._calc_reproj_err(corners)
        
    def _update_init(self, board, corners, frame_size):
        data = self.data
        data.type = "FISHEYE"
        data.camera_mat = np.eye(3, 3)
        data.dist_coeff = np.zeros((4, 1))
        data.ok, data.camera_mat, data.dist_coeff, data.rvecs, data.tvecs = cv2.fisheye.calibrate(
            board, corners, frame_size, data.camera_mat, data.dist_coeff,
            flags=cv2.fisheye.CALIB_FIX_SKEW|cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC,
            criteria=(cv2.TERM_CRITERIA_COUNT, 30, 0.1))
        data.ok = data.ok and cv2.checkRange(data.camera_mat) and cv2.checkRange(data.dist_coeff)
        
    def _update_refine(self, board, corners, frame_size):
        data = self.data
        data.ok, data.camera_mat, data.dist_coeff, data.rvecs, data.tvecs = cv2.fisheye.calibrate(
            board, corners, frame_size, data.camera_mat, data.dist_coeff,
            flags=cv2.fisheye.CALIB_FIX_SKEW|cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC|cv2.CALIB_USE_INTRINSIC_GUESS,
            criteria=(cv2.TERM_CRITERIA_COUNT, 10, 0.1))
        data.ok = data.ok and cv2.checkRange(data.camera_mat) and cv2.checkRange(data.dist_coeff)
        
    def _calc_reproj_err(self, corners):
        if not self.inited: return
        data = self.data
        data.reproj_err = []
        for i in range(len(corners)):
            corners_reproj = cv2.fisheye.projectPoints(BOARD[i], data.rvecs[i], data.tvecs[i], data.camera_mat, data.dist_coeff)
            err = cv2.norm(corners_reproj, corners[i], cv2.NORM_L2)
            data.reproj_err.append(err)    
        
class data_t(EasyDict):
    def __init__(self, raw_frame):
        super().__init__({
        "raw_frame":raw_frame,
        "corners":None,
        "ok":False,
        })
        self.ok, self.corners = cv2.findChessboardCorners(self.raw_frame, cfgs.CHESS_BOARD_SIZE(),
                                flags = cv2.CALIB_CB_ADAPTIVE_THRESH|cv2.CALIB_CB_NORMALIZE_IMAGE|cv2.CALIB_CB_FAST_CHECK)
        if not self.ok: return
        gray = cv2.cvtColor(self.raw_frame, cv2.COLOR_BGR2GRAY)
        self.corners = cv2.cornerSubPix(gray, self.corners, (11, 11), (-1, -1),
                        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 0.1))        
                
class history_t:
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
        
        
def main():
    history = history_t()

    cap = cv2.VideoCapture(cfgs.CAMERA_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfgs.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfgs.FRAME_HEIGHT)
    if not cap.isOpened(): 
        raise Exception("camera {} open failed".format(cfgs.CAMERA_ID))

    fisheye = Fisheye()

    while True:
        ok, raw_frame = cap.read()
        if not ok:
            flags.READ_FAIL_CTR += 1
            if flags.READ_FAIL_CTR >= cfgs.MAX_READ_FAIL_CTR:
                raise Exception("image read failed")
        else:
            flags.READ_FAIL_CTR = 0
            flags.frame_id += 1

        if 0 == flags.frame_id % cfgs.FIND_CHESSBOARD_DELAY_MOD:
            current = data_t(raw_frame)
            history.append(current)

        if len(history) >= cfgs.N_CALIBRATE_SIZE and history.updated:
            fisheye.update(history.get_corners(), raw_frame.shape[1::-1])
            calib = fisheye.data                                                                             
            calib.map1, calib.map2 = cv2.fisheye.initUndistortRectifyMap(
                calib.camera_mat, calib.dist_coeff, np.eye(3, 3), calib.camera_mat, raw_frame.shape[1::-1], cv2.CV_16SC2)
            
        if len(history) >= cfgs.N_CALIBRATE_SIZE:
            undist_frame = cv2.remap(raw_frame, calib.map1, calib.map2, cv2.INTER_LINEAR);     
            cv2.imshow("undist_frame", undist_frame)

        cv2.imshow("raw_frame", raw_frame)
        key = cv2.waitKey(1)
        if key == 27: break
    
    cv2.destroyAllWindows() 
    
    if fisheye.data.dist_coeff is None:
        raise Exception("calibration failed. chessboard not found, check the parameters")
    print("Calibration Complete")
    print("Camera Matrix is : {}".format(fisheye.data.camera_mat.tolist()))
    print("Distortion Coefficient is : {}".format(fisheye.data.dist_coeff.tolist()))
    np.save('camera_K.npy',fisheye.data.camera_mat.tolist())
    np.save('camera_D.npy',fisheye.data.dist_coeff.tolist())
    
if __name__ == '__main__':
    main()
        