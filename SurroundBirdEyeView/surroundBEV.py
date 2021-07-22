import cv2
import numpy as np
import argparse
import os

parser = argparse.ArgumentParser(description="Generate Surrounding Camera Bird Eye View")
parser.add_argument('-fw', '--FRAME_WIDTH', default=1280, type=int, help='Camera Frame Width')
parser.add_argument('-fh', '--FRAME_HEIGHT', default=1024, type=int, help='Camera Frame Height')
parser.add_argument('-bw', '--BEV_WIDTH', default=1000, type=int, help='BEV Frame Width')
parser.add_argument('-bh', '--BEV_HEIGHT', default=1000, type=int, help='BEV Frame Height')
parser.add_argument('-cw', '--CAR_WIDTH', default=250, type=int, help='Car Frame Width')
parser.add_argument('-ch', '--CAR_HEIGHT', default=400, type=int, help='Car Frame Height')
parser.add_argument('-fs', '--FOCAL_SCALE', default=1, type=float, help='Camera Undistort Focal Scale')
parser.add_argument('-ss', '--SIZE_SCALE', default=2, type=float, help='Camera Undistort Size Scale')
parser.add_argument('-blend','--BLEND_FLAG', default=False, type=bool, help='Blend BEV Image (Ture/False)')
parser.add_argument('-balance','--BALANCE_FLAG', default=False, type=bool, help='Balance BEV Image (Ture/False)')
args = parser.parse_args()

FRAME_WIDTH = args.FRAME_WIDTH
FRAME_HEIGHT = args.FRAME_HEIGHT
BEV_WIDTH = args.BEV_WIDTH
BEV_HEIGHT = args.BEV_HEIGHT
CAR_WIDTH = args.CAR_WIDTH
CAR_HEIGHT = args.CAR_HEIGHT
FOCAL_SCALE = args.FOCAL_SCALE
SIZE_SCALE = args.SIZE_SCALE

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

def color_balance(image):
    b, g, r = cv2.split(image)
    B = np.mean(b)
    G = np.mean(g)
    R = np.mean(r)
    K = (R + G + B) / 3
    Kb = K / B
    Kg = K / G
    Kr = K / R
    cv2.addWeighted(b, Kb, 0, 0, 0, b)
    cv2.addWeighted(g, Kg, 0, 0, 0, g)
    cv2.addWeighted(r, Kr, 0, 0, 0, r)
    return cv2.merge([b,g,r])

def luminance_balance(images):
    [front,back,left,right] = [cv2.cvtColor(image,cv2.COLOR_BGR2HSV) 
                               for image in images]
    hf, sf, vf = cv2.split(front)
    hb, sb, vb = cv2.split(back)
    hl, sl, vl = cv2.split(left)
    hr, sr, vr = cv2.split(right)
    V_f = np.mean(vf)
    V_b = np.mean(vb)
    V_l = np.mean(vl)
    V_r = np.mean(vr)
    V_mean = (V_f + V_b + V_l +V_r) / 4
    vf = cv2.add(vf,(V_mean - V_f))
    vb = cv2.add(vb,(V_mean - V_b))
    vl = cv2.add(vl,(V_mean - V_l))
    vr = cv2.add(vr,(V_mean - V_r))
    front = cv2.merge([hf,sf,vf])
    back = cv2.merge([hb,sb,vb])
    left = cv2.merge([hl,sl,vl])
    right = cv2.merge([hr,sr,vr])
    images = [front,back,left,right]
    images = [cv2.cvtColor(image,cv2.COLOR_HSV2BGR) for image in images]
    return images

