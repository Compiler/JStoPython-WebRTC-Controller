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




async def handler(websocket):
    while True:
        try:
            message = await websocket.recv()
        except websockets.ConnectionClosedOK:
            break
        print(message)


async def main():
    async with websockets.serve(handler, 'ws://localhost:4000', 8001):
        print("Go")
        await asyncio.Future()  # run forever








lc = RTCPeerConnection()
stay_alive = True
from aiortc.contrib.media import MediaPlayer, MediaRelay
from aiortc.rtcrtpsender import RTCRtpSender

ROOT = os.path.dirname(__file__)


relay = None
webcam = None


def create_local_tracks(play_from, decode):
    global relay, webcam

    if play_from:
        player = MediaPlayer(play_from, decode=decode)
        return player.audio, player.video
    else:
        options = {"framerate": "30", "video_size": "640x480"}
        if relay is None:
            if platform.system() == "Darwin":
                webcam = MediaPlayer(
                    "default:none", format="avfoundation", options=options
                )
            elif platform.system() == "Windows":
                webcam = MediaPlayer(
                    "video=Integrated Camera", format="dshow", options=options
                )
            else:
                try:
                    webcam = MediaPlayer("/dev/video0", format="v4l2", options=options)
                except Exception:
                    webcam = MediaPlayer("/dev/video1", format="v4l2", options=options)
            relay = MediaRelay()
        return None, relay.subscribe(webcam.video)

def force_codec(lc, sender, forced_codec):
    kind = forced_codec.split("/")[0]
    codecs = RTCRtpSender.getCapabilities(kind).codecs
    transceiver = next(t for t in lc.getTransceivers() if t.sender == sender)
    transceiver.setCodecPreferences(
        [codec for codec in codecs if codec.mimeType == forced_codec]
    )
    
    

def channel_log(channel, t, message):
    print("channel(%s) %s %s" % (channel.label, t, message))
    



        
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
        
        
        
        
        
async def start(lc : RTCPeerConnection):
    websocket = await websockets.connect('ws://localhost:4000')
    handler(websocket)
        
    
    
    dc = lc.createDataChannel("input")
    
    
    from my_track import NumpyVideoTrack
    video_sender = lc.addTrack(NumpyVideoTrack())
    force_codec(lc, video_sender, 'video/h264')

    
    channel_log(dc, "-", "created by local party")

    await setup_callbacks(lc, dc)
    print(dc.event_names)
    #lc.onicecandidate = lambda e : print("SDP:", json.dumps(lc.localDescription, separators=(',', ':'))); 
    offer = await lc.createOffer()
    await lc.setLocalDescription(offer)
    while True:
        print(f"icegatheringstate:{lc.iceGatheringState}")
        if lc.iceGatheringState == "complete":
            break
    req_body = json.dumps({
        'type':lc.localDescription.type,
        'sdp':lc.localDescription.sdp,
        'client_id': 34,
        'user':"Robot",
        'to':"Controller"
        }, separators=(',', ':'))
    
    
    #await send_offer(req_body, 34)
    first_msg = json.dumps({
        'user':"Robot"
        }, separators=(',', ':'))
    await send(first_msg)
        
    #task = asyncio.Task(start_cam())
    while True:
        #dc.send(json.dumps({"now": time.time() * 1000}))
        #await dc._RTCDataChannel__transport._data_channel_flush()
        #await dc._RTCDataChannel__transport._transmit()
        await asyncio.sleep(1)
        

async def answers():
     async with websockets.connect('ws://localhost:4000') as websocket:
        answer = await websocket.recv()
        print("Answer:", answer)

async def send(msg):
     async with websockets.connect('ws://localhost:4000') as websocket:
        await websocket.send(msg)
        
        
async def conn():
    async with websockets.connect('ws://localhost:4000') as websocket:
        await websocket.send("hello")
        response = await websocket.recv()
        print(response)
        
async def send_and_get(msg):
    async with websockets.connect('ws://localhost:4000') as websocket:
        await websocket.send(msg)
        ans = await websocket.recv()
        print("got answer from socket:", ans)
        return ans

        
async def getconn():
    async with websockets.connect('ws://localhost:4000') as websocket:
            return websocket

if __name__ == "__main__":
    #asyncio.run(start(lc))
    # run event loop
    loop = asyncio.get_event_loop()
    try:
        asyncio.run(main())
        #loop.run_until_complete(start(lc))
    except KeyboardInterrupt:
        pass
    finally:
        #while(stay_alive):asyncio.run(asyncio.sleep(10))
        loop.run_until_complete(lc.close())