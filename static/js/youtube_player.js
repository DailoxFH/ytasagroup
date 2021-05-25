var yt_id = document.getElementById("input_ytid").value;
var room_id = document.getElementById("input_roomid").value;
var finished = false;

var dontSubmit = false;

var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

var player;
function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
          height: '390',
          width: '640',
          videoId: yt_id,
          playerVars: {
            'playsinline': 1,
            'autoplay': 0
          },
          events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange,
          }
        });
}

var t;
function onPlayerReady(event) {
    checkChanged();
    t = setInterval(checkChanged, 1000);
}

function onPlayerStateChange(event) {
  if(event.data == 3 || event.data == -1) {
    return;
  }

  submit(event.data);
}

function submit(event) {
    var xhr = new XMLHttpRequest();
    var requeststr = window.location.origin+"/submit_text?ytid="+yt_id+"&roomid="+room_id+"&event="+event+"&time="+player.getCurrentTime()+"&automaticallydone="+dontSubmit;
    xhr.open("GET", requeststr, true);
    xhr.onloadend = function () {
      if(xhr.status == 401) {
        document.body.innerHTML = xhr.responseText;
        alert(xhr.responseText);
        clearInterval(t);
      }
    }
    if(finished) {
      dontSubmit = false;
      finished = false;
    }
    xhr.send();
}

function checkChanged() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", window.location.origin+"/changed?roomid="+room_id+"&event="+player.getPlayerState()+"&ytid="+yt_id+"&time="+player.getCurrentTime(), true);
    xhr.onload = function () {
      var obj = JSON.parse(xhr.responseText);
      if(obj.status !== "OK") {
        if(obj.video != yt_id) {
          yt_id = obj.video;
          player.loadVideoById(yt_id, obj.time);
          document.getElementById("div_ytid").innerHTML = yt_id;
        }

        dontSubmit = true;

        if(obj.time != player.getCurrentTime()) {
            player.seekTo(obj.time);
            time = obj.time;
        }

        if(obj.event == "STOPPED") {
          player.stopVideo();

        } else if(obj.event == "PLAYING") {
          player.playVideo();

        } else if(obj.event == "PAUSED") {
          player.pauseVideo();

        }

        finished = true;

        yt_id = obj.video;

      }
      document.getElementById("change").innerHTML = obj.doneBy + " did: "+obj.event+" ("+obj.time+")";
      currentChange = obj.doneBy;
}

    xhr.onloadend = function () {
      if(xhr.status == 404) {
        document.body.innerHTML = xhr.responseText;
        alert(xhr.responseText);
        clearInterval(t);
        }
      }
    xhr.send();
}


document.getElementById("submit").addEventListener('click', function (e) {
    var ytid = document.getElementById("ytid").value;
    yt_id = ytid
    submit(2);
    document.getElementById("div_ytid").innerHTML = yt_id;
    player.loadVideoById(yt_id);
});