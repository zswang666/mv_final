import numpy as np
import scipy
from scipy import signal
from scipy import misc
from scipy import ndimage

from skimage.util import view_as_blocks
import matplotlib.pyplot as plt
import cv2

# def _solve_ttc_julia(img1, img2):
#     # Julia copy
#     # m, n = img1.shape
#     # img_stacked = np.stack([img1, img2]).transpose([1, 2, 0])
#     # DIVIDE_EX = 16 / (n)
#     # DIVIDE_EY = 16 / (m)
#     # DIVIDE_ET = 4 / (min(n, m))
#     # DIVIDE_GG = 1

#     # sobel = np.array([
#     #         [-1, 0, 1],
#     #         [-2, 0, 2],
#     #         [-1, 0, 1]
#     #     ])

#     # sobel3_x = (1 / DIVIDE_EX) * np.stack([sobel, sobel]).transpose([1, 2, 0])
#     # sobel3_y = (1 / DIVIDE_EY) * np.stack([sobel.T, sobel.T]).transpose([1, 2, 0])

#     # prewitt2_t = (1 / DIVIDE_ET) * np.array([
#     #                                 [
#     #                                     [-1.0, -1.0], 
#     #                                     [-1.0, -1.0]
#     #                                 ], 
#     #                                 [
#     #                                     [1.0, 1.0], 
#     #                                     [1.0, 1.0]
#     #                                 ]
#     #                             ])

#     # Ex = ndimage.convolve(img_stacked, sobel3_x)
#     # Ey = ndimage.convolve(img_stacked, sobel3_y) 
#     # Et = ndimage.convolve(img_stacked, prewitt2_t)

#     # Ex = Ex[2:m - 2, 2:n - 2, 1]
#     # Ey = Ey[2:m - 2, 2:n - 2, 1]
#     # Et = Et[2:m - 2, 2:n - 2, 1]
    
#     # xv, yv = np.linspace(-n / 2, n / 2, n - 4), np.linspace(-m / 2, m / 2, m - 4)
#     # x = np.asarray([[j for j in xv] for i in yv])
#     # y = np.asarray([[i for j in xv] for i in yv])

#     # GG = np.multiply(Ex, x) / (DIVIDE_GG) + np.multiply(Ey, y) / (DIVIDE_GG) 
    
#     # # Original method
#     # #E = np.stack([Ex.reshape(-1), Ey.reshape(-1), GG.reshape(-1)]).transpose([1, 0])
#     # #v, residual, rank, s = np.linalg.lstsq(E, -Et.reshape(-1))

#     # v = _solve_v(Ex, Ey, Et, GG)

#     # print('v=', v)
#     # x0 = -v[0] / v[2]; #foe x
#     # y0 = -v[1] / v[2]; #foe y
#     # T = 1 / v[2];      #ttc
    
#     # return T, x0, y0, Ex, Ey, Et, v

# def uniform_blur_julia(img, n):
#     # f = np.ones((n, n)) / (n**2)
#     # g = ndimage.convolve(img, f)
#     # g = g[n-1: g.shape[0] - n, n-1:g.shape[1] - n]
#     # return g

def make_even_size(img, k=2):
    height, width = img.shape
    
    if (height % k):
        height += height % k

    if (width % k):
        width += width % k
    
    resized_img = cv2.resize(img, (width, height)) 
   
    return resized_img

def rgb2gray(img):
    return np.mean(img, axis=-1)

def uniform_blur(img, n):
    return ndimage.uniform_filter(img, size=n)

def restrict(f, k=2):
    if k == 1:
        return f
    block_shape = (k, k)
    view = view_as_blocks(make_even_size(f), block_shape)
    flatten_view = view.reshape(view.shape[0], view.shape[1], -1)
    mean_view = np.mean(flatten_view, axis=2)
    return mean_view

def load_video(filename):
    cap = cv2.VideoCapture(filename)
    while(cap.isOpened()):
        ret, frame = cap.read()
        
        if frame is None:
            break
        frame = rgb2gray(frame)      
        yield frame
    cap.release()

def _solve_v(Ex, Ey, Et, GG):
    Ex2 = np.multiply(Ex, Ex)
    Ey2 = np.multiply(Ey, Ey)
    GG2 = np.multiply(GG, GG)
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

    return v

def _compute_Ex(E):
    Ex = np.zeros_like(E)
    m, n = E.shape
    for i in range(m - 1):
        for j in range(n):
            Ex[i][j] = E[i + 1][j] - E[i][j]
    return Ex

