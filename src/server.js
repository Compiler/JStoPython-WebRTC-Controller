var express = require('express');
var app = express();
offer = {}
answer = {}
app.use(express.json())
app.get('/', function (req, res) {
    res.send('Hello World');
 })

 app.post('/client_:uuid(*)', function (req, res) {
    console.log(req.body)
    console.log(req.params.uuid)
    offer[`client_${req.params.uuid}`] = req.body
    console.log({offer})
 })

 app.post('/answer_client_:uuid(*)', function (req, res) {
    console.log(req.body)
    console.log(req.params.uuid)
    answer[`client_${req.params.uuid}`] = req.body
    console.log({answer})
 })


 app.get('/active_users', function (req, res) {
    console.log({offer, answer})
 })
var server = app.listen(8081, function () {
   var host = server.address().address
   var port = server.address().port
   console.log("Example app listening at http://%s:%s", host, port)
})