#!/usr/bin/env python

import asyncio
import json
import websockets
from websockets import WebSocketClientProtocol
import cv2
server = 'ws://192.241.156.85:80'
my_uid = -44
from_name = 'Controller'
to_name = 'Robot'
from aiortc.contrib.media import MediaPlayer, MediaRelay, MediaRecorder


async def establish_connection(websocket):
    first_msg = json.dumps({
        'from':from_name
    }, separators=(',', ':'))
    await websocket.send(first_msg)

async def handle_message(websocket, message):
    global my_uid
    print("received:", message)
    try:
        data = json.loads(message)
        message_header = {"from": from_name, "to": to_name}
        if('uid' in data): my_uid = data['uid']
        if(my_uid != -44): message_header['uid'] = my_uid
        if('request' in data):
            if(data['request'] == 'heartbeat'):
                await websocket.send(json.dumps({'from':from_name,'uid':my_uid,'heartbeat':'beating'}, separators=(',', ':')))
        
        if('sdp' in data):
            await webrtc_helper.set_offer(data)
            print("Generating answer as implicit response to an offer")
            answer = await webrtc_helper.generate_answer()
            message_header['type']=answer['type']
            message_header['sdp']=answer['sdp']
            message_header = json.dumps(message_header, separators=(',', ':'))
            await asyncio.sleep(2)
            print("sending answer")
            await websocket.send(message_header)
            print("sent")
                
    except Exception as e:
        print('Error', e)
        
        

    
async def handle():
    async with websockets.connect(server) as websocket:
        try:
            await establish_connection(websocket)
            print("connection established, awaiting message")
            while True:
                await asyncio.sleep(1)
                message = await websocket.recv()
                await handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosedError:
            print("Closed")

async def main():
    await handle()
    


  

import cv2
from controller_webrtc_helper import ControllerWRTC
webrtc_helper = ControllerWRTC()

if __name__ == "__main__":
    my_uid = -44
      
    loop = asyncio.new_event_loop()
    created = True
    signaling_task = loop.create_task(main())
    main_task = loop.create_task(webrtc_helper.run())

    if created:
        try:
            asyncio.set_event_loop(loop)
            loop.run_until_complete(signaling_task)
        except Exception as e:
            pass
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
    
    