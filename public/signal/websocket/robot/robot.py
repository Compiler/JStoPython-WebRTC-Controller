#!/usr/bin/env python

import asyncio
import json
import websockets
from websockets import WebSocketClientProtocol
server = 'ws://localhost:4000'
my_uid = -44
from_name = 'Robot'
async def generate_offer():
    msg_dict = {
        'from':from_name,
        'to':'Controller',
        "offer":"not here yet lmao",
        'uid' : my_uid,
        
    }
    if(my_uid != -44): 
        msg_dict['uid'] = my_uid
    msg = json.dumps(msg_dict, separators=(',', ':'))
    return msg
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
        if('uid' in data):
            
            my_uid = data['uid']
        if('request' in data):
            if(data['request'] == 'offer'):
                offer = await generate_offer()
                await asyncio.sleep(2)
                print("sending offer")
                await websocket.send(offer)
                print("sent")
            if(data['request'] == 'heartbeat'):
                await websocket.send(json.dumps({'from':'Robot','uid':my_uid,'heartbeat':'beating'}, separators=(',', ':')))
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