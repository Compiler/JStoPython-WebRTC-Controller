#!/usr/bin/env python

import asyncio
import json
import websockets
from websockets import WebSocketClientProtocol
import cv2
from aiortc.contrib.media import MediaPlayer, MediaRelay, MediaRecorder
import cv2
from controller_webrtc_helper import ControllerWRTC
  


class ControllerSignaller:
    def __init__(self, server : str, webrtc_helper : ControllerWRTC):
        self.server = server
        self.webrtc_helper = webrtc_helper
        self.uid = -44

    async def establish_connection(self, websocket):
        first_msg = json.dumps({
            'from':ControllerWRTC.FROM_NAME
        }, separators=(',', ':'))
        await websocket.send(first_msg)

    async def handle_message(self, websocket, message):
        print("received:", message)
        try:
            data = json.loads(message)
            message_header = {"from": ControllerWRTC.FROM_NAME, "to": ControllerWRTC.TO_NAME}
            if('uid' in data): self.uid = data['uid']
            if(self.uid != -44): message_header['uid'] = self.uid
            if('request' in data):
                if(data['request'] == 'heartbeat'):
                    await websocket.send(json.dumps({'from':ControllerWRTC.FROM_NAME,'uid':self.uid,'heartbeat':'beating'}, separators=(',', ':')))
            
            if('sdp' in data):
                await self.webrtc_helper.set_offer(data)
                print("Generating answer as implicit response to an offer")
                answer = await self.webrtc_helper.generate_answer()
                message_header['type']=answer['type']
                message_header['sdp']=answer['sdp']
                message_header = json.dumps(message_header, separators=(',', ':'))
                await asyncio.sleep(2)
                print("sending answer")
                await websocket.send(message_header)
                print("sent")
                    
        except Exception as e:
            print('Error', e)
            
            

        
    async def handle(self):
        async with websockets.connect(self.server) as websocket:
            try:
                await self.establish_connection(websocket)
                print("connection established, awaiting message")
                while True:
                    await asyncio.sleep(1)
                    message = await websocket.recv()
                    await self.handle_message(websocket, message)
            except websockets.exceptions.ConnectionClosedError:
                print("Closed")





        
        