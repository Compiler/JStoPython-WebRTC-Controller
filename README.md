# WebRTC Controller

Use p2p connection to control robot through webcam input. 

## Warnings
- Nat translation cannot be symmetric
    - Destination ip/port pair will not match due to p2p connection, the pair will match signaling websocket/server
    - STUN server will not be able to send data back to user
    
- Server is local for now
- Production will require TURN server. This is dev setup
## How to use
- npm i
- Launch the server(for signaling)
- Point robot and rc controller to server
- Connect to same room to start controlling