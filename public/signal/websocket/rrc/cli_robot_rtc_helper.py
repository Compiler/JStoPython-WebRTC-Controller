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
        dc = e
        print("Dc established")
        dc.send("keydown:KeyA")
        dc.send("keyup:KeyA")
        @dc.on("message")
        async def on_message(e):    
            print("from robot:", e.data)
        @dc.on("open")
        async def on_open(e):    
            print("Data Channel Connection opened on remote")
        
        
        
        








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
    
async def run(buf):
    import cv2
    global cur_frame
    print("Entered")
    while(cur_frame is None): await asyncio.sleep(2)
    count = 0;
    while True:
        #try:
        f = await cur_frame.recv()
        #print("IN loop")
        if not f:
            await asyncio.sleep(2)
        else:
            #print("Running")
            i = np.array(f.to_image())
            if not dc == None:dc.send('keydown:KeyA')  
            if count == 15 and not dc == None:
                print("Send message")
                dc.send('keyup:KeyA')
            count = (count + 1) % 100
            print(count)
            #print(i.shape)
            buf[:] = i.flatten()
            #gray = np.ones((480, 640,  3), np.uint8) * 128
            #cv2.imshow('v', gray); cv2.waitKey(0);
            #cv2.imshow('view', i)
            #cv2.waitKey(1);
        # except Exception as e:
        #     print("error", e)
    print("Terminated")
    # while True:
    #     try:
    #     except Exception:
    #         return
    ...
    #cv2.imshow('view', )