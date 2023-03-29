
const CHAT_CHANNEL = "chat"

function waitForAllICE(peerConnection) {
    return new Promise((fufill, reject) => {
        peerConnection.onicecandidate = (iceEvent) => {
            if (iceEvent.candidate === null) fufill()
        }
        setTimeout(() => reject("Waited too long for ice candidates"), 1000)
    }) 
  }

function addConnectionStateHandler(peerConnection) {
    peerConnection.onconnectionstatechange = function () {
        console.log("State:",peerConnection.connectionState)
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
    console.log(localOffer)
    //send_offer(localOffer, 34)
    await peerConnection.setLocalDescription(localOffer)
    await waitForAllICE(peerConnection)
    const localOfferWithICECandidates = peerConnection.localDescription
    console.log("localOfferWithICECandidates:")
    console.log(JSON.stringify(localOfferWithICECandidates))
  }
async function receiveAnswerSDP(peerConnection) {
    console.log("Will wait for answer")
    const remoteAnswerString = prompt("Peer answer");
    const remoteAnswer = JSON.parse(remoteAnswerString)
    peerConnection.setRemoteDescription(remoteAnswer)
  }
async function start(){
    const peerConnection = initializeBeforeCreatingOffer()
    await prepareOfferSDP(peerConnection)
    await receiveAnswerSDP(peerConnection)
}

start()
