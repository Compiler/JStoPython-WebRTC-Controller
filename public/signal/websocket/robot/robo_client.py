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
    
    
async def send_offer(data, client_id):
    requests.post(
        url=f"http://0.0.0.0:8081/post_offer_{client_id}",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin" : "*", 
            "Access-Control-Allow-Credentials" : 'true ',
            "Mode":"cors"
            },)
    

async def get_answer(client_id):
    response = requests.get(
        url=f"http://0.0.0.0:8081/get_answer_{client_id}",
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin" : "*", 
            "Access-Control-Allow-Credentials" : 'true ',
            "Mode":"cors"
            },)
    return response

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
    dc = lc.createDataChannel("input")
    
    
    
    # open media source
    audio, video = create_local_tracks(
        None, decode=True
    )
    print("VIdeo:", video)
    if audio: audio_sender = lc.addTrack(audio)
    if video:
        video_sender = lc.addTrack(video)
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
        'user:':'Robot'
        }, separators=(',', ':'))
    
    
    #await send_offer(req_body, 34)
    
    answer = await send_and_get(req_body)
    
    #answer = await get_answer(34)
    answer = answer.json()
    answer_wrapped = RTCSessionDescription(answer['sdp'], answer['type'])
    await lc.setRemoteDescription(answer_wrapped)
    
    #task = asyncio.Task(start_cam())
    while True:
        #dc.send(json.dumps({"now": time.time() * 1000}))
        #await dc._RTCDataChannel__transport._data_channel_flush()
        #await dc._RTCDataChannel__transport._transmit()
        await asyncio.sleep(1)
    


async def conn():
    async with websockets.connect('ws://localhost:4000') as websocket:
            await websocket.send("hello")
            response = await websocket.recv()
            print(response)
async def send_and_get(msg):
    async with websockets.connect('ws://localhost:4000') as websocket:
            await websocket.send(msg)
            return await websocket.recv()
        
async def getconn():
    async with websockets.connect('ws://localhost:4000') as websocket:
            return websocket

if __name__ == "__main__":
    #asyncio.run(start(lc))
    # run event loop
    if(True):
        import websockets

        HOST = "localhost"  # The server's hostname or IP address
        PORT = 4000  # The port used by the server

        con = asyncio.run(conn())


    else:
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(start(lc))
        except KeyboardInterrupt:
            pass
        finally:
            #while(stay_alive):asyncio.run(asyncio.sleep(10))
            loop.run_until_complete(lc.close())