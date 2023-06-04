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


to_name = 'Robot'
from_name = 'Controller'
dc = None;
#stream = MediaPlayer()
tracks = []
cur_frame = None;
async def setup_callbacks(lc : RTCPeerConnection):
    @lc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s", lc.connectionState)
        if lc.connectionState == "failed":  
            stay_alive = False
            await lc.close()
        if lc.connectionState == 'disconnected':
            stay_alive = False
            
    @lc.on("icecandidate")
    async def on_icecandidate(e):
        print("SDP:", json.dumps(lc.localDescription, separators=(',', ':')))
        
    @lc.on("track")
    async def on_track(track):
        global cur_frame
        print("Receiving %s" % track.kind)
        cur_frame = track        
        
        print("done")
        #lc.getTransceivers
        #lc.addTrack(e)
        
    @lc.on("datachannel")
    async def on_datachannel(e):
        print("Dc established")
        global dc
        dc = e
        
        dc.send("keydown:KeyA")
        dc.send("keyup:KeyA")
        @dc.on("message")
        async def on_message(msg):   
            print("from robot:", msg)
        @dc.on("open")
        async def on_open():    
            print("Data Channel Connection opened on remote")
        
        

async def rgb2depth(frame):
    R = np.left_shift (np.bitwise_and(frame[:, :, 2], 0xf8).astype(np.uint16), 8)# 00000000 RRRRR000 -> RRRRR000 00000000
    G = np.left_shift (np.bitwise_and(frame[:, :, 1], 0xfc).astype(np.uint16), 3)# 00000000 GGGGGG00 -> 00000GGG GGG00000
    B = np.right_shift(np.bitwise_and(frame[:, :, 0], 0xf8).astype(np.uint16), 3)
    I = np.bitwise_or(R, G, B)
    return I

        

async def depth2rgb(depth):
    return cv2.applyColorMap(np.sqrt(depth).astype(np.uint8), cv2.COLORMAP_HSV)




lc = RTCPeerConnection()
stay_alive = True
from aiortc.contrib.media import MediaPlayer, MediaRelay
from aiortc.rtcrtpsender import RTCRtpSender

ROOT = os.path.dirname(__file__)
offer = None
async def generate_answer():
    #await setup_callbacks(lc, lc.dc)
    answer = await lc.createAnswer()
    await lc.setLocalDescription(answer)
    while True:
        print(f"icegatheringstate:{lc.iceGatheringState}")
        if lc.iceGatheringState == "complete":
            break
    req_body = {
        'type':lc.localDescription.type,
        'sdp':lc.localDescription.sdp,
        'from':from_name,
        'to':to_name
    }

    return req_body
async def set_offer(offer):
    await setup_callbacks(lc)
    print("Setting offer")
    offer_wrapped = RTCSessionDescription(offer['sdp'], offer['type'])
    await lc.setRemoteDescription(offer_wrapped)
    
import open3d
async def run():
    import cv2
    global dc
    global cur_frame
    print("Entered")
    while(cur_frame is None): await asyncio.sleep(2)
    count = 0;
    while True:
        f = await cur_frame.recv()
        if not f:
            await asyncio.sleep(2)
        else:
            if count == 15 :
                if not dc == None:
                    print("Dc send msg to robo xD")
                    dc.send('keydown:KeyA')
                    dc.send('keyup:KeyA')
            count = (count + 1) % 100
            
            
            np_frame = np.array(f.to_image())
            d_frame = await rgb2depth(np_frame)
            f_frame = await depth2rgb(d_frame)
            cv2.imshow('robo_view', f_frame)
            cv2.waitKey(1);

    print("Terminated")
    # while True:
    #     try:
    #     except Exception:
    #         return
    ...
    #cv2.imshow('view', )