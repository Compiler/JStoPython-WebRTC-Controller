const http = require('http')
const WebSocketServer = require('websocket').server
let connection = null

const httpserver = http.createServer((req, res)=>{
    console.log("request received")
})

const websocket = new WebSocketServer({
    "httpServer":httpserver,//handshake
})

websocket.on('request', req=>{
    connection = req.accept(null, req.origin)//accept req for 101 upgrade from client
    connection.on('open', e=>{console.log("connection opened on server")})
    connection.on('close', e=>{console.log("connection close on server")})
    const KEY = 'User:'
    connection.on('message', msg=>{
        try{
            msg = JSON.parse(msg.utf8Data)
        }catch{
            console.log("Message is not JSON:", msg)
        }

    })


})

httpserver.listen(4000, () => console.log("server is listening"))