from aiortc.mediastreams import VideoStreamTrack
import asyncio
import fractions
import time
import uuid
from abc import ABCMeta, abstractmethod
from typing import Tuple, Union

from av import AudioFrame, VideoFrame
from av.frame import Frame
from av.packet import Packet
from pyee.asyncio import AsyncIOEventEmitter

AUDIO_PTIME = 0.020  # 20ms audio packetization
VIDEO_CLOCK_RATE = 90000
VIDEO_PTIME = 1 / 60  # 60fps
VIDEO_TIME_BASE = fractions.Fraction(1, VIDEO_CLOCK_RATE)

class NumpyVideoTrack(VideoStreamTrack):
    
    kind = "video"

    _start: float
    _timestamp: int
    
    async def next_timestamp(self) -> Tuple[int, fractions.Fraction]:
        if self.readyState != "live":
            raise Exception

        if hasattr(self, "_timestamp"):
            self._timestamp += int(VIDEO_PTIME * VIDEO_CLOCK_RATE)
            wait = self._start + (self._timestamp / VIDEO_CLOCK_RATE) - time.time()
            await asyncio.sleep(wait)
        else:
            self._start = time.time()
            self._timestamp = 0
        return self._timestamp, VIDEO_TIME_BASE
    count = 0
    async def recv(self) -> Frame:
        """
        Receive the next :class:`~av.video.frame.VideoFrame`.
        """
        import numpy as np
        import os
        import cv2
        def load_img(ind):
            try:
                x = np.load(f'{os.path.dirname(__file__)}/../../../../data/data/depth/{ind}.npy')
                x1 = np.bitwise_and(x, np.ones(x.shape, dtype=np.uint16) * 0xf800)
                x1 = np.right_shift(x1, np.ones(x.shape, dtype=np.int32) * 8).astype(np.uint8)
                x2 = np.bitwise_and(x, np.ones(x.shape, dtype=np.uint16) * 0x07e0)
                x2 = np.right_shift(x2, np.ones(x.shape, dtype=np.int32) * 3).astype(np.uint8)
                x3 = np.bitwise_and(x, np.ones(x.shape, dtype=np.uint16) * 0x001f)
                x3 = np.left_shift(x2, np.ones(x.shape, dtype=np.int32) * 3).astype(np.uint8)
                h, w = x.shape
                x = np.concatenate((x1.reshape(h, w, 1), x2.reshape(h, w, 1), x3.reshape(h, w, 1)), axis=-1)

                #x = ((x.astype(np.float32) / x.max()) * 255).astype(np.uint8)
                #x = np.tile(x.reshape((x.shape[0], x.shape[1], 1)), (1,1,3))
                
            except Exception as e:
                print(e)
            
            cv2.imshow('depth mask color', x)
            return x;
        pts, time_base = await self.next_timestamp()
        #frame = VideoFrame(width=360, height=640)
        #array = np.random.randint(100, 256, size=(480, 640, 3), dtype=np.uint8)
        #frame = VideoFrame.from_ndarray(array, format='bgr24')
        frame = VideoFrame.from_ndarray(load_img(0), format='rgb24')
        self.count += 1
        self.count = self.count % 5
        #for p in frame.planes: p.update(bytes(p.buffer_size))
        frame.pts = pts
        frame.time_base = time_base
        return frame
