//socketio method go here
var socket = io();

if (!socket.connected){
  socket = io.connect(window.location.origin);
}

const chat = document.getElementById('chat')

const messageInput = document.getElementById('messageInput')
const messageButton = document.getElementById('messageButton')

const videoInput = document.getElementById('videoInput')
const videoButton = document.getElementById('videoButton')

const playButton = document.getElementById("playButton")
const fullscreenButton = document.getElementById("fullscreenButton")
const skipButton = document.getElementById("skipButton")
const timeline = document.getElementById("timeline")
const volumeBar = document.getElementById("volumeBar")

const appendMessage = (msg, isSender)=>{
  const messageElement = document.createElement('div')
  messageElement.className = `rounded-lg bg-${isSender ? 'red-700' : 'purple-600'} text-white max-w-sm py-2 px-4 mt-4 ${isSender ? 'mr-3 self-end' : 'ml-3 self-start'} text-center`
  messageElement.innerText = msg
  chat.append(messageElement)
}

socket.once("connect", ()=>{
  appendMessage(`${username}(You) are connected`, true)
  //get the video that is currently playing and the time
})

socket.on("joinChat", (user)=>{
  appendMessage(`${user} has connected to the room`, false)  
})

//send message to everyone else
socket.on("message", (msg)=>{
  appendMessage(`${msg}`, false)
})

socket.once("leaveChat", (data)=>{
  appendMessage(`${data["userleft"]} has disconnected from the room`)
  if(data["newHost"] !== undefined){
    appendMessage(`${data["newHost"]} is the host now`)
  }
})

//sync the user to the video
socket.on("getVideoProgress", (data)=>{
  const timeToSkipTo = player.getDuration() * timeline.value/1000
  socket.emit('skipTo', {time: timeToSkipTo, timelineValue: timeline.value, userId: data})
  player.seekTo(timeToSkipTo, true)
})

socket.on("addVideoResponse", (data)=>{
  addAlert(data)
})

//play/pause video at x seconds
socket.on("toggleVideo", (data)=>{
  player.seekTo(data["time"], true)
  playVideo(data["state"])
  playButton.innerHTML = `<i class="bi bi-${data["state"]}-fill"></i>`
})

socket.on("jumpTo", (data)=>{
  player.seekTo(data["time"], true)
  timeline.value = data["timelineValue"]
})

socket.on('skipVideoResponse', (data)=>{
  if(data["status"] === "Success"){
    player.cueVideoById(data["video"])
  }
  addAlert(data)
})

socket.on('playNextVideo', (data)=>{
   if(data["status"] === "Success"){
     player.cueVideoById(data["video"])
     playButton.innerhtml = `<i class="bi bi-play-fill"></i>`
   }
   addAlert(data)
})

//add message on your screen
messageButton.addEventListener('click', ()=>{
  var msg = messageInput.value
  if (msg){
    appendMessage(`${messageInput.value}`, true)
    socket.emit('sendMessage', {message: `${username}: ${messageInput.value}`, room: room})
    messageInput.value = ''
    chat.scrollTo(0,chat.scrollHeight)
  }
})

//pressing enter submits form and shift + enter makes a new line
messageInput.addEventListener('keydown', (e)=>{
  const keyCode = e.which || e.key;
  if(keyCode === 13 && !e.shiftKey){
    e.preventDefault()
    messageButton.click()
  }
})

//add video to queue
videoButton.addEventListener('click', ()=>{
    var link = videoInput.value
    if(link){
      socket.emit('addVideo', {link:link, room:room})
      videoInput.value = ''
    }
})

//emits play/pause command
playButton.addEventListener('click', ()=>{
  const state = player.getPlayerState() === 1 ? "play" : "pause"
  socket.emit('playVideo', {state:state, room: room, userId: userId, time:player.getCurrentTime()})
})

//scrub timeline
const scrubVideo = ()=>{
     const timeToSkipTo = player.getDuration() * timeline.value/1000
     socket.emit('skipTo', {time: timeToSkipTo, timelineValue: timeline.value, room: room, userId: userId})
     player.seekTo(timeToSkipTo, true)
}

//full screen
fullscreenButton.addEventListener('click', ()=>{
  var requestFullScreen = iframe.requestFullscreen || iframe.mozRequestFullScreen || iframe.webkitRequestFullScreen;
  if (requestFullScreen) {
    requestFullScreen.bind(iframe)();
  }
}) 

//adjust volume client side only
const adjustVolume = ()=>{
  player.setVolume(volumeBar.value)
}

//skip video
skipButton.addEventListener('click', ()=>{
  socket.emit('skipVideo', {room: room, userId: userId})
})

const copyLink = ()=>{
  /* Get the text field */
  let copyText = document.getElementById("invite");
  /* Select the text field */
  copyText.select();
  copyText.setSelectionRange(0, 99999); /* For mobile devices */
  /* Copy the text inside the text field */
  document.execCommand("copy");
} 