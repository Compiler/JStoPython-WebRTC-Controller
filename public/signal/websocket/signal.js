


let ws = new WebSocket("ws://localhost:4000")
ws.onopen = o =>{
    ws.send(JSON.stringify({'from':'Controller'}))
    console.log("Opened connection")
}

function send_answer(msg, client_id){
    ws.send(msg)
}

count = 0
uid = -44
ws.onmessage = msg => {
    console.log("Got message")
    console.log(msg.data)
    data = JSON.parse(msg.data)
    msg_header = {"from": 'Controller', 'to' : "Robot"}
    if(data.hasOwnProperty('uid')) uid = data.uid
    if(uid != -44)msg_header['uid'] = uid
    if(data.hasOwnProperty('sdp')){//respond to offer
        get_offer_and_send(msg.data).then(ans=>{
            console.log(ans)
            console.log(msg_header)
            answer = {msg_header, ans}
            msg_header['type'] = ans.type
            msg_header['sdp'] = ans.sdp
            ws.send(JSON.stringify(msg_header))
        })

    }else{
        console.log("Sending msg header")
        ws.send(JSON.stringify(msg_header))
    }
    //if(data.hasOwnProperty('')){
    //

} //first message in will be an offer