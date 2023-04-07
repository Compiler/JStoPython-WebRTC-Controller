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

    connection.on('message', msg=>{
        console.log("Message from peer:", msg)
    })

    connection.send("hello")

})

httpserver.listen(4000, () => console.log("server is listening"))