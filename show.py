import cv2

img = cv2.imread('img.jpg')
oh, ow, oc = img.shape
h = 400
w = 400
img_resized = img
img_arr = []
while True:
    h, w = int(h * (129/128)), int(w * (129/128))
    if h >= oh:
        h = 400
        w = 400
        break
    ci, cj = h // 2, w //2
    img_resized = cv2.resize(img, (h, w), interpolation=cv2.INTER_AREA)
    img_resized = img_resized[ci - 200: ci + 200, cj - 200:cj + 200]
    img_arr.append(img_resized)
    #print(img_resized.shape)
    cv2.imshow('img', img_resized)
    cv2.waitKey(1)

fps = 30
capSize = (400, 400) # this is the size of my source video
#fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v') # note the lower case
#fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
vout = cv2.VideoWriter('test.mp4',cv2.VideoWriter_fourcc(*'XVID'),fps,(400, 400))
#vout = cv2.VideoWriter()
#success = vout.open('test.mov',fourcc,fps,capSize,True) 
for i in range(len(img_arr)):
    vout.write(img_arr[i])
vout.release()  
#cv2.destroyAllWindows()  