def _compute_Ey(E):
    Ey = np.zeros_like(E)
    m, n = E.shape
    for i in range(m):
        for j in range(n - 1):
            Ey[i][j] = E[i][j + 1] - E[i][j]
    return Ey

def _compute_Et(E1, E2):
    return E2 - E1

def _compute_G(Ex, Ey):
    m, n = Ex.shape
    G = np.zeros_like(Ex)
    ci, cj = m // 2, n // 2
    for i in range(m):
        for j in range(n):
            G[i][j] = (i - ci) * Ex[i][j] + (j - cj) * Ey[i][j]
    return G

def solve_ttc(img1, img2):
    Ex = restrict(_compute_Ex(img2), 1)
    Ey = restrict(_compute_Ey(img2), 1)
    Et = restrict(_compute_Et(img1, img2), 1)
    G = _compute_G(Ex, Ey)
    v = _solve_v(Ex, Ey, Et, G)

    x0 = -v[0] / v[2]
    y0 = -v[1] / v[2]
    T = 1 / v[2]
    
    return T, x0, y0, Ex, Ey, Et, v


def solve_ttc_multiscale(img1, img2, size=2):
    T_n, x0_n, y0_n, EX_n, EY_n, ET_n, v_n = solve_ttc(img1, img2)
    T_p, x0_p, y0_p, EX_p, EY_p, ET_p, v_p = T_n, x0_n, y0_n, EX_n, EY_n, ET_n, v_n

    T_p = T_n + 1

    k = 0
    while T_p > T_n and T_n > 0:
        T_p, x0_p, y0_p, EX_p, EY_p, ET_p, v_p = T_n, x0_n, y0_n, EX_n, EY_n, ET_n, v_n

        img1_ = restrict(uniform_blur(img1, size))
        img2_ = restrict(uniform_blur(img2, size))
        
        if min(img1_.shape) <= 6:
            break        
        
        T_n, x0_n, y0_n, EX_n, EY_n, ET_n, v_n = solve_ttc(img1_, img2_)
        
        img1 = img1_
        img2 = img2_
        k += 1
    print('k=', k)
    return T_p, x0_p*k, y0_p*k, EX_p, EY_p, ET_p, v_p*k


if __name__ == '__main__':
    import argparse
    import matplotlib.pyplot as plt
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=str, default='test.mp4',
                        help='Source video')
    parser.add_argument('--dst', type=str, default='T.npy',
                        help='Target TTC.npy')
    parser.add_argument('--size', type=int, default=5)
    parser.add_argument('--vis', action='store_true', default=False)
    parser.add_argument('--use-multiscale', action='store_true', default=False)
    parser.add_argument('--filter-outlier', action='store_true', default=False)
    args = parser.parse_args()

    plt.gray()
    fig = plt.figure()
    ax1 = fig.add_subplot(331)  # left side
    ax2 = fig.add_subplot(332)  # right side
    ax3 = fig.add_subplot(333)  # right side
    ax4 = fig.add_subplot(334)  # right side
    ax5 = fig.add_subplot(335)  # right side
    ax6 = fig.add_subplot(336)  # right side

    Ts = []
    prev_frame = None
    FOE_marker = None
    for frame in load_video(args.src):
        frame = restrict(frame)
        m, n = frame.shape
        frame = uniform_blur(frame, args.size)

        if prev_frame is not None:
            if args.use_multiscale:
                T, x0, y0, Ex, Ey, Et, v = solve_ttc_multiscale(prev_frame, frame)
            else:
                T, x0, y0, Ex, Ey, Et, v = solve_ttc(prev_frame, frame)

            if args.filter_outlier and (T > 1e5 or T < 0):
               continue

            print('T=', T)
            Ts.append(T)

            if args.vis:
                ax1.imshow(Ex)
                ax2.imshow(Ey)
                ax3.imshow(Et)
                ax4.plot(Ts, color='b')
                ax5.imshow(prev_frame)
                ax6.imshow(frame)
                print('Image size=', frame.shape, 'FOE=', (x0+(n)/2, y0+(m)/2))
                
                if FOE_marker is not None:
                    FOE_marker.remove()
                FOE_marker = ax6.annotate('X', # this is the text
                            (x0+(n)/2, y0+(m)/2), # this is the point to label
                            textcoords="offset points", # how to position the text
                            xytext=(0,0), # distance from text to points (x,y)
                            color='r',
                            ha='center') 
                plt.draw()
                plt.pause(0.00001)
        
        prev_frame = frame

    with open('{}'.format(args.dst), 'wb') as f:
        np.save(f, np.array(Ts))
