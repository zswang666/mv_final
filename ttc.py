import numpy as np
import scipy
from scipy import signal
from scipy import misc
import matplotlib.pyplot as plt
import cv2

def load_video(filename):
    cap = cv2.VideoCapture(filename)
    prev_frame = None
    while(cap.isOpened()):
        ret, frame = cap.read()
        if frame is None:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float64)
        if prev_frame is not None:           
            yield prev_frame, frame
        prev_frame = frame
    cap.release()

def uniform_blur(img, n):
    if n == 0:
        return img
    from scipy import ndimage, misc
    return ndimage.uniform_filter(img, size=n)
    
def solve_ttc(img1, img2):
    m, n = img1.shape
    img_stacked = np.stack([img1, img2]).transpose([1, 2, 0])

    DIVIDE_EX = 16 / (n)
    DIVIDE_EY = 16 / (m)
    DIVIDE_ET = 4 / (min(n, m))
    DIVIDE_GG = 1

    sobel = np.array([
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1]
        ])

    sobel3_x = (1 / DIVIDE_EX) * np.stack([sobel, sobel]).transpose([1, 2, 0])
    sobel3_y = (1 / DIVIDE_EY) * np.stack([sobel.T, sobel.T]).transpose([1, 2, 0])
    prewitt2_t = (1 / DIVIDE_ET) * np.array([
                                    [
                                        [-1.0, -1.0], 
                                        [-1.0, -1.0]
                                    ], 
                                    [
                                        [1.0, 1.0], 
                                        [1.0, 1.0]
                                    ]
                                ])
    Ex = signal.convolve(img_stacked[:, :, -1], sobel3_x[:, :, -1])
    Ey = signal.convolve(img_stacked[:, :, -1], sobel3_y[:, :, -1])   
    Et = signal.convolve(img_stacked, prewitt2_t)
    
    Ex = Ex[2:m - 2, 2:n-2];
    Ey = Ey[2:m - 2, 2:n-2];
    Et = Et[2:m - 2, 2:n-2, 2];
    
    xv, yv = np.linspace(-n / 2, n / 2, n - 4), np.linspace(-m / 2, m / 2, m - 4)
    x = np.asarray([[j for i in xv] for j in yv])
    y = np.asarray([[i for i in xv] for j in yv])

    GG = np.multiply(Ex, x) / (DIVIDE_GG) + np.multiply(Ey, y) / (DIVIDE_GG)
    
    E = np.stack([Ex.reshape(-1), Ey.reshape(-1), GG.reshape(-1)]).T
    
    # TODO: Solve in other ways
    #v, mse, rank, s = np.linalg.lstsq(E, -Et.reshape(-1))
       
    Ex2 = Ex**2
    Ey2 = Ey**2
    GG2 = GG**2
    ExEy = np.multiply(Ex, Ey)
    GEx = np.multiply(GG, Ex)
    GEy = np.multiply(GG, Ey)

    ExEt = np.multiply(Ex, Et)
    EyEt = np.multiply(Ey, Et)
    GEt = np.multiply(GG, Et)
    
    A = np.array([
            [Ex2.sum(), ExEy.sum(), GEx.sum()],
            [ExEy.sum(), Ey2.sum(), GEy.sum()],
            [GEx.sum(), GEy.sum(), GG2.sum()],
        ])
    b = np.array([
            [-ExEt.sum()],
            [-EyEt.sum()],
            [-GEt.sum()]
        ])
    
    v = np.matmul(np.linalg.inv(A), b)
    mse = 0

    # compile results
    x0 = -v[0] / v[2]; #foe x
    y0 = -v[1] / v[2]; #foe y
    T = 1 / v[2];      #ttc
    
    return T, x0, y0, Ex, Ey, Et, v, mse

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=str, default='test.mp4',
                        help='Source video')
    parser.add_argument('--dst', type=str, default='T.npy',
                        help='Target TTC.npy')
    parser.add_argument('--size', type=int, default=5)
    parser.add_argument('--vis', action='store_true', default=False)
    args = parser.parse_args()


    Ts = []
    for img1, img2 in load_video(args.src):
        n, m = img1.shape
        bimg1, bimg2 = uniform_blur(img1, args.size), uniform_blur(img2, args.size)
        
        T, x0, y0, Ex, Ey, Et, v, mse = solve_ttc(bimg1, bimg2) 

        if args.vis:
            cv2.imshow('bimg1', bimg1.astype(np.uint8))
            cv2.imshow('bimg2', bimg2.astype(np.uint8))       
            cv2.imshow('img1', img1.astype(np.uint8))
            cv2.imshow('img2', img2.astype(np.uint8))
            cv2.imshow('Ex', Ex.astype(np.uint8))
            cv2.imshow('Ey', Ey.astype(np.uint8))
            cv2.imshow('Et', Et.astype(np.uint8))      
            cv2.waitKey(0)
        print('T=', T, 'MSE=', mse)
        Ts.append(T)
    
    cv2.destroyAllWindows()  

    with open('{}'.format(args.dst), 'wb') as f:
        np.save(f, np.array(Ts))
