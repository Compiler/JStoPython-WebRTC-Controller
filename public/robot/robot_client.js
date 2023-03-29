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
async function start() {
  const peerConnection = initializeBeforeReceivingOffer()
  await receiveOfferSDP(peerConnection)
  await sendAnswerSDP(peerConnection)
}

function initializeBeforeReceivingOffer() {
  const peerConnection = new RTCPeerConnection()
  addConnectionStateHandler(peerConnection)
  return peerConnection
}

async function receiveOfferSDP(peerConnection) {
    remoteOfferString = await get_offer('34')
    console.log(remoteOfferString)
    // console.log(JSON.parse(remoteOfferString))
    // console.log(JSON.stringify(remoteOfferString))
    // inputted = "{"+JSON.stringify(remoteOfferString)+"}"
    // console.log(inputted)
    // remoteOfferString = prompt("Peer offer");
    const remoteOffer = new RTCSessionDescription(JSON.parse(remoteOfferString))
    await peerConnection.setRemoteDescription(remoteOffer)
}

async function sendAnswerSDP(peerConnection) {
  const localAnswer = await peerConnection.createAnswer()
  peerConnection.setLocalDescription(localAnswer)
  await waitForAllICE(peerConnection)
  const localAnswerWithICECandidates = peerConnection.localDescription
  console.log("localAnswerWithICECandidates:")
  console.log(JSON.stringify(localAnswerWithICECandidates))
}

start()