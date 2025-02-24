import cv2
import numpy as np


P_IMAGE = r'src\reincarnator\outputs\output_2025-02-22-00-04-10\images\1740153851-2452.png'

def add_noise(frame):
    noise = np.abs(np.random.normal(0, 15, frame.shape)).astype(np.uint8)
    noisy_frame = cv2.add(frame, noise)
    return noisy_frame

def color_bleeding(frame):
    # Split channels
    b, g, r = cv2.split(frame)
    # Blur and shift the red channel
    r = cv2.GaussianBlur(r, (5, 5), 0)
    r = cv2.warpAffine(r, np.float32([[1, 0, 2], [0, 1, 0]]), (r.shape[1], r.shape[0]))
    return cv2.merge([b, g, r])

def scan_lines(frame):
    height, width = frame.shape[:2]
    scan_line_interval = 2  # Adjust for thicker/thinner lines
    for y in range(0, height, scan_line_interval):
        frame[y:y+1, :] = frame[y:y+1, :] * 0.3  # Darken the line
    return frame

def chromatic_aberration(frame):
    b, g, r = cv2.split(frame)
    # Shift red and blue channels
    r_shifted = cv2.warpAffine(r, np.float32([[1, 0, 1], [0, 1, 0]]), (r.shape[1], r.shape[0]))
    b_shifted = cv2.warpAffine(b, np.float32([[1, 0, -1], [0, 1, 0]]), (b.shape[1], b.shape[0]))
    return cv2.merge([b_shifted, g, r_shifted])

def lower_resolution(frame, scale_factor=0.5):
    h, w = frame.shape[:2]
    small = cv2.resize(frame, (int(w * scale_factor), int(h * scale_factor)), interpolation=cv2.INTER_LINEAR)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

def apply_vhs_effect(frame):
    frame = lower_resolution(frame)
    frame = color_bleeding(frame)
    frame = chromatic_aberration(frame)
    frame = add_noise(frame)
    # frame = scan_lines(frame)
    return frame
    

if __name__ == '__main__':
    input = cv2.imread(P_IMAGE)
    res = apply_vhs_effect(input)
    cv2.imshow('', res)
    cv2.imwrite('output_image.jpg', res)
