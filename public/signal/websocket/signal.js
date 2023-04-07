


let ws = new WebSocket("ws://localhost:4000")
ws.onopen = o =>{
    ws.send(JSON.stringify({'user':'RobotController'}))

}
ws.onmessage = msg => {
    console.log(msg.data)
    get_offer_and_send(msg.data)

} //first message in will be an offer