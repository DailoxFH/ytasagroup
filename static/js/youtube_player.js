let lastLog = "";
let lastAllUsers = [];
window.addEventListener("beforeunload", function () {
    let xhr = new XMLHttpRequest();
    xhr.open("GET", window.location.origin + "/disconnect?roomid=" + room_id)
    xhr.send();

});

let tag = document.createElement('script');
tag.src = "https://www.youtube.com/iframe_api";
let firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

let player;

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


let t;

function onPlayerReady(event) {
    t = setInterval(checkChanged, 1000);
    checkChanged(true);
}

function onPlayerStateChange(event) {
    if (event.data === 3 || event.data === -1) {
        return;
    }
    submit(event.data);
}

function updateLog(toUpdate) {
    if (toUpdate !== lastLog) {
        let currentDate = new Date();
        let finalToUpdate = "\n(" + currentDate.getHours() + ":" + currentDate.getMinutes() + ":" + currentDate.getSeconds() + ")" + " " + toUpdate;
        let eventLog = document.getElementById("event-log");
        let changeInput = document.getElementById("change");
        changeInput.innerHTML = toUpdate;
        eventLog.innerHTML += finalToUpdate;
        eventLog.scrollTop = eventLog.scrollHeight;
        lastLog = toUpdate;
    }
}

function checkForError(xhr) {
    let error = false;
    if (xhr.status === 401 || xhr.status === 404) {
        clearInterval(t);
        document.body.innerHTML = xhr.responseText;
        error = true;
    }
    return error;
}

function submit(event, asynchronous = true) {
    let submit_xhr = new XMLHttpRequest();
    let time = 0;
    let tmpYtId = yt_id;
    if (player.getCurrentTime() !== undefined) {
        time = player.getCurrentTime();
    }
    let requeststr = window.location.origin + "/submit_text?ytid=" + yt_id + "&roomid=" + room_id + "&event=" + event + "&time=" + time;


    submit_xhr.open("GET", requeststr, asynchronous);

    let isOk = false;
    submit_xhr.onloadend = function () {
        let obj = JSON.parse(submit_xhr.responseText);
        checkForError(submit_xhr);
        if (obj.status === "OK" && obj.ytid !== undefined && obj.ytid !== yt_id) {
            tmpYtId = obj.ytid;
        }
        if(submit_xhr.status !== 400) {
            isOk = true;
        }
    }

    submit_xhr.send();

    yt_id = tmpYtId;

    return isOk;

}

function showMessage(msg) {
    document.getElementById("username_to_show").innerHTML = msg;
    showAlert();
}

function checkChanged(firstRun=false) {
    let xhr = new XMLHttpRequest();
    let time = 0;
    if (player.getCurrentTime() !== undefined) {
        time = player.getCurrentTime();
    }
    xhr.open("GET", window.location.origin + "/changed?roomid=" + room_id + "&event=" + player.getPlayerState() + "&ytid=" + yt_id + "&time=" + time, true);
    xhr.onload = function () {
        let obj = JSON.parse(xhr.responseText);
        if (obj.status !== "OK") {
            if (obj.video !== yt_id) {
                yt_id = obj.video;
                if(firstRun) {
                    player.loadVideoById(yt_id, obj.time);
                } else {
                    player.loadVideoById(yt_id);
                }
                document.getElementById("input_ytid").innerHTML = yt_id;
            }
            if (obj.time - player.getCurrentTime() > 3.0 || obj.time - player.getCurrentTime() < -3.0) {
                player.seekTo(obj.time);
            }


            if (obj.doneBy !== activeUser) {
                if (obj.event === "STOPPED") {
                    player.stopVideo();

                } else if (obj.event === "PLAYING") {
                    player.playVideo();

                } else if (obj.event === "PAUSED") {
                    player.pauseVideo();
                }
            }


            yt_id = obj.video;

        }
        let toUpdate = obj.doneBy + " did: " + obj.event + " (" + Number((obj.time).toFixed(3)) + ")";
        updateLog(toUpdate);

        if (obj.allUsers !== lastAllUsers) {
            let userList = document.getElementById("user-list");
            userList.innerHTML = "";
            for (let i = 0; i < obj.allUsers.length; i++) {
                let currentUser = obj.allUsers[i];
                if (!lastAllUsers.includes(currentUser)) {
                    if (obj.event === "PLAYING" && currentUser !== activeUser) {
                        player.pauseVideo();
                    }
                    let toUpdateNotification = '"' + currentUser + '" joined the room!';
                    showMessage(toUpdateNotification);
                    updateLog(toUpdateNotification);
                }
                userList.innerHTML += "\n - " + currentUser;
            }
            userList.scrollTop = userList.scrollHeight;
            lastAllUsers = obj.allUsers;
        }

    }

    xhr.onloadend = function () {
        checkForError(xhr);
        if (xhr.status === 400) {
            yt_id = xhr.responseText;
            showMessage("Invalid Request. Please try again!");
            document.getElementById("ytid").value = "";
        }
    }
    xhr.send();
}

document.getElementById("submit").addEventListener('click', function () {
    yt_id = document.getElementById("ytid").value;
    if(submit(2, false)) {
        player.loadVideoById(yt_id);
    }
});