class Camera:
    def __init__(self, name):
        self.camera_mat = np.load(os.path.dirname(__file__) + '/data/{}/camera_{}_K.npy'.format(name,name))
        self.dist_coeff = np.load(os.path.dirname(__file__) + '/data/{}/camera_{}_D.npy'.format(name,name))
        self.homography = np.load(os.path.dirname(__file__) + '/data/{}/camera_{}_H.npy'.format(name,name))
        self.camera_mat_dst = self.get_camera_mat_dst()
        self.undistort_maps = self.get_undistort_maps()
        self.bev_maps = self.get_bev_maps()
        
    def get_camera_mat_dst(self):
        camera_mat_dst = self.camera_mat.copy()
        camera_mat_dst[0][0] *= FOCAL_SCALE
        camera_mat_dst[1][1] *= FOCAL_SCALE
        camera_mat_dst[0][2] = FRAME_WIDTH / 2 * SIZE_SCALE
        camera_mat_dst[1][2] = FRAME_HEIGHT / 2 * SIZE_SCALE
        return camera_mat_dst
    
    def get_undistort_maps(self):
        undistort_maps = cv2.fisheye.initUndistortRectifyMap(
                    self.camera_mat, self.dist_coeff, 
                    np.eye(3, 3), self.camera_mat_dst,
                    (int(FRAME_WIDTH * SIZE_SCALE), int(FRAME_HEIGHT * SIZE_SCALE)), cv2.CV_16SC2)
        return undistort_maps
    
    def get_bev_maps(self):
        map1 = self.warp_homography(self.undistort_maps[0])
        map2 = self.warp_homography(self.undistort_maps[1])
        return (map1, map2)
    
    def undistort(self, img):
        return cv2.remap(img, *self.undistort_maps, interpolation = cv2.INTER_LINEAR)
        
    def warp_homography(self, img):
        return cv2.warpPerspective(img, self.homography, (BEV_WIDTH,BEV_HEIGHT))
        
    def raw2bev(self, img):
        return cv2.remap(img, *self.bev_maps, interpolation = cv2.INTER_LINEAR)

class Mask:
    def __init__(self, name):
        self.mask = self.get_mask(name)
        
    def get_points(self, name):
        if name == 'front':
            points = np.array([
                [0, 0],
                [BEV_WIDTH, 0], 
                [(BEV_WIDTH+CAR_WIDTH)/2, (BEV_HEIGHT-CAR_HEIGHT)/2],
                [(BEV_WIDTH-CAR_WIDTH)/2, (BEV_HEIGHT-CAR_HEIGHT)/2]
            ]).astype(np.int32)
        elif name == 'back':
            points = np.array([
                [0, BEV_HEIGHT],
                [BEV_WIDTH, BEV_HEIGHT],
                [(BEV_WIDTH+CAR_WIDTH)/2, (BEV_HEIGHT+CAR_HEIGHT)/2], 
                [(BEV_WIDTH-CAR_WIDTH)/2, (BEV_HEIGHT+CAR_HEIGHT)/2]
            ]).astype(np.int32)
        elif name == 'left':
            points = np.array([
                [0, 0],
                [0, BEV_HEIGHT], 
                [(BEV_WIDTH-CAR_WIDTH)/2, (BEV_HEIGHT+CAR_HEIGHT)/2],
                [(BEV_WIDTH-CAR_WIDTH)/2, (BEV_HEIGHT-CAR_HEIGHT)/2]
            ]).astype(np.int32)
        elif name == 'right':
            points = np.array([
                [BEV_WIDTH, 0],
                [BEV_WIDTH, BEV_HEIGHT], 
                [(BEV_WIDTH+CAR_WIDTH)/2, (BEV_HEIGHT+CAR_HEIGHT)/2], 
                [(BEV_WIDTH+CAR_WIDTH)/2, (BEV_HEIGHT-CAR_HEIGHT)/2]
            ]).astype(np.int32)
        else:
            raise Exception("name should be front/back/left/right")
        return points
    
    def get_mask(self, name):
        mask = np.zeros((BEV_HEIGHT,BEV_WIDTH), dtype=np.uint8)
        points = self.get_points(name)
        return cv2.fillPoly(mask, [points], 255)
    
    def __call__(self, img):
        return cv2.bitwise_and(img, img, mask=self.mask)

