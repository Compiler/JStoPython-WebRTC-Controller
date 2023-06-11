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
from signal_helper import RobotSignaller
from aiortc.contrib.media import MediaPlayer, MediaRelay
from aiortc.rtcrtpsender import RTCRtpSender
class RobotWRTC:
    
    def __init__(self, video_track, keyboard_values) -> None:

        self.ROOT = os.path.dirname(__file__)
        self.keyboard_values = keyboard_values
        self.video_track = video_track
        self.dc = None

        self.lc = RTCPeerConnection()
        self.alive = True


    def _reset_(self):
        self.dc = None
        self.lc = RTCPeerConnection()
        self.alive = True 

    def send_msg_to_client(self, msg): 
        if self.dc: self.dc.send(msg)

    async def setup_callbacks(self):
        #dc.onmessage = lambda e : print("Message from robot:", e.data, e)

        @self.dc.on("message")
        def on_message(message):
            if isinstance(message, str) and self.keyboard_values is not None:
                print("recvd event: ", message)
                event, data = message.split(":")
                ch = ord(data[3])
                self.keyboard_values.acquire()
                if event in ["keydown", "keyup"]:
                    self.keyboard_values[ch] = int(len(event) > 6)
                self.keyboard_values.release()
                self.send_msg_to_client("key received")

        @self.lc.on("connectionstatechange")
        async def on_connectionstatechange():
            print("Connection state is %s", self.lc.connectionState)
            if self.lc.connectionState == "failed" or self.lc.connectionState == 'disconnected':
                self.alive = False
                await self.lc.close()
                self._reset_()
                
        @self.lc.on("icecandidate")
        async def on_icecandidate(e):
            print("SDP:", json.dumps(self.lc.localDescription, separators=(',', ':')))
            
            
            
            


    def force_codec(self, sender, forced_codec):
        kind = forced_codec.split("/")[0]
        codecs = RTCRtpSender.getCapabilities(kind).codecs
        transceiver = next(t for t in self.lc.getTransceivers() if t.sender == sender)
        transceiver.setCodecPreferences(
            [codec for codec in codecs if codec.mimeType == forced_codec]
        )
        
        

    def channel_log(self, channel, t, message):
        print("channel(%s) %s %s" % (channel.label, t, message))
        


    async def set_answer(self, answer):
        answer_wrapped = RTCSessionDescription(answer['sdp'], answer['type'])
        await self.lc.setRemoteDescription(answer_wrapped)

    async def get_offer(self):
        self.dc = self.lc.createDataChannel("input")
        self.channel_log(self.dc, "-", "created by local party")


        # from .my_track import NumpyVideoTrack
        video_sender = self.lc.addTrack(self.video_track)
        self.force_codec(self.lc, video_sender, 'video/h264')

        await self.setup_callbacks()
        # print(self.dc.event_names)
        #self.lc.onicecandidate = lambda e : print("SDP:", json.dumps(self.lc.localDescription, separators=(',', ':'))); 
        offer = await self.lc.createOffer()
        await self.lc.setLocalDescription(offer)
        while True:
            print(f"icegatheringstate:{self.lc.iceGatheringState}")
            if self.lc.iceGatheringState == "complete":
                break
        req_body = {
            'type':self.lc.localDescription.type,
            'sdp':self.lc.localDescription.sdp,
            'from':RobotSignaller.FROM_NAME,
            'to':RobotSignaller.TO_NAME
            }
        
        return req_body
        
