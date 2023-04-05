var fs = require('fs')
var express = require('express');
var bodyParser = require('body-parser');
var cors = require('cors')
var app = express();

offer = {}
answer = {}
app.use(bodyParser.urlencoded({ extended: false }))
app.use(express.static('public'));
app.use(bodyParser.json())
app.use(cors());

fs.appendFile('./session_', 'New Session ================\n', err=>{if(err) throw err})
app.get('/', function (req, res) {
    res.send('Hello World');
 })

 app.post('/post_offer_:uuid(*)', function (req, res) {
    //console.log("submitted an offer to server")
    fs.appendFile('./session_', `/post_offer_${req.params.uuid}\noffer[${req.params.uuid}] = ${JSON.stringify(req.body)}\n`, err=>{if(err) throw err})

    offer[`${req.params.uuid}`] = req.body
    console.log(offer)
    //console.log(req.params.uuid + ": " + req.body)
    res.status(200).json({ success: true});
 })

 app.post('/post_answer_:uuid(*)', function (req, res) {
    //console.log("submitted an answer")
    //console.log(req.body)
    //console.log(req.params.uuid)
    fs.appendFile('./session_', `/post_answer_${req.params.uuid}\nanswer[${req.params.uuid}] = ${JSON.stringify(req.body)}\n`, err=>{if(err) throw err})
    answer[`${req.params.uuid}`] = req.body
    //console.log(answer)
    res.status(200).json({ success: true});
 })



app.get('/get_offer_:uuid(*)', function (req, res) {
    //console.log("requested an offer")
    //console.log("Return:",offer[`${req.params.uuid}`])
    fs.appendFile('./session_', `/get_offer_${req.params.uuid}\nreturns: offer[${req.params.uuid}] = ${JSON.stringify(offer[`${req.params.uuid}`])}\n`, err=>{if(err) throw err})
    res.status(200).send(offer[`${req.params.uuid}`]);
 })

app.get('/get_answer_:uuid(*)', function (req, res) {
    //console.log("requested an answer")
    //console.log(answer[`${req.params.uuid}`])
    fs.appendFile('./session_', `/get_answer_${req.params.uuid}\nreturns: answer[${req.params.uuid}] = ${JSON.stringify(answer[`${req.params.uuid}`])}\n`, err=>{if(err) throw err})
    res.status(200).send(answer[`${req.params.uuid}`]);
 })


 app.get('/index.htm', function (req, res) {
    res.sendFile( __dirname + "/" + "index.htm" );
 })
var server = app.listen(8081, function () {
   var host = server.address().address
   var port = server.address().port
   //console.log("Example app listening at http://%s:%s", host, port)
})