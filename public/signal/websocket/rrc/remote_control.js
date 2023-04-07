
function addConnectionStateHandler(peerConnection) {
    peerConnection.onconnectionstatechange = function () {
        console.log("State:",peerConnection.connectionState)
        switch(peerConnection.connectionState){
            case "connected": {
                document.addEventListener('keydown', (event) => {
                    var key = event.key;
                    var code = event.code;
                    console.log("Sending:", code)
                    rc.dc.send(code)
                  }, false);
                break;
            }

            case "disconnected":{
                document.removeEventListener('keydown')
                break;
            }
        }
    };
}

let rc = undefined;
async function start(){
    rc = new RTCPeerConnection() //remote connection
    addConnectionStateHandler(rc)

    vp2 = document.getElementById('robot-view')
    remoteStream = new MediaStream()//setup the MediaStream, add the data from remote later
    vp2.srcObject = remoteStream
    vp2.addEventListener('loadedmetadata', () =>{
        vp2.play()
    })
    vp2.append(remoteStream)

    rc.ontrack = e=>{
        e.streams[0].getTracks().forEach(track => remoteStream.addTrack(track))
    }
    rc.onicecandidate = e => {
        console.log("SDP:", JSON.stringify(rc.localDescription))
        send_answer(JSON.stringify(rc.localDescription), 34) //3
    }
    rc.ondatachannel = e =>{
        rc.dc = e.channel
        rc.dc.onmessage = e =>{
            console.log("from remote controller", e.data)
        }
        rc.dc.onopen = e=> console.log("Data Channel Connection opened on remote")
    }



    
}


async function get_offer_and_send(offer){
    console.log("received offer:",offer);
    await rc.setRemoteDescription(JSON.parse(offer))
    console.log("offer set on remote, need to send answer")
    answer = await rc.createAnswer()
    rc.setLocalDescription(answer);
    await waitForAllICE(rc)//
    console.log("sending answer:", JSON.stringify(rc.localDescription))
    await send_answer(JSON.stringify(rc.localDescription), 34) //3
    console.log("Submitted answer")
}

start().then(a=>{
})

