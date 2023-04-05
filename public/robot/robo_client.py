import argparse
import asyncio
import logging
import time

from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription
import requests
import json

lc = RTCPeerConnection()
stay_alive = True

'''
async function send_offer(offer, client_id){
    fetch(`http://0.0.0.0:8081/post_offer_${client_id}`,
        {
            method: "POST", 
            mode: "cors", 
            headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin" : "*", 
            "Access-Control-Allow-Credentials" : true 
            },
            body: offer
    })
    .then((response) => response.json())
    .then((data) => console.log("DATA:", data));
}
'''

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
        'sdp':lc.localDescription.sdp
        }, separators=(',', ':'))
    await send_offer(req_body, 34)
    
    await asyncio.sleep(4)
    answer = await get_answer(34)
    answer = answer.json()
    answer_wrapped = RTCSessionDescription(answer['sdp'], answer['type'])
    await lc.setRemoteDescription(answer_wrapped)
    
    while True:
        #dc.send(json.dumps({"now": time.time() * 1000}))
        #await dc._RTCDataChannel__transport._data_channel_flush()
        #await dc._RTCDataChannel__transport._transmit()
        await asyncio.sleep(1)
    
if __name__ == "__main__":
    
    #asyncio.run(start(lc))
    # run event loop
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start(lc))
    except KeyboardInterrupt:
        pass
    finally:
        while(stay_alive):asyncio.run(asyncio.sleep(10))
        loop.run_until_complete(lc.close())