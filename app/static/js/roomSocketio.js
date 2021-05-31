//socketio method go here
var socket = io();
if (!socket.connected){
  var socket = io.connect(window.location.origin);
}


const username = document.getElementById('username').textContent
const room = document.getElementById('room').textContent

const chat = document.getElementById('chat')

const messageInput = document.getElementById('messageInput')
const messageButton = document.getElementById('messageButton')

const videoInput = document.getElementById('videoInput')
const videoButton = document.getElementById('videoButton')


const appendMessage = (msg) => {
  const messageElement = document.createElement('div')
  messageElement.innerText = msg
  chat.append(messageElement)
}

socket.on("connect", ()=>{
  console.log(`{username} has connected`)
  socket.emit('connectUser', {'username': username, 'room': room})
  appendMessage(`${username}(You) are connected`)
})

socket.on("joinChat", (user)=>{
  console.log(user + " has connected to room")
  appendMessage(`${user} has connected to the room`)  
})

socket.on("leaveChat", (user)=>{
  console.log(user + " has left the room")
  appendMessage(`${user} has disconnected from the room`)  
})


//send message to everyone else
socket.on("message", (msg)=>{
  console.log(msg)
  appendMessage(`${msg}`)
})

//add message on your screen
messageButton.addEventListener('click', () => {
  var msg = messageInput.value
  if (msg){
    appendMessage(`${username}(You): ${messageInput.value}`)
    socket.emit('sendMessage', {'message': `${username}: ${messageInput.value}`, 'room': room})
    messageInput.value = ''
  }
})

//add video to queue
videoButton.addEventListener('click', ()=>{
    var link = videoInput.value
    if(link){
      console.log(link)
      socket.emit('addVideo', {'link':link, 'room': room})
      videoInput.value = ''
    }
})