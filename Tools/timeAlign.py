import argparse
import os

parser = argparse.ArgumentParser(description="Time Align for Images")
parser.add_argument("--front", type=str,default="./data/front")
parser.add_argument("--back", type=str,default="./data/back")
parser.add_argument("--left", type=str,default="./data/left")
parser.add_argument("--right", type=str,default="./data/right")
parser.add_argument("--usb_align_thresh", type=float,default=0.1)
args = parser.parse_args([])

def my_mean(base_i):
    sum = 0
    for x in base_i:
        sum += x
    return sum / len(base_i)

def align_time(time_dict, thresh, init=True, info_list=None):
    """
    :param time_dict: {"cam1":[t1,t2,..],"cam2":[t7,t6]...}
    :param thresh: 对齐的时间阈值
    :param init: 如果为True，直接根据time_dict对齐，否则将根据info_list中的数据作为基础，将time_dict与其中进行对齐
    :param info_list: [base_time_stamp, cams] base_time_stamp = [[t1,t3 ...],[t3,t6...],[t3,t8...],[t0,t9 ...]]
    已经对齐的一部分数据
    cams ["leftback","rightback",...] base_time_stamp中的数据来源

    :return: base_time_stamp 和 cams
    """
    def init_base(time_dict):
        init_camera = str()
        max_time = 0
        for key, value in time_dict.items():
            if value[0] > max_time:
                max_time = value[0]
                init_camera = key

        base_time_stamp = [[x] for x in time_dict[init_camera]]
        return base_time_stamp, init_camera

    if init is True:
        base_time_stamp, init_camera = init_base(time_dict)
        cams = []
        cams.append(init_camera)
    else:
        base_time_stamp, cams = info_list
        init_camera = None
    for key, value in time_dict.items():
        if key == init_camera:
            continue
        cams.append(key)
        base_i = 0
        for i, time in enumerate(value):

            if base_i > len(base_time_stamp) - 1:
                break
            time_diff = time - my_mean(base_time_stamp[base_i])
            if abs(time_diff) < thresh:
                base_time_stamp[base_i].append(time)
                base_i += 1
            else:
                if time_diff > 0:
                    while not (time_diff < 0 or abs(time_diff) < thresh):
                        base_i += 1
                        if base_i > len(base_time_stamp) - 1:
                            break
                        time_diff = time - my_mean(base_time_stamp[base_i])
                    if abs(time_diff) < thresh:
                        base_time_stamp[base_i].append(time)
                        if base_i > len(base_time_stamp) - 1:
                            break
                        base_i += 1
    return base_time_stamp, cams

class TimeParser(object):
    def __init__(self, args):
        self.cams = ["front", "back", "left", "right"]
        self.usb_align_thresh = args.usb_align_thresh
        self.cam_dict = dict()
        for cam in self.cams:
            self.cam_dict[cam] = self.get_time_list(eval("args." + cam))

    def get_time_list(self, cam_dir):
        return sorted([float(x[:-4]) for x in os.listdir(cam_dir)])

    def usb_cam_align(self):
        time_list, cam = align_time(self.cam_dict, self.usb_align_thresh, init=True, info_list=None)
        final = list(filter(lambda x: len(x) == 4, time_list))
        return final, cam


def main():
    timeparser = TimeParser(args)
    res, base = timeparser.usb_cam_align()
    print(len(res))
    print(base)
    # print(res)
    # 之后可以按照res列表的内容按顺序读取图片

if __name__ == '__main__':
    main()
