import argparse
import asyncio
import logging
import time

from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription
import requests
import platform
import os
import json

import cv2
import numpy as np
import websockets
from aiortc.contrib.media import MediaPlayer, MediaRelay
from aiortc.rtcrtpsender import RTCRtpSender

from aiortc.contrib.media import MediaPlayer, MediaRelay
from aiortc.rtcrtpsender import RTCRtpSender
import open3d
class ControllerWRTC:
    TO_NAME = 'Robot'
    FROM_NAME = 'Controller'
    def __init__(self) -> None:
        self.dc = None;
        self.cur_frame = None;
        
        self.lc = RTCPeerConnection()
        self.alive = True

        self.ROOT = os.path.dirname(__file__)
        self.offer = None
    
    def alive(self)->bool:return self.alive;
    async def setup_callbacks(self):
        @self.lc.on("connectionstatechange")
        async def on_connectionstatechange():
            print("Connection state is %s", self.lc.connectionState)
            if self.lc.connectionState == "failed" or self.lc.connectionState == 'disconnected':  
                print("resetting state, connection was closed")
                alive = False
                await self.lc.close()
                self.__init__(); #reset class
                await self.run();
                
        @self.lc.on("icecandidate")
        async def on_icecandidate(e):
            print("SDP:", json.dumps(self.lc.localDescription, separators=(',', ':')))
            
        @self.lc.on("track")
        async def on_track(track):
            print("Receiving %s" % track.kind)
            self.cur_frame = track        
            
            print("done")
            #lc.getTransceivers
            #lc.addTrack(e)
            
        @self.lc.on("datachannel")
        async def on_datachannel(e):
            print("Dc established")
            self.dc = e
            
            self.dc.send("keydown:KeyA")
            self.dc.send("keyup:KeyA")
            @self.dc.on("message")
            async def on_message(msg):   
                print("from robot:", msg)
            @self.dc.on("open")
            async def on_open():    
                print("Data Channel Connection opened on remote")
            
            

    async def rgb2depth(self, frame):
        R = np.left_shift (np.bitwise_and(frame[:, :, 2], 0xf8).astype(np.uint16), 8)# 00000000 RRRRR000 -> RRRRR000 00000000
        G = np.left_shift (np.bitwise_and(frame[:, :, 1], 0xfc).astype(np.uint16), 3)# 00000000 GGGGGG00 -> 00000GGG GGG00000
        B = np.right_shift(np.bitwise_and(frame[:, :, 0], 0xf8).astype(np.uint16), 3)
        I = np.bitwise_or(R, G, B)
        return I

            

    async def depth2rgb(self, depth):
        return cv2.applyColorMap(np.sqrt(depth).astype(np.uint8), cv2.COLORMAP_HSV)




    async def generate_answer(self):
        #await setup_callbacks(lc, self.lc.dc)
        answer = await self.lc.createAnswer()
        await self.lc.setLocalDescription(answer)
        while True:
            print(f"icegatheringstate:{self.lc.iceGatheringState}")
            if self.lc.iceGatheringState == "complete":
                break
        req_body = {
            'type':self.lc.localDescription.type,
            'sdp':self.lc.localDescription.sdp,
            'from':ControllerWRTC.FROM_NAME,
            'to':ControllerWRTC.TO_NAME
        }

        return req_body
    async def set_offer(self, offer):
        await self.setup_callbacks()
        print("Setting offer")
        offer_wrapped = RTCSessionDescription(offer['sdp'], offer['type'])
        await self.lc.setRemoteDescription(offer_wrapped)
        
    async def run(self):
        print("Entered running loop")
        while(self.cur_frame is None): await asyncio.sleep(2)
        count = 0;
        while True:
            f = await self.cur_frame.recv()
            if not f:
                await asyncio.sleep(2)
            else:
                if count == 15 :
                    if not self.dc == None:
                        print("Dc send msg to robo xD")
                        self.dc.send('keydown:KeyA')
                        self.dc.send('keyup:KeyA')
                count = (count + 1) % 100
                
                
                np_frame = np.array(f.to_image())
                d_frame = await self.rgb2depth(np_frame)
                f_frame = await self.depth2rgb(d_frame)
                cv2.imshow('robo_view', f_frame)
                cv2.waitKey(1);

        print("Terminated")
