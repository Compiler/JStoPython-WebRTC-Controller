import argparse
import asyncio
import logging
import time

from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription
import requests


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


async def start(lc : RTCPeerConnection):
    dc = lc.createDataChannel("input")
    dc.onmessage = lambda e : print("Message from robot:", e.data)
    dc.onopen = lambda e : print("Input connection opened")
    import json
    lc.onicecandidate = lambda e : print("SDP:", json.dumps(lc.localDescription, separators=(',', ':')))
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
    
    time.sleep(4)
    answer = await get_answer(34)
    answer = answer.json()
    answer_wrapped = RTCSessionDescription(answer['sdp'], answer['type'])
    await lc.setRemoteDescription(answer_wrapped)
    
    
    print(f"Local: {str(lc.localDescription)}\nRemote: {lc.remoteDescription}")
    
if __name__ == "__main__":
    
    lc = RTCPeerConnection()
    asyncio.run(start(lc))