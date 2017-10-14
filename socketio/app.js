var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var resetX = 0;
var resetY = 0;
var event_x = 0;
var event_y = 0;

app.get('/', function(req, res) {
   res.sendfile('index.html');
});

//Whenever someone connects this gets executed
io.on('connection', function(socket) {
   console.log('A user connected');

   socket.on('buttonEvent', function(data) {
      console.log("Button: " + data);

      if(data == 8) {
        resetX = event_x;
        resetY = event_y;
      }
   });

   socket.on('rotationEvent', function(data) {
      console.log("Rotation: " + data);
   });

   //Whenever someone disconnects this piece of code executed
   socket.on('disconnect', function () {
      console.log('A user disconnected');
   });
});

http.listen(3000, function() {
   console.log('listening on *:3000');
});
