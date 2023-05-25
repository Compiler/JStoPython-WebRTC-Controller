#!/usr/bin/env python

import asyncio
import json
import websockets
from websockets import WebSocketClientProtocol
import public.signal.websocket.rrc.cli_robot_rtc_helper as cli_robot_rtc_helper
server = 'ws://localhost:4000'
my_uid = -44
from_name = 'Robot'
to_name = 'Controller'
async def generate_offer():
    msg_dict = {
        'from':from_name,
        'to':to_name,
        "offer":"not here yet lmao",
        'uid' : my_uid,
        
    }
    
    offer_dict = await cli_robot_rtc_helper.get_offer()
    if(my_uid != -44): 
        offer_dict['uid'] = my_uid
    msg = json.dumps(offer_dict, separators=(',', ':'))
    return msg
async def establish_connection(websocket):
    first_msg = json.dumps({
        'from':from_name
    }, separators=(',', ':'))
    await websocket.send(first_msg)

from . import cli_robot_rtc_helper
async def handle_message(websocket, message):
    global my_uid
    print("received:", message)
    try:
        data = json.loads(message)
        if('uid' in data): my_uid = data['uid']
        if('request' in data):
            if(data['request'] == 'answer'):
                offer = await cli_robot_rtc_helper.generate_answer()
                await asyncio.sleep(2)
                print("sending offer")
                await websocket.send(offer)
                print("sent")
            if(data['request'] == 'heartbeat'):
                await websocket.send(json.dumps({'from':from_name,'uid':my_uid,'heartbeat':'beating'}, separators=(',', ':')))
                
        if('type' in data and data['type'] == 'offer'):
            await cli_robot_rtc_helper.set_offer(data)
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
    

# async def establish_connection():
#         return websocket

if __name__ == "__main__":
    my_uid = -44
    asyncio.run(main())