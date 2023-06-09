// var data = {
//     "test_beg":"test_end"
// };
// var xhr = new XMLHttpRequest();
// xhr.open("POST","localhost:8081/client_44",true);
// xhr.setRequestHeader("Content-Type","application/json");
// xhr.send(data);
const stun_servers = {
    iceServers:[
        {
            urls:['stun:stun1.1.google.com:19302', 'stun:stun2.1.google.com:19302']
        }
    ]
}
function print_state(pc){
    console.log("Done:\nLocal:",JSON.stringify(pc.localDescription),'\nRemote:',JSON.stringify(pc.remoteDescription))

}
function waitForAllICE(peerConnection) {
    return new Promise((fufill, reject) => {
        peerConnection.onicecandidate = (iceEvent) => {
            if (iceEvent.candidate === null) fufill()
        }
        setTimeout(() => reject("Waited too long for ice candidates"), 10000)
    }) 
  }

async function send_offer(offer, client_id){
    fetch(`http://0.0.0.0:8081/post_offer_${client_id}`,
        {
            method: "POST", 
            mode: "cors", 
            headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin" : "*", 
            "Access-Control-Allow-Credentials" : true 
            },
            body: offer
    })
    .then((response) => response.json())
    .then((data) => console.log("DATA:", data));
}


async function send_answer(answer, client_id){
    fetch(`http://0.0.0.0:8081/post_answer_${client_id}`,
        {
            method: "POST", 
            mode: "cors", 
            headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : true 
                },
            body: answer
    })
    .then((response) => response.json())
    .then((data) => console.log(data));
}
async function get_answer(client_id){
    return fetch(`http://0.0.0.0:8081/get_answer_${client_id}`,
        {
            method: "GET", 
            mode: "cors", 
            redirect: 'follow',
            headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : true 
                },
    })
    .then((response) => response.json())
    //.then((data) => return data);
}


async function get_offer(client_id){
    var requestOptions = {
        'content-type': 'application/json',
         method: 'GET',
       };
    return await fetch(`http://0.0.0.0:8081/get_offer_${client_id}`,
    {
        method: "GET", 
        mode: "cors", 
        redirect: 'follow',
        headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin" : "*", 
            "Access-Control-Allow-Credentials" : true 
            },
    }).then(res => res.text())
    .catch((e) => console.log("FUCK",e))
   
    



}
