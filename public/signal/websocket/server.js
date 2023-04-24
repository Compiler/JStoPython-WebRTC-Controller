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
class RobotResponder{
    connection = ""
    id = -1

}
ROBOT_JSON_NAME = "Robot"
CONTROLLER_JSON_NAME = "Controller"
USERS = [ROBOT_JSON_NAME, CONTROLLER_JSON_NAME]
user_map = new Map();
connections = []

offer = null
answer = null
websocket.on('request', req=>{

    connection = req.accept(null, req.origin)//accept req for 101 upgrade from client
    connections.push(connection)
    connection.on('open', e=>{console.log("connection opened on server")})
    connection.on('close', e=>{console.log("connection close on server")})
    connection.on('message', msg=>{
        try{
            data = JSON.parse(msg.utf8Data)
            if(!data.hasOwnProperty('user')){
                console.error("No user specified, discarding message")
            }else{
                if(user_map.has(data.user) == false){
                    user_map.set(data.user, connection)
                    console.log("mapped", data.user, "to a connection")
                    connection.send("Success")
                }
                console.log("message from", data.user)
                if(data.hasOwnProperty('to')){
                    if(user_map.has(data.to)){
                        console.log("sent msg from", data.user, 'to', data.to)
                        user_map.get(data.to).send(JSON.stringify(data))
                    }else{
                        console.log("couldnt send data to", data.to)
                    }
                }
            }
            
        }catch(err){
            console.log("Message is not JSON:", msg)
            console.log(err)
        }

    })


})

httpserver.listen(4000, () => console.log("server is listening"))