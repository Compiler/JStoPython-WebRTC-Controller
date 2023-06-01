


import multiprocessing
from multiprocessing import RawArray
from multiprocessing import Process
import ctypes
import cv2

import cv2
import numpy as np
import websockets
screen_buffer = RawArray(ctypes.c_uint8, (480 * 640 * 3))

if __name__ == "__main__":
    my_uid = -44
    
    #process = Process(target=asyncworker, args=(screen_buffer,))
    
    #process.start()
    import numpy as np
    while True:
        print("HERE")
        cv2.imshow('this is NEVER going to work!', np.array(screen_buffer[:], np.uint8).reshape((480,640,3)))
        cv2.waitKey(1)