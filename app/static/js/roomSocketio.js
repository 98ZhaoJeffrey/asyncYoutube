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

const playButton = document.getElementById("playButton")
const fullscreenButton = document.getElementById("fullscreenButton")
const timeline = document.getElementById("timeline")

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
    event.target.playVideo();
 }
 
 // 5. The API calls this function when the player's state changes.
 //    The function indicates that when playing a video (state=1),
 //    the player should play for six seconds and then stop.
 var done = false;
 function onPlayerStateChange(event) {
     if (event.data == YT.PlayerState.PLAYING && !done) {
         setTimeout(stopVideo, 6000);
         done = true;
     }
 }
 function stopVideo() {
     player.stopVideo();
 }

const appendMessage = (msg, isSender) => {
  const messageElement = document.createElement('div')
  if (isSender){
    messageElement.className = "rounded-lg bg-red-700 text-white max-w-sm py-2 px-4 mt-4 mr-3 self-end text-center"
  }else{
    messageElement.className = "rounded-lg bg-purple-600 text-white max-w-sm py-2 px-4 mt-4 ml-3 self-start text-center"
  }
  messageElement.innerText = msg
  chat.append(messageElement)
}

socket.on("connect", ()=>{
  console.log(`${username} has connected`)
  socket.emit('connectUser', {username: username, room: room})
  appendMessage(`${username}(You) are connected`, true)
})

socket.on("joinChat", (user)=>{
  console.log(user + " has connected to room")
  appendMessage(`${user} has connected to the room`, false)  
})

socket.on("leaveChat", (user)=>{
  console.log(user + " has left the room")
  appendMessage(`${user} has disconnected from the room`)  
})


//send message to everyone else
socket.on("message", (msg)=>{
  console.log(msg)
  appendMessage(`${msg}`, false)
})

//add message on your screen
messageButton.addEventListener('click', () => {
  var msg = messageInput.value
  if (msg){
    appendMessage(`${messageInput.value}`, true)
    socket.emit('sendMessage', {message: `${username}: ${messageInput.value}`, room: room})
    messageInput.value = ''
    chat.scrollTo(0,chat.scrollHeight)
  }
})

messageInput.addEventListener('keydown', (e) => {
  const keyCode = e.which || e.key;

  if(keyCode === 13 && !e.shiftKey){
    e.preventDefault()
    messageButton.click()
  }
})
//pressing enter submits form and shift + enter makes a new line

//add video to queue
videoButton.addEventListener('click', ()=>{
    var link = videoInput.value
    if(link){
      console.log(link)
      socket.emit('addVideo', {link:link, room: room})
      videoInput.value = ''
    }
})

const playVideo = (state) => {
  if(state === "Play"){
    player.pauseVideo()
  }
  else{
    player.playVideo()    
  }
}

//emits play/pause command
playButton.addEventListener('click', ()=>{
  const state = player.getPlayerState() === 1 ? "Play" : "Pause"
  socket.emit('playVideo', {state:state, room: room, time:player.getCurrentTime()})
  playVideo(state)
  playButton.innerText = state
})

//play/pause video at x seconds
socket.on("toggleVideo", (data)=>{
  console.log("Video should be playing")
  player.seekTo(data["time"], true)
  playVideo(data["state"])
})

//scrub timeline
const scrubVideo = () => {
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