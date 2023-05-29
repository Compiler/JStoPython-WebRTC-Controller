#!/usr/bin/env python

import asyncio
import json
import websockets
from websockets import WebSocketClientProtocol
import cli_robot_rtc_helper
server = 'ws://192.241.156.85:80'
my_uid = -44
from_name = 'Controller'
to_name = 'Robot'
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

async def handle_message(websocket, message):
    global my_uid
    print("received:", message)
    try:
        data = json.loads(message)
        print("sdp in data?", 'sdp' in data)
        if('uid' in data): 
            my_uid = data['uid']
            print("Set uid to", my_uid)
        if('request' in data):
            if(data['request'] == 'answer'):
                print("Generating answer")
                answer = await cli_robot_rtc_helper.generate_answer()
                await asyncio.sleep(2)
                print("sending answer")
                await websocket.send(answer)
                print("sent")
            if(data['request'] == 'heartbeat'):
                await websocket.send(json.dumps({'from':from_name,'uid':my_uid,'heartbeat':'beating'}, separators=(',', ':')))
        
        elif('sdp' in data):
            if('type' in data and data['type'] == 'offer'):
                await cli_robot_rtc_helper.set_offer(data)
                print("Generating answer")
                answer = await cli_robot_rtc_helper.generate_answer()
                await asyncio.sleep(2)
                print("sending answer")
                await websocket.send(answer)
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
    

# async def establish_connection():
#         return websocket

if __name__ == "__main__":
    my_uid = -44
    asyncio.run(main())