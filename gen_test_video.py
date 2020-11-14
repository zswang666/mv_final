import cv2

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--src', type=str, required=True,
                    help='Source image')
parser.add_argument('--dst', type=str, required=True,
                    help='Target video')
parser.add_argument('--size', type=int, default=200)
parser.add_argument('--rate', type=float, default=(65)/(64))
args = parser.parse_args()


img = cv2.imread(args.src)
oh, ow, oc = img.shape
rh = h = args.size
rw = w = args.size
img_resized = img
img_arr = []
while True:
    rh, rw = int(rh * args.rate), int(rw * args.rate)
    if rh >= oh:
        break
    ci, cj = rh // 2, rw //2
    img_resized = cv2.resize(img, (rh, rw), interpolation=cv2.INTER_AREA)
    img_resized = img_resized[ci - h//2: ci + h//2, cj - w // 2:cj + w // 2]
    img_arr.append(img_resized)
    cv2.imshow('img', img_resized)
    cv2.waitKey(1)

fps = 30
capSize = (h, w) # this is the size of my source video
#fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v') # note the lower case
#fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
vout = cv2.VideoWriter(args.dst, cv2.VideoWriter_fourcc(*'XVID'),fps,(h, w))
#vout = cv2.VideoWriter()
#success = vout.open('test.mov',fourcc,fps,capSize,True) 
for i in range(len(img_arr)):
    vout.write(img_arr[i])
vout.release()  
#cv2.destroyAllWindows()  
