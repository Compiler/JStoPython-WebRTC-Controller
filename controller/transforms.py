import numpy as np
import cv2
class Transforms: 
    
    async def rgb2depth(frame):
            R = np.left_shift (np.bitwise_and(frame[:, :, 2], 0xf8).astype(np.uint16), 8)# 00000000 RRRRR000 -> RRRRR000 00000000
            G = np.left_shift (np.bitwise_and(frame[:, :, 1], 0xfc).astype(np.uint16), 3)# 00000000 GGGGGG00 -> 00000GGG GGG00000
            B = np.right_shift(np.bitwise_and(frame[:, :, 0], 0xf8).astype(np.uint16), 3)
            I = np.bitwise_or(R, G, B)
            return I

    async def depth2rgb(depth):
        return cv2.applyColorMap(np.sqrt(depth).astype(np.uint8), cv2.COLORMAP_HSV)