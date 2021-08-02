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
          videoId: yt_id,
          playerVars: {
            'playsinline': 1,
            'autoplay': 1,
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

function submit(event, asynchronous=true) {
    var submit_xhr = new XMLHttpRequest();
    time = 0;
    var tmpYtId = yt_id;
    if(player.getCurrentTime() != undefined) {
      time = player.getCurrentTime();
    }
    var requeststr = window.location.origin+"/submit_text?ytid="+yt_id+"&roomid="+room_id+"&event="+event+"&time="+time+"&automaticallydone="+dontSubmit;


    submit_xhr.open("GET", requeststr, asynchronous);


    submit_xhr.onloadend = function () {
      var obj = JSON.parse(submit_xhr.responseText);
      if(submit_xhr.status == 401 || submit_xhr.status == 400) {
        document.body.innerHTML = xhr.responseText;
        alert(submit_xhr.responseText);
        clearInterval(t);
      } else if (obj.status == "OK"){
        if(obj.ytid !== undefined && obj.ytid !== yt_id) {
            tmpYtId = obj.ytid;
        }
      }

    if(finished) {
      dontSubmit = false;
      finished = false;
    }
   }
   submit_xhr.send();

   yt_id = tmpYtId;

}

function checkChanged() {
    var xhr = new XMLHttpRequest();
    time = 0;
    if(player.getCurrentTime() != undefined) {
      time = player.getCurrentTime();
    }
    xhr.open("GET", window.location.origin+"/changed?roomid="+room_id+"&event="+player.getPlayerState()+"&ytid="+yt_id+"&time="+time, true);
    xhr.onload = function () {
      var obj = JSON.parse(xhr.responseText);
      if(obj.joined) {
        submit(2);
      }
      if(obj.status !== "OK") {
        if(obj.video !== yt_id) {
          yt_id = obj.video;
          player.loadVideoById(yt_id, obj.time);
          document.getElementById("input_ytid").value = yt_id;
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
      var changeInput = document.getElementById("change");
      changeInput.value = obj.doneBy + " did: "+obj.event+" ("+obj.time+")";
      //changeInput.style.width = changeInput.value.length + "ch";
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
    yt_id = document.getElementById("ytid").value;
    submit(2, false);
    document.getElementById("input_ytid").value = yt_id;
    player.loadVideoById(yt_id);
});