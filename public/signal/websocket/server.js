const http = require('http')
const { parse } = require('path')
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
    USERS = ['Robot', 'RemoteController']
    connection.on('message', msg=>{
        try{
            parsed = JSON.parse(msg.utf8Data)
            console.log("message from", parsed.user)
            USERS.array.forEach(user => {
                if(parsed.user != user)
                    console.error(`User '${parsed.user} not a valid user` )
            });
        }catch{
            console.log("Message is not JSON:", msg)
        }

    })


})

httpserver.listen(4000, () => console.log("server is listening"))