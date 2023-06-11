#!/usr/bin/env python

import asyncio
import json
import websockets
from websockets import WebSocketClientProtocol
from . import config
from .robot_webrtc_helper import RobotWRTC
class RobotSignaller:

    def __init__(self, wrtc: RobotWRTC):
        self.server = f'ws://{config.server}:{config.ws_port}'
        self.uid = -44
        self.wrtc = wrtc
        
    async def generate_offer(self):
        msg_dict = {
            'from':config.FROM_NAME,
            'to':config.TO_NAME,
            "offer":"not here yet lmao",
            'uid' : self.uid,
            
        }
        
        offer_dict = await self.wrtc.get_offer()
        if(self.uid != -44): 
            offer_dict['uid'] = self.uid
        msg = json.dumps(offer_dict, separators=(',', ':'))
        return msg
    async def establish_connection(self, websocket):
        first_msg = json.dumps({
            'from':config.FROM_NAME
        }, separators=(',', ':'))
        await websocket.send(first_msg)
        
    async def handle_message(self, websocket, message):
        print("received:", message)
        # try:
        data = json.loads(message)
        if('uid' in data): self.uid = data['uid']
        if('request' in data):
            if(data['request'] == 'offer'):
                offer = await self.generate_offer()
                await asyncio.sleep(2)
                print("sending offer")
                await websocket.send(offer)
                print("sent")
            if(data['request'] == 'heartbeat'):
                await websocket.send(json.dumps({'from':'Robot','uid':self.uid,'heartbeat':'beating'}, separators=(',', ':')))
                
        if('type' in data and data['type'] == 'answer'):
            await self.wrtc.set_answer(data)
            
            

        
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

        
        