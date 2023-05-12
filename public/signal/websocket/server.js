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



ROBOT_JSON_NAME = "Robot"
CONTROLLER_JSON_NAME = "Controller"
uids = new Set();
connection_pairs = new Map();
class ConnectionPair{
    constructor(){
        this.uid = generate_uid()
        this.connections = new Map()
        this.beating = new Map()
        this.beating.set(ROBOT_JSON_NAME, false)
        this.beating.set(CONTROLLER_JSON_NAME, false)
        console.log("Created new connectionpair w/ uid " + this.uid)
    }

    get getUID(){return this.uid()}
    get getConnections(){return this.connections()}

    set_dead(){
        this.beating.set(ROBOT_JSON_NAME, false)
        this.beating.set(CONTROLLER_JSON_NAME, false)
    }
    is_beating(){return this.beating.get(ROBOT_JSON_NAME) && this.beating.get(CONTROLLER_JSON_NAME)}

}



function get_connectionpairs(user_type){
    looking_for = ""
    if(user_type == ROBOT_JSON_NAME) looking_for = CONTROLLER_JSON_NAME
    else looking_for = ROBOT_JSON_NAME
    available_connections = []
    for (let [uid, pairs] of connection_pairs) {
        if(pairs.connections.length == 2) continue;
        if(pairs.connections.has(looking_for) && !pairs.connections.has(user_type)){
            available_connections.push(pairs)
        }
    }
    return available_connections
}

function generate_uid(){
    last_uid = -1
    size = uids.size
    while(uids.size == size){
        last_uid = Math.floor(Math.random() * Math.pow(2, 30) - 1)
        uids.add(last_uid)
    }
    return last_uid
}

function begin_transaction(connection_pair){
    connection_pair.connections.get(ROBOT_JSON_NAME).send(JSON.stringify({'msg':"YOU ARE CONNECTED", 'uid':connection_pair.uid}))
    connection_pair.connections.get(CONTROLLER_JSON_NAME).send(JSON.stringify({'msg':"YOU ARE CONNECTED", 'uid':connection_pair.uid}))
    connection_pair.connections.get(ROBOT_JSON_NAME).send(JSON.stringify({'request':'offer'}))
}

function register_user(data, connection){
    check_heartbeats()

    conn_pairs_found = get_connectionpairs(data.from)
    connection_pair = null;
    console.log(conn_pairs_found.length)
    if(conn_pairs_found.length == 0) connection_pair = new ConnectionPair()
    else connection_pair = conn_pairs_found[0]

    connection_pairs.set(connection_pair.uid, connection_pair)
    connection_pairs.get(connection_pair.uid).connections.set(data.from, connection)
    connection_pairs.get(connection_pair.uid).beating.set(data.from, true)
    connection.send(JSON.stringify({'uid':connection_pair.uid, 'status':'success'}))
    console.log("ConnectionPair uid " + connection_pair.uid + " chosen")
    console.log("connections = " + connection_pair.connections.size)
    if(connection_pair.connections.size == 2) begin_transaction(connection_pair)
    print_active_connections()
}

function parse_message(data, connection){
    if(data.hasOwnProperty('from')){
        if(data.hasOwnProperty('uid')){
            if(connection_pairs.has(data.uid)){
                //min requirements met to start handling messages between two clients
                connection_pairs.get(data.uid).beating.set(data.from, true)
                if(data.hasOwnProperty('to')){
                    if(connection_pairs.get(data.uid).connections.has(data.to)){
                        pair = connection_pairs.get(data.uid)
                        pair.connections.get(data.to).send(JSON.stringify(data))
                    }
                }
            }else{
                //handle resetting member
                console.log("someone disconnected from this connection pair:", data)
            }
        }else{// no uid in message
            register_user(data, connection)
        }
    }else{
        console.log("no 'from' user specified:", data)
    }

    
}

last_heartbeat = -1
timeout = 10000
function check_heartbeats(){
    console.log("Checking heartbeats")
    for (let [uid, connection_pair] of connection_pairs) {
        if(!connection_pair.is_beating()){
            console.log("\t" + uid + ": Somethign not beatintg")
            robo_dead = false;
            ctrl_dead = false;
            console.log("\tRobo " + connection_pair.beating.get(ROBOT_JSON_NAME))
            console.log("\tCtrl " + connection_pair.beating.get(CONTROLLER_JSON_NAME))
            if(connection_pair.beating.get(ROBOT_JSON_NAME) == false && connection_pair.connections.has(ROBOT_JSON_NAME)){
                connection_pair.connections.delete(ROBOT_JSON_NAME)
                //console.log("\trobot is dead in " + connection_pair.uid)
            }
            if(connection_pair.beating.get(CONTROLLER_JSON_NAME) == false && connection_pair.connections.has(CONTROLLER_JSON_NAME)){
                connection_pair.connections.delete(CONTROLLER_JSON_NAME)
                //console.log("\tctrl is dead in " + connection_pair.uid)
            }
            if(connection_pair.beating.get(CONTROLLER_JSON_NAME) == false && connection_pair.beating.get(ROBOT_JSON_NAME) == false){
                console.log("\t pair is dead")
                uids.delete(uid)
                connection_pairs.delete(uid)
            }
        }

    }
    for (let [uid, connection_pair] of connection_pairs) {
        connection_pair.set_dead()
        for(let [user, connection] of connection_pair.connections){
            connection.send(JSON.stringify({'from':'admin', 'request':'heartbeat'}))
        }
    }

    print_active_connections()

}

function print_active_connections(){
    console.log("Connections:{")
    for (let [uid, connection_pair] of connection_pairs) {
        console.log("\t" + connection_pair.uid)
    }
    console.log("}")

}
websocket.on('request', req=>{
    print_active_connections()
    connection = req.accept(null, req.origin)//accept req for 101 upgrade from client
    connection.on('open', e=>{console.log("connection opened on server", e)})
    connection.on('close', e=>{
        console.log("connection close on server", e)
        //now check heartbeat of connection_pairs
        check_heartbeats()
    })
    connection.on('message', msg=>{
        try{
            data = JSON.parse(msg.utf8Data)
            console.log(data)
            if(!data.hasOwnProperty('from')){
                console.error("No 'from' user specified, discarding message:", data)
            }else{
                parse_message(data, connection)
            }
            
        }catch(err){
            console.log("Message is not JSON:", msg)
            console.log(err)
        }

    })


})

httpserver.listen(4000, () => console.log("server is listening"))