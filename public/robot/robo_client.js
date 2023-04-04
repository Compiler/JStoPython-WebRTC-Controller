


let lc = undefined;
let dc = undefined;
async function start(){
    lc = new RTCPeerConnection()//local connection
    dc = lc.createDataChannel("input")
    dc.onmessage = e => console.log("Message from robot:", e.data)
    dc.onopen = e => console.log("Connection opened!!")
    lc.onicecandidate = e => console.log("SDP:", JSON.stringify(lc.localDescription))
    lc.onconnectionstatechange = function () {
        console.log("State:",lc.connectionState)
    };

    offer = await lc.createOffer()// 1.
    lc.setLocalDescription(offer)
    console.log("waiting for ice")
    await waitForAllICE(lc)//
    console.log("done")
    console.log("Submitting offer:", JSON.stringify(lc.localDescription))
    send_offer(JSON.stringify(lc.localDescription), 34).then(a => console.log("Set local description"))
        
    ans = prompt("waiting")
    answer = await get_answer(34)//4d
    await lc.setRemoteDescription(answer)
    console.log("Set answer:",JSON.stringify(answer))//d

    console.log("Done")
//


  

}

start().then(a=>{
    print_state(lc)
})//d