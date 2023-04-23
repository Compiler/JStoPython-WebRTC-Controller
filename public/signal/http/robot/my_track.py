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
VIDEO_PTIME = 1 / 30  # 30fps
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

    async def recv(self) -> Frame:
        """
        Receive the next :class:`~av.video.frame.VideoFrame`.

        The base implementation just reads a 640x480 green frame at 30fps,
        subclass :class:`VideoStreamTrack` to provide a useful implementation.
        """
        import numpy as np
        import os
        import cv2
        x = np.load(f'{os.path.dirname(__file__)}/../../../../data/data/depth/0.npy')
        y = cv2.applyColorMap(np.sqrt(x).astype(np.uint8), cv2.COLORMAP_HSV)
        a = np.ones((512, 256, 3)).astype(int)*255
        pts, time_base = await self.next_timestamp()

        #frame = VideoFrame(width=360, height=640)
        
        frame = VideoFrame(width=360, height=640)
        frame = VideoFrame.from_ndarray(a)
        
        #frame = VideoFrame.from_ndarray(a, format='rgb32')
        for p in frame.planes: p.update(bytes(p.buffer_size))
        frame.pts = pts
        frame.time_base = time_base
        return frame
