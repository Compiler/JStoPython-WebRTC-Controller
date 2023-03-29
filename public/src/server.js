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
app.get('/', function (req, res) {
    res.send('Hello World');
 })

 app.post('/post_offer_:uuid(*)', function (req, res) {
    console.log("submitted an offer")
    offer[`${req.params.uuid}`] = req.body
    console.log(offer)
    res.status(200).json({ success: true});
 })

 app.post('/post_answer_:uuid(*)', function (req, res) {
    console.log("submitted an answer")
    console.log(req.body)
    console.log(req.params.uuid)
    answer[`${req.params.uuid}`] = req.body
    console.log(answer)
    res.status(200).json({ success: true});
 })



app.get('/get_offer_:uuid(*)', function (req, res) {
    console.log("requested an offer")
    console.log("Return:",offer[`${req.params.uuid}`])
    res.status(200).send(offer[`${req.params.uuid}`]);
 })

app.get('/get_answer_:uuid(*)', function (req, res) {
    console.log("requested an answer")
    console.log(answer_[`${req.params.uuid}`])
    res.status(200).send(answer[`${req.params.uuid}`]);
 })


 app.get('/index.htm', function (req, res) {
    res.sendFile( __dirname + "/" + "index.htm" );
 })
var server = app.listen(8081, function () {
   var host = server.address().address
   var port = server.address().port
   console.log("Example app listening at http://%s:%s", host, port)
})