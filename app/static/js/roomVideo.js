// 2. This code loads the IFrame Player API code asynchronously.
var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

// 3. This function creates an <iframe> (and YouTube player)
//    after the API code downloads.
var player, iframe;
function onYouTubeIframeAPIReady(){
    player = new YT.Player('player', {
            videoId: video,
            playerVars: {
                'playsinline': 0,
                'controls':0,
                'disablekb':1,
                'autoplay': 0,
            },
            events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
            }
        });
}

const updateTimeline = ()=>{
    setInterval(()=>{
        timeline.value = 1000*player.getCurrentTime()/player.getDuration()
    }, 200)
}

//handle queuing the next video when it ends
function onPlayerStateChange(event){
    if (event.data == YT.PlayerState.ENDED) {
       //cue the next video
       socket.emit("videoEnded", {room: room})
    }
}

// 4. The API will call this function when the video player is ready.
function onPlayerReady(event){
   var player = event.target;
   iframe = document.getElementById("player")
   player.setVolume(50)
   event.target.playVideo();
   updateTimeline()
   socket.emit("syncVideo", {userId: userId, roomcode: room})
}

//play video helper function
const playVideo = (state)=>{
    if(state === "play"){
      player.pauseVideo()
    }
    else{
      player.playVideo()    
    }
}

const stopVideo = ()=>{
    player.stopVideo();
}


