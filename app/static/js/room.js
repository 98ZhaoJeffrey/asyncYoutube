//socketio method go here
var socket = io();
if (!socket.connected){
  var socket = io.connect(window.location.origin);
}
const chat = document.getElementById('chat')
const username = document.getElementById('username').textContent
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
  console.log(username + " has connected")
  socket.emit('connectUser', username)
  appendMessage(`You(${username}) are connected`)
})

socket.on("joinChat", (user)=>{
  console.log(user + " has connected to room")
  appendMessage(`${user} has connected to the room`)  
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
    appendMessage(`(You): ${messageInput.value}`)
    socket.emit('sendMessage', `${username}: ${messageInput.value}`)
    messageInput.value = ''
  }
})
