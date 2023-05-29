#!/usr/bin/env python

import asyncio
import json
import websockets
from websockets import WebSocketClientProtocol
import robot_rtc_helper
import config

server = f'ws://{config.server}:{config.ws_port}'
my_uid = -44
from_name = 'Robot'
to_name = 'Controller'
async def generate_offer(video_track):
    msg_dict = {
        'from':from_name,
        'to':to_name,
        "offer":"not here yet lmao",
        'uid' : my_uid,
        
    }
    
    offer_dict = await robot_rtc_helper.get_offer(video_track)
    if(my_uid != -44): 
        offer_dict['uid'] = my_uid
    msg = json.dumps(offer_dict, separators=(',', ':'))
    return msg
async def establish_connection(websocket):
    first_msg = json.dumps({
        'from':from_name
    }, separators=(',', ':'))
    await websocket.send(first_msg)
    
async def handle_message(websocket, message, video_track):
    global my_uid
    print("received:", message)
    # try:
    data = json.loads(message)
    if('uid' in data): my_uid = data['uid']
    if('request' in data):
        if(data['request'] == 'offer'):
            offer = await generate_offer(video_track)
            await asyncio.sleep(2)
            print("sending offer")
            await websocket.send(offer)
            print("sent")
        if(data['request'] == 'heartbeat'):
            await websocket.send(json.dumps({'from':'Robot','uid':my_uid,'heartbeat':'beating'}, separators=(',', ':')))
            
    if('type' in data and data['type'] == 'answer'):
        await robot_rtc_helper.set_answer(data)
    # except Exception as e:
    #     print('Error', e)
        
        

    
async def handle(video_track):
    async with websockets.connect(server) as websocket:
        try:
            await establish_connection(websocket)
            print("connection established, awaiting message")
            while True:
                await asyncio.sleep(1)
                message = await websocket.recv()
                await handle_message(websocket, message, video_track)
        except websockets.exceptions.ConnectionClosedError:
            print("Closed")
        
async def main(video_track):

    await handle(video_track)
    

# async def establish_connection():
#         return websocket

if __name__ == "__main__":
    my_uid = -44
    print("NO LONGER USABLE CAUSE WE HACKED IT")
    asyncio.run(main(None))