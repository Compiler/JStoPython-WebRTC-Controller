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

async def setup_callbacks(lc : RTCPeerConnection, dc):
    #dc.onmessage = lambda e : print("Message from robot:", e.data, e)

    @dc.on("message")
    def on_message(message):
        if isinstance(message, str):
            print(message)

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
        
        
        
        








lc = RTCPeerConnection()
stay_alive = True
from aiortc.contrib.media import MediaPlayer, MediaRelay
from aiortc.rtcrtpsender import RTCRtpSender

ROOT = os.path.dirname(__file__)
offer = None
def generate_answer():
    assert(offer is not None)
    
async def set_offer(offer):
    offer_wrapped = RTCSessionDescription(offer['sdp'], offer['type'])
    await lc.setRemoteDescription(offer_wrapped)