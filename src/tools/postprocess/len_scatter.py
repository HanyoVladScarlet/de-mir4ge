import cv2
import numpy as np


P_IMAGE = r'src\reincarnator\outputs\output_2025-02-22-00-04-10\images\1740153851-2452.png'

def chromatic_aberration(img, shift_radius=3):
    # Split channels
    b, g, r = cv2.split(img)
    
    # Shift channels (adjust directions as needed)
    b_shifted = np.roll(b, shift_radius, axis=1)
    r_shifted = np.roll(r, -shift_radius, axis=1)
    
    # Merge shifted channels
    merged = cv2.merge([b_shifted, g, r_shifted])
    
    # Crop to remove black borders caused by shifting
    return merged[:, shift_radius:-shift_radius]


def add_lens_flare(img, center, radius=50, num_flares=6):
    h, w = img.shape[:2]
    flare = np.zeros((h, w, 3), dtype=np.uint8)
    
    # Create random flare positions around the center
    for _ in range(num_flares):
        angle = np.random.uniform(0, 2*np.pi)
        distance = np.random.randint(radius//2, radius*2)
        x = int(center[0] + distance * np.cos(angle))
        y = int(center[1] + distance * np.sin(angle))
        
        # Draw circles with random size and brightness
        size = np.random.randint(10, 50)
        brightness = np.random.randint(200, 255)
        cv2.circle(flare, (x, y), size, (brightness, brightness, brightness), -1)
    
    # Blur the flare for a glow effect
    flare = cv2.GaussianBlur(flare, (99, 99), 30)
    
    # Blend with original image
    result = cv2.addWeighted(img, 1, flare, 0.5, 0)
    return result

# Usage
image = cv2.imread(P_IMAGE)
effect = chromatic_aberration(image)
cv2.imshow("Chromatic Aberration", effect)
cv2.waitKey(0)
center = (300, 200)  # Adjust based on your image
result = add_lens_flare(image, center)
cv2.imshow("Lens Flare", result)
cv2.waitKey(0)