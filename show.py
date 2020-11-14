import cv2

img = cv2.imread('img_crop.jpg')
oh, ow, oc = img.shape
rh = h = 200
rw = w = 200
img_resized = img
img_arr = []
while True:
    rh, rw = int(rh * (65/64)), int(rw * (65/64))
    print(h, w)
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
vout = cv2.VideoWriter('test.mp4',cv2.VideoWriter_fourcc(*'XVID'),fps,(h, w))
#vout = cv2.VideoWriter()
#success = vout.open('test.mov',fourcc,fps,capSize,True) 
for i in range(len(img_arr)):
    vout.write(img_arr[i])
vout.release()  
#cv2.destroyAllWindows()  
