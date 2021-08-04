//socketio method go here
var socket = io();

if (!socket.connected){
  socket = io.connect(window.location.origin);
}

const username = document.getElementById('username').textContent
const room = document.getElementById('room').textContent
const userId = document.getElementById('userId').textContent

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

 // 2. This code loads the IFrame Player API code asynchronously.
 var tag = document.createElement('script');

 tag.src = "https://www.youtube.com/iframe_api";
 var firstScriptTag = document.getElementsByTagName('script')[0];
 firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
 
 // 3. This function creates an <iframe> (and YouTube player)
 //    after the API code downloads.
 var player, iframe;
 function onYouTubeIframeAPIReady() {
     player = new YT.Player('player', {
             height: '456',
             width: '768',
             videoId: 'xTczn5RUgnk',
             playerVars: {
                 'playsinline': 0,
                 'controls':0,
                 'disablekb':1
             },
             events: {
             'onReady': onPlayerReady,
             'onStateChange': onPlayerStateChange
             }
         });
 }
 
 // 4. The API will call this function when the video player is ready.
 function onPlayerReady(event) {
    var player = event.target;
    iframe = document.getElementById("player")
    player.setVolume(50)
    event.target.playVideo();
 }
 
 function stopVideo() {
     player.stopVideo();
 }

const appendMessage = (msg, isSender)=>{
  const messageElement = document.createElement('div')
  messageElement.className = `rounded-lg bg-${isSender ? 'red-700' : 'purple-600'} text-white max-w-sm py-2 px-4 mt-4 ${isSender ? 'mr-3 self-end' : 'ml-3 self-start'} text-center`
  messageElement.innerText = msg
  chat.append(messageElement)
}

socket.once("connect", ()=>{
  console.log(`${username} has connected`)
  appendMessage(`${username}(You) are connected`, true)
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

socket.once("leaveChat", (data)=>{
  console.log(`${data["userleft"]} has left the room`)
  appendMessage(`${data["userleft"]} has disconnected from the room`)
  if(data["newHost"] !== undefined){
    console.log(`${data["newHost"]} is the host now`)  
    appendMessage(`${data["newHost"]} is the host now`)
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

socket.on("addVideoResponse", (data)=>{
  console.log(data)
  addAlert(data)
})

//play video helper function
const playVideo = (state)=>{
  if(state === "play"){
    player.pauseVideo()
  }
  else{
    player.playVideo()    
  }
}

//emits play/pause command
playButton.addEventListener('click', ()=>{
  const state = player.getPlayerState() === 1 ? "play" : "pause"
  socket.emit('playVideo', {state:state, room: room, time:player.getCurrentTime()})
  playVideo(state)
  playButton.innerHTML = `<i class="bi bi-${state}-fill"></i>`
})

//play/pause video at x seconds
socket.on("toggleVideo", (data)=>{
  console.log("Video should be playing")
  player.seekTo(data["time"], true)
  playVideo(data["state"])
})

//scrub timeline
const scrubVideo = ()=>{
     console.log(timeline.value)
     const timeToSkipTo = player.getDuration() * timeline.value/1000
     socket.emit('skipTo', {time: timeToSkipTo, timelineValue: timeline.value, room: room})
     player.seekTo(timeToSkipTo, true)
 }

socket.on("jumpTo", (data)=>{
  player.seekTo(data["time"], true)
  timeline.value = data["timelineValue"]
  console.log(timeline.value)
})

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

socket.on('skipVideoResponse', (data)=>{
  if(data["state"] === "skipping"){
    player.cueVideoById(data["video"])
    console.log(`Now playing ${data["video"]}`)
  }
})

//handle queuing the next video when it ends
function onPlayerStateChange(event) {
     if (event.data == YT.PlayerState.ENDED) {
        //cue the next video
        socket.emit("videoEnded", {room: room})
     }
 }

socket.on('playNextVideo', (data)=>{
   console.log(data)
   if(data["state"] === "next"){
     player.cueVideoById(data["video"])
     playButton.innerhtml = `<i class="bi bi-play-fill"></i>`
     console.log(`Now playing ${data["video"]}`)
   }
})

