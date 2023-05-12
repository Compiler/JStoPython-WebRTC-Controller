


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
    if(data.hasOwnProperty('uid')) uid = data.uid
    send_msg = {
        'from':'Controller'
    }
    if(uid != -44)
    send_msg['uid'] = uid
    ws.send(JSON.stringify(send_msg))
    //if(data.hasOwnProperty('')){
    if(count > 1){
        //get_offer_and_send(msg.data)
        console.log("Sending answer")
    }

} //first message in will be an offer