class BlendMask:
    def __init__(self,name):
        mf = self.get_mask('front')
        mb = self.get_mask('back')
        ml = self.get_mask('left')
        mr = self.get_mask('right')
        self.get_lines()
        if name == 'front':
            mf = self.get_blend_mask(mf, ml, self.lineFL, self.lineLF)
            mf = self.get_blend_mask(mf, mr, self.lineFR, self.lineRF)
            self.mask = mf
        if name == 'back':
            mb = self.get_blend_mask(mb, ml, self.lineBL, self.lineLB)
            mb = self.get_blend_mask(mb, mr, self.lineBR, self.lineRB)
            self.mask = mb
        if name == 'left':
            ml = self.get_blend_mask(ml, mf, self.lineLF, self.lineFL)
            ml = self.get_blend_mask(ml, mb, self.lineLB, self.lineBL)
            self.mask = ml
        if name == 'right':
            mr = self.get_blend_mask(mr, mf, self.lineRF, self.lineFR)
            mr = self.get_blend_mask(mr, mb, self.lineRB, self.lineBR)
            self.mask = mr
        self.weight = np.repeat(self.mask[:, :, np.newaxis], 3, axis=2) / 255.0
        self.weight = self.weight.astype(np.float32)
        
    def get_points(self, name):
        if name == 'front':
            points = np.array([
                [0, 0],
                [BEV_WIDTH, 0], 
                [BEV_WIDTH, BEV_HEIGHT/5], 
                [(BEV_WIDTH+CAR_WIDTH)/2, (BEV_HEIGHT-CAR_HEIGHT)/2],
                [(BEV_WIDTH-CAR_WIDTH)/2, (BEV_HEIGHT-CAR_HEIGHT)/2],
                [0, BEV_HEIGHT/5], 
            ]).astype(np.int32)
        elif name == 'back':
            points = np.array([
                [0, BEV_HEIGHT],
                [BEV_WIDTH, BEV_HEIGHT],
                [BEV_WIDTH, BEV_HEIGHT - BEV_HEIGHT/5],
                [(BEV_WIDTH+CAR_WIDTH)/2, (BEV_HEIGHT+CAR_HEIGHT)/2], 
                [(BEV_WIDTH-CAR_WIDTH)/2, (BEV_HEIGHT+CAR_HEIGHT)/2],
                [0, BEV_HEIGHT - BEV_HEIGHT/5],
            ]).astype(np.int32)
        elif name == 'left':
            points = np.array([
                [0, 0],
                [0, BEV_HEIGHT], 
                [BEV_WIDTH/5, BEV_HEIGHT], 
                [(BEV_WIDTH-CAR_WIDTH)/2, (BEV_HEIGHT+CAR_HEIGHT)/2],
                [(BEV_WIDTH-CAR_WIDTH)/2, (BEV_HEIGHT-CAR_HEIGHT)/2],
                [BEV_WIDTH/5, 0]
            ]).astype(np.int32)
        elif name == 'right':
            points = np.array([
                [BEV_WIDTH, 0],
                [BEV_WIDTH, BEV_HEIGHT], 
                [BEV_WIDTH - BEV_WIDTH/5, BEV_HEIGHT],
                [(BEV_WIDTH+CAR_WIDTH)/2, (BEV_HEIGHT+CAR_HEIGHT)/2], 
                [(BEV_WIDTH+CAR_WIDTH)/2, (BEV_HEIGHT-CAR_HEIGHT)/2],
                [BEV_WIDTH - BEV_WIDTH/5, 0]
            ]).astype(np.int32)
        else:
            raise Exception("name should be front/back/left/right")
        return points
    
    def get_mask(self, name):
        mask = np.zeros((BEV_HEIGHT,BEV_WIDTH), dtype=np.uint8)
        points = self.get_points(name)
        return cv2.fillPoly(mask, [points], 255)
    
    def get_lines(self):
        self.lineFL = np.array([
                        [0, BEV_HEIGHT/5], 
                        [(BEV_WIDTH-CAR_WIDTH)/2, (BEV_HEIGHT-CAR_HEIGHT)/2],
                    ]).astype(np.int32)
        self.lineFR = np.array([
                        [BEV_WIDTH, BEV_HEIGHT/5], 
                        [(BEV_WIDTH+CAR_WIDTH)/2, (BEV_HEIGHT-CAR_HEIGHT)/2],
                    ]).astype(np.int32)
        self.lineBL = np.array([
                        [0, BEV_HEIGHT - BEV_HEIGHT/5], 
                        [(BEV_WIDTH-CAR_WIDTH)/2, (BEV_HEIGHT+CAR_HEIGHT)/2],
                    ]).astype(np.int32)
        self.lineBR = np.array([
                        [BEV_WIDTH, BEV_HEIGHT - BEV_HEIGHT/5], 
                        [(BEV_WIDTH+CAR_WIDTH)/2, (BEV_HEIGHT+CAR_HEIGHT)/2],
                    ]).astype(np.int32)
        self.lineLF = np.array([
                        [BEV_WIDTH/5, 0],
                        [(BEV_WIDTH-CAR_WIDTH)/2, (BEV_HEIGHT-CAR_HEIGHT)/2]
                    ]).astype(np.int32)
        self.lineLB = np.array([
                        [BEV_WIDTH/5, BEV_HEIGHT],
                        [(BEV_WIDTH-CAR_WIDTH)/2, (BEV_HEIGHT+CAR_HEIGHT)/2]
                    ]).astype(np.int32)
        self.lineRF = np.array([
                        [BEV_WIDTH - BEV_WIDTH/5, 0],
                        [(BEV_WIDTH+CAR_WIDTH)/2, (BEV_HEIGHT-CAR_HEIGHT)/2]
                    ]).astype(np.int32)
        self.lineRB = np.array([
                        [BEV_WIDTH - BEV_WIDTH/5, BEV_HEIGHT],
                        [(BEV_WIDTH+CAR_WIDTH)/2, (BEV_HEIGHT+CAR_HEIGHT)/2]
                    ]).astype(np.int32)
        
    def get_blend_mask(self, maskA, maskB, lineA, lineB):
        overlap = cv2.bitwise_and(maskA, maskB)
        indices = np.where(overlap != 0)
        for y, x in zip(*indices):
            distA = cv2.pointPolygonTest(np.array(lineA), (x, y), True)
            distB = cv2.pointPolygonTest(np.array(lineB), (x, y), True)
            maskA[y, x] = distA**2 / (distA**2 + distB**2 + 1e-6) * 255
        return maskA
    
    def __call__(self, img):
        return (img * self.weight).astype(np.uint8)    
    
class BevGenerator:
    def __init__(self, blend=args.BLEND_FLAG, balance=args.BALANCE_FLAG):
        self.init_args()
        self.cameras = [Camera('front'), Camera('back'), 
                        Camera('left'), Camera('right')]
        self.blend = blend
        self.balance = balance
        if not self.blend:
            self.masks = [Mask('front'), Mask('back'), 
                          Mask('left'), Mask('right')]
        else:
            self.masks = [BlendMask('front'), BlendMask('back'), 
                      BlendMask('left'), BlendMask('right')]

    @staticmethod
    def get_args():
        return args

    def init_args(self):
        global FRAME_WIDTH, FRAME_HEIGHT, BEV_WIDTH, BEV_HEIGHT
        global CAR_WIDTH, CAR_HEIGHT, FOCAL_SCALE, SIZE_SCALE
        FRAME_WIDTH = args.FRAME_WIDTH
        FRAME_HEIGHT = args.FRAME_HEIGHT
        BEV_WIDTH = args.BEV_WIDTH
        BEV_HEIGHT = args.BEV_HEIGHT
        CAR_WIDTH = args.CAR_WIDTH
        CAR_HEIGHT = args.CAR_HEIGHT
        FOCAL_SCALE = args.FOCAL_SCALE
        SIZE_SCALE = args.SIZE_SCALE

    def __call__(self, front, back, left, right, car = None):
        images = [front,back,left,right]
        if self.balance:
            images = luminance_balance(images)
        images = [mask(camera.raw2bev(img)) 
                  for img, mask, camera in zip(images, self.masks, self.cameras)]
        surround = cv2.add(images[0],images[1])
        surround = cv2.add(surround,images[2])
        surround = cv2.add(surround,images[3])
        if self.balance:
            surround = color_balance(surround)
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
    
    cv2.namedWindow('surround', flags = cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.imshow('surround', surround)
    cv2.imwrite('./surround.jpg', surround)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()