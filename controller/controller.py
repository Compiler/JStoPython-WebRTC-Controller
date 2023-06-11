#!/usr/bin/env python

import asyncio
from websockets import WebSocketClientProtocol
import cv2
from controller_webrtc_helper import ControllerWRTC
from signal_helper import ControllerSignaller

if __name__ == "__main__":
      
    server = 'ws://192.241.156.85:80'
    webrtc_helper = ControllerWRTC()
    signaller = ControllerSignaller(server, webrtc_helper)
      
    loop = asyncio.new_event_loop()
    created = True
    
    
    signaling_task = loop.create_task(signaller.handle())
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
    