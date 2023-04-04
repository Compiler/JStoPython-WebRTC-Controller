import argparse
import asyncio
import logging
import time

from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription



async def start(lc):
    dc = lc.createDataChannel("input")
    dc.onmessage = lambda e : print("Message from robot:", e.data)
    dc.onopen = lambda e : print("Input connection opened")
    import json
    lc.onicecandidate = lambda e : print("SDP:", json.dumps(lc.localDescription, separators=(',', ':')))
    offer = await lc.createOffer()
    lc.setLocalDescription(offer)
    
if __name__ == "__main__":
    
    lc = RTCPeerConnection()
    asyncio.run(start(lc))