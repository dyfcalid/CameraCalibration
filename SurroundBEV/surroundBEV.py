import cv2
import numpy as np
import argparse

parser = argparse.ArgumentParser(description="Generate Surrounding Camera Bird Eye View")
parser.add_argument('-fw', '--FRAME_WIDTH', default=1280, type=int, help='Camera Frame Width')
parser.add_argument('-fh', '--FRAME_HEIGHT', default=720, type=int, help='Camera Frame Height')
parser.add_argument('-bw', '--BEV_WIDTH', default=2560, type=int, help='BEV Frame Width')
parser.add_argument('-bh', '--BEV_HEIGHT', default=2560, type=int, help='BEV Frame Height')
parser.add_argument('-cw', '--CAR_WIDTH', default=287, type=int, help='Car Frame Width')
parser.add_argument('-ch', '--CAR_HEIGHT', default=641, type=int, help='Car Frame Height')
args = parser.parse_args()

FRAME_WIDTH = args.FRAME_WIDTH
FRAME_HEIGHT = args.FRAME_HEIGHT
BEV_WIDTH = args.BEV_WIDTH
BEV_HEIGHT = args.BEV_HEIGHT
CAR_WIDTH = args.CAR_WIDTH
CAR_HEIGHT = args.CAR_HEIGHT

def padding(img,width,height):
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
    img = cv2.copyMakeBorder(img, top, bottom, left, right,
                             cv2.BORDER_CONSTANT, value = (0,0,0)) 
    return img

class Camera:
    def __init__(self, name):
        self.camera_mat = np.load('./data/{}/camera_{}_K.npy'.format(name,name))
        self.dist_coeff = np.load('./data/{}/camera_{}_D.npy'.format(name,name))
        self.homography = np.load('./data/{}/camera_{}_H.npy'.format(name,name))
        self.camera_mat_dst = self.get_camera_mat_dst()
        self.undistort_maps = self.get_undistort_maps()
        self.bev_maps = self.get_bev_maps()
        
    def get_camera_mat_dst(self):
        camera_mat_dst = self.camera_mat.copy()
        camera_mat_dst[0][2] = FRAME_WIDTH
        camera_mat_dst[1][2] = FRAME_HEIGHT
        return camera_mat_dst
    
    def get_undistort_maps(self):
        undistort_maps = cv2.fisheye.initUndistortRectifyMap(
                    self.camera_mat, self.dist_coeff, 
                    np.eye(3, 3), self.camera_mat_dst,
                    (FRAME_WIDTH*2, FRAME_HEIGHT*2), cv2.CV_16SC2)
        return undistort_maps
    
    def get_bev_maps(self):
        map1 = self.warp_homography(self.undistort_maps[0])
        map2 = self.warp_homography(self.undistort_maps[1])
        return (map1, map2)
    
    def undistort(self, img):
        return cv2.remap(img, *self.undistort_maps, interpolation = cv2.INTER_LINEAR)
        
    def warp_homography(self, img):
        return cv2.warpPerspective(img, self.homography, (BEV_HEIGHT,BEV_WIDTH))
        
    def raw2bev(self, img):
        return cv2.remap(img, *self.bev_maps, interpolation = cv2.INTER_LINEAR)

class Mask:
    def __init__(self, name):
        self.mask = np.zeros((BEV_HEIGHT,BEV_WIDTH,3), dtype=np.uint8)
        if name == 'front':
            self.points = np.array([
                [0, 0],
                [BEV_HEIGHT, 0], 
                [(BEV_WIDTH+CAR_WIDTH)/2, (BEV_HEIGHT-args.CAR_HEIGHT)/2],
                [(BEV_WIDTH-CAR_WIDTH)/2, (BEV_HEIGHT-args.CAR_HEIGHT)/2]
            ]).astype(np.int32)
        elif name == 'back':
            self.points = np.array([
                [0, BEV_WIDTH],
                [BEV_HEIGHT,BEV_WIDTH],
                [(BEV_WIDTH+CAR_WIDTH)/2, (BEV_HEIGHT+args.CAR_HEIGHT)/2], 
                [(BEV_WIDTH-CAR_WIDTH)/2, (BEV_HEIGHT+args.CAR_HEIGHT)/2]
            ]).astype(np.int32)
        elif name == 'left':
            self.points = np.array([
                [0, 0],
                [0,BEV_WIDTH], 
                [(BEV_WIDTH-CAR_WIDTH)/2, (BEV_HEIGHT+args.CAR_HEIGHT)/2],
                [(BEV_WIDTH-CAR_WIDTH)/2, (BEV_HEIGHT-args.CAR_HEIGHT)/2]
            ]).astype(np.int32)
        elif name == 'right':
            self.points = np.array([
                [BEV_HEIGHT, 0],
                [BEV_HEIGHT,BEV_WIDTH], 
                [(BEV_WIDTH+CAR_WIDTH)/2, (BEV_HEIGHT+args.CAR_HEIGHT)/2], 
                [(BEV_WIDTH+CAR_WIDTH)/2, (BEV_HEIGHT-args.CAR_HEIGHT)/2]
            ]).astype(np.int32)
        else:
            raise Exception("name should be front/back/left/right")
            
    def __call__(self, img):
        self.mask = cv2.fillPoly(self.mask, [self.points], (255,255,255))
        return cv2.bitwise_and(img, self.mask)

class BevGenerator:
    def __init__(self):
        self.cameras = [Camera('front'), Camera('back'), 
                        Camera('left'), Camera('right')]
        self.masks = [Mask('front'), Mask('back'), 
                      Mask('left'), Mask('right')]
        
    def __call__(self, front, back, left, right, car = None):
        images = [front,back,left,right]
        images = [mask(camera.raw2bev(img)) 
                  for img, mask, camera in zip(images, self.masks, self.cameras)]
        surround = cv2.add(images[0],images[1])
        surround = cv2.add(surround,images[2])
        surround = cv2.add(surround,images[3])
        if car is not None:
            surround = cv2.add(surround,car)
        return surround

def main():
    front = cv2.imread('./data/front/front.jpg')
    back = cv2.imread('./data/back/back.jpg')
    left = cv2.imread('./data/left/left.jpg')
    right = cv2.imread('./data/right/right.jpg')
    car = cv2.imread('./data/car.jpg')
    car = padding(car, BEV_WIDTH, BEV_HEIGHT)
    
    bev = BevGenerator()
    surround = bev(front,back,left,right,car)
    
#     surround = surround[780:1780,780:1780,:]
    cv2.namedWindow('surround', flags = cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.imshow('surround', surround)
    # cv2.imwrite('./surround.jpg', surround)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()