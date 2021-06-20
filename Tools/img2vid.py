import argparse
import cv2
import os

parser = argparse.ArgumentParser(description="Convert Image to Video")
parser.add_argument('-path', '--PATH', default='./data/', type=str, help='Image Path')
parser.add_argument('-name', '--NAME', default='video.mp4', type=str, help='Video Name')
parser.add_argument('-width','--WIDTH', default=1280, type=int, help='Camera Frame Width')
parser.add_argument('-height','--HEIGHT', default=1024, type=int, help='Camera Frame Height')
parser.add_argument('-fps','--FPS', default=25, type=int, help='Video Frame per Second')
args = parser.parse_args()

def main():
    videoWrite = cv2.VideoWriter('./' + args.NAME, cv2.VideoWriter_fourcc('M', 'P', '4', 'V'),
                                 args.FPS, (args.WIDTH, args.HEIGHT))
    files = os.listdir(args.PATH)
    for file in files:
        img = cv2.imread(args.PATH + file)
        videoWrite.write(img)
    videoWrite.release()

if __name__ == '__main__' :
    main()


