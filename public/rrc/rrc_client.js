
const CHAT_CHANNEL = "chat"

function waitForAllICE(peerConnection) {
    return new Promise((fufill, reject) => {
        peerConnection.onicecandidate = (iceEvent) => {
            if (iceEvent.candidate === null) fufill()
        }
        setTimeout(() => reject("Waited too long for ice candidates"), 1000)
    }) 
  }
//type RTCPeerConnectionState = "closed" | "connected" | "connecting" | "disconnected" | "failed" | "new";
function addConnectionStateHandler(peerConnection) {
    peerConnection.onconnectionstatechange = function () {
        console.log("State:",peerConnection.connectionState)
        switch(peerConnection.connectionState){
            case "connected":
                alert("Connection Established");
                break;
            default:
                console.log("State:",peerConnection.connectionState)
                break;
                 
        }
    };
}

//```````````````
function initializeBeforeCreatingOffer() {
    const peerConnection = new RTCPeerConnection()
    addConnectionStateHandler(peerConnection)
    peerConnection.createDataChannel(CHAT_CHANNEL)
    return peerConnection
}
async function prepareOfferSDP(peerConnection) {
    const localOffer = await peerConnection.createOffer()
    console.log("Creating")
    console.log(localOffer)
    await send_offer(JSON.stringify({
        'type':'offer', 
        'sdp':localOffer.sdp
    }), 34)
    //await send_offer(localOffer, 34)
    await peerConnection.setLocalDescription(localOffer)
    await waitForAllICE(peerConnection)
    const localOfferWithICECandidates = peerConnection.localDescription
    console.log("localOfferWithICECandidates:")
    console.log(JSON.stringify(localOfferWithICECandidates))
  }
async function receiveAnswerSDP(peerConnection) {
    console.log("Will wait for answer")
    let remoteAnswerString = await get_answer('34')
    remoteAnswerString = JSON.stringify(remoteAnswerString)
    console.log(remoteAnswerString)
    remoteAnswerString = prompt("Peer answer");
    const remoteAnswer = JSON.parse(remoteAnswerString)
    console.log(remoteAnswer)
    peerConnection.setRemoteDescription(remoteAnswer)//d
  }
async function start(){
    const peerConnection = initializeBeforeCreatingOffer()
    await prepareOfferSDP(peerConnection)
    await receiveAnswerSDP(peerConnection)
}

start()
