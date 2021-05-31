function validVideoId(link) {
    var id
    if(link.length > 11){
        id = link.slice(link.length-11)
    }
    var img = new Image();
    img.src = "http://img.youtube.com/vi/" + id + "/mqdefault.jpg";
    img.onload = function () {
        checkThumbnail(this.width);
    }
}

function checkThumbnail(width) {
    //HACK a mq thumbnail has width of 320.
    //if the video does not exist(therefore thumbnail don't exist), a default thumbnail of 120 width is returned.
    if (width === 120) {
        alert("Error: Invalid video id");
    }
}


export {validVideoId}