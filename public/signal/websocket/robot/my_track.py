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


from multiprocessing import RawArray, Lock
import ctypes
import numpy as np


AUDIO_PTIME = 0.020  # 20ms audio packetization
VIDEO_CLOCK_RATE = 90000
VIDEO_PTIME = 1 / 60  # 60fps
VIDEO_TIME_BASE = fractions.Fraction(1, VIDEO_CLOCK_RATE)

class DoubleFramebuffer:
  def __init__(self, width, height):
    self.height = height
    self.width = width
    self.bufs = [RawArray(ctypes.c_uint8, width * height * 3) for _ in range(2)]
    self.readidx = 0
    self.writeidx = 1
    self.lock = Lock()

    self.write_bufs = [np.frombuffer(buf, dtype=np.uint8)\
      .reshape((height, width, 3)) for buf in self.bufs]
    self.read_bufs = None

  def data(self):
    if self.read_bufs is None:
      self.read_bufs = [np.frombuffer(buf, dtype=np.uint8)\
        .reshape((self.height, self.width, 3)) for buf in self.bufs]

    self.lock.acquire()
    readidx = self.readidx
    buf = np.copy(self.read_bufs[readidx]).astype(np.uint8)
    self.lock.release()
    return buf

  def set(self, frame, dtype="color"):
    if dtype == "depth": # preset the data
      x = (frame * 1000.).astype(np.int32) # meters to mm
      h, w = x.shape
      x1 = np.right_shift(np.bitwise_and(x, 0x0000f800), 8).astype(np.uint8)
      x1 = np.bitwise_or(x1, np.random.randint(0x8, size=(h, w), dtype=np.uint8))   # 3 bit noise
      x2 = np.right_shift(np.bitwise_and(x, 0x000007e0), 3).astype(np.uint8)
      x2 = np.bitwise_or(x2, np.random.randint(0x4, size=(h, w), dtype=np.uint8))   # 2 bit noise
      x3 = np.left_shift (np.bitwise_and(x, 0x0000001f), 3).astype(np.uint8)
      x3 = np.bitwise_or(x3, np.random.randint(0x8, size=(h, w), dtype=np.uint8))   # 3 bit noise
      frame = np.concatenate((x1.reshape(h, w, 1), x2.reshape(h, w, 1), x3.reshape(h, w, 1)), axis=-1)

    if frame is not None and isinstance(frame, np.ndarray) and \
        frame.shape == (self.height, self.width, 3):
      self.lock.acquire()
      writeidx = self.writeidx
      self.lock.release()
      np.copyto(self.write_bufs[writeidx], frame)
      self.lock.acquire()
      self.writeidx, self.readidx = self.readidx, self.writeidx
      self.lock.release()

class NumpyVideoTrack(VideoStreamTrack):
    
    kind = "video"

    _start: float
    _timestamp: int

    def __new__(cls): # use singleton to store DoubleBuffer item on precall
        if not hasattr(cls, 'instance'):
            cls.instance = super(NumpyVideoTrack, cls).__new__(cls)
        return cls.instance

    def __init__(self, w, h) -> None:
        super().__init__()
        self.buf = DoubleFramebuffer(w, h)
    
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
        """
        frame = self.buf.data()

        if frame is not None:
            frame = VideoFrame.from_ndarray(frame, format="bgr24")

            pts, time_base = await self.next_timestamp()
            frame.pts = pts
            frame.time_base = time_base
        else:
            frame = None
        return frame
