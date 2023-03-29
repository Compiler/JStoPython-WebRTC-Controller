// var data = {
//     "test_beg":"test_end"
// };
// var xhr = new XMLHttpRequest();
// xhr.open("POST","localhost:8081/client_44",true);
// xhr.setRequestHeader("Content-Type","application/json");
// xhr.send(data);



async function send_offer(offer, client_id){
    fetch(`http://0.0.0.0:8081/client_${client_id}`,
        {
            method: "POST", // *GET, POST, PUT, DELETE, etc.
            mode: "cors", 
            headers: {
            "Content-Type": "application/json",
            },
            body: offer
    })
    .then((response) => response.json())
    .then((data) => console.log(data));
}


async function send_answer(answer, client_id){
    fetch(`http://0.0.0.0:8081/answer_client_${client_id}`,
        {
            method: "POST", // *GET, POST, PUT, DELETE, etc.
            mode: "cors", 
            headers: {
            "Content-Type": "application/json",
            },
            body: answer
    })
    .then((response) => response.json())
    .then((data) => console.log(data));
}


async function get_users(){
    fetch(`http://0.0.0.0:8081/get_users`,
        {
            method: "GET", // *GET, POST, PUT, DELETE, etc.
            mode: "cors", 
            headers: {
            "Content-Type": "application/json",
            },
    })
    .then((response) => response.json())
    .then((data) => console.log(data));
}


send_offer('{"sdp":"hey u"}', 44)
send_answer('{"sdp":"hey u too bro"}', 44)
