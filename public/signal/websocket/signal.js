


let ws = new WebSocket("ws://localhost:4000")
ws.onopen = o =>{
    ws.send(JSON.stringify({'user':'Controller'}))
    console.log("Opened connection")
}

function send_answer(msg, client_id){
    ws.send(msg)
}

count = 0
ws.onmessage = msg => {
    console.log("Got message")
    console.log(msg.data)
    count += 1
    console.log(count)
    if(count > 1){
        get_offer_and_send(msg.data)
        console.log("Sending answer")
    }

} //first message in will be an offer