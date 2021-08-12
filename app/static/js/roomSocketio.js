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
  console.log(`${username} has connected`)
  appendMessage(`${username}(You) are connected`, true)
  //get the video that is currently playing and the time
})

socket.on("joinChat", (user)=>{
  console.log(`${user} has connected to room`)
  appendMessage(`${user} has connected to the room`, false)  
})

//send message to everyone else
socket.on("message", (msg)=>{
  console.log(msg)
  appendMessage(`${msg}`, false)
})

socket.once("leaveChat", (data)=>{
  console.log(`${data["userleft"]} has left the room`)
  appendMessage(`${data["userleft"]} has disconnected from the room`)
  if(data["newHost"] !== undefined){
    console.log(`${data["newHost"]} is the host now`)  
    appendMessage(`${data["newHost"]} is the host now`)
  }
})

socket.on("addVideoResponse", (data)=>{
  console.log(data)
  addAlert(data)
})

//play/pause video at x seconds
socket.on("toggleVideo", (data)=>{
  console.log("Video should be playing")
  player.seekTo(data["time"], true)
  playVideo(data["state"])
  playButton.innerHTML = `<i class="bi bi-${data["state"]}-fill"></i>`
})

socket.on("jumpTo", (data)=>{
  player.seekTo(data["time"], true)
  timeline.value = data["timelineValue"]
  console.log(timeline.value)
})

socket.on('skipVideoResponse', (data)=>{
  if(data["status"] === "Success"){
    player.cueVideoById(data["video"])
    console.log(`Now playing ${data["video"]}`)
  }
  addAlert(data)
})

socket.on('playNextVideo', (data)=>{
   console.log(data)
   if(data["status"] === "Success"){
     player.cueVideoById(data["video"])
     playButton.innerhtml = `<i class="bi bi-play-fill"></i>`
     console.log(`Now playing ${data["video"]}`)
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
      console.log(link)
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
     console.log(timeline.value)
     const timeToSkipTo = player.getDuration() * timeline.value/1000
     socket.emit('skipTo', {time: timeToSkipTo, timelineValue: timeline.value, room: room, userId: userId})
     player.seekTo(timeToSkipTo, true)
 }

//full screen
fullscreenButton.addEventListener('click', ()=>{
  console.log("fullscreen")
  var requestFullScreen = iframe.requestFullscreen || iframe.mozRequestFullScreen || iframe.webkitRequestFullScreen;
  if (requestFullScreen) {
    requestFullScreen.bind(iframe)();
  }
}) 

//adjust volume client side only
const adjustVolume = ()=>{
  player.setVolume(volumeBar.value)
  console.log(`Player's volume ${player.getVolume()}`)
}

//skip video
skipButton.addEventListener('click', ()=>{
  console.log("Skip request")
  socket.emit('skipVideo', {room: room, userId: userId})
})

const copyLink = ()=>{
  /* Get the text field */
  var copyText = document.getElementById("invite");
  /* Select the text field */
  copyText.select();
  copyText.setSelectionRange(0, 99999); /* For mobile devices */
  /* Copy the text inside the text field */
  document.execCommand("copy");
} 