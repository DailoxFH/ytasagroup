from flask import Flask, render_template, request, redirect, url_for, make_response, Response, send_from_directory
import string
import random
import hashlib

rooms = {}
app = Flask(__name__, static_url_path="/static", template_folder="templates", static_folder="static")

def generate_random(iter, lower=False):
    if lower:
        return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(iter))
    else:
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(iter))


def room_not_found():
    return Response("Room not found OR could not be created", status=404)


def username_not_found():
    return Response("Username not found", status=401)


def invalid_request():
    return Response("Invalid request", status=400)


def username_already_taken():
    return Response("Username already taken", status=401)


def check_if_room_exists(roomid):
    try:
        # noinspection PyStatementEffect
        rooms[roomid]
        return True
    except KeyError:
        return False


def check_cookie(cookies, cookie_values, roomId):
    where = ""
    avoid = [[]]
    for i in range(0, len(cookies)):
        value = cookie_values[i]
        key = list(cookies.keys())[i]
        for k1,v1 in rooms.items():
            for k2, v2 in rooms[k1].items():
                if k2 == "user":
                    for k3, v3 in rooms[k1][k2].items():
                        if k3 == key and v3 == value:
                            avoid.append(i)
                            break
        else:
            for k, v in cookies.items():
                if k in rooms[roomId]["user"].keys():
                    where = k
    if len(avoid) == 0:
        avoid.append(where)
    return [where, avoid]


def get_id_from_link(input):
    toCheck = ["/watch?v=", "/embed/", "/v/"]
    if "/watch?v=" in input:
        splittedUrl = input.split('/')
        return splittedUrl[-1].replace("watch?v=", "")
    elif len(input) == 11 and '/' not in input:
        return input
    else:
        return False


def create_cookie(roomId, username):
    resp = make_response(redirect(url_for("watchyt", roomid=roomId), code=307))
    id = generate_random(24, True)
    resp.set_cookie(username, id)
    h = hashlib.sha512(id.encode())
    rooms[roomId]["user"][username] = h.hexdigest()
    return resp


@app.route('/')
def sessions():
    return render_template('session.html')


@app.route("/watchyt", methods=["GET", "POST"])
def watchyt():
    try:
        roomId = request.args.get("roomid")
        if not check_if_room_exists(roomId):
            return room_not_found()
    except KeyError:
        return room_not_found()

    try:
        ytid = request.form["ytid"]
    except KeyError:
        ytid = rooms[roomId]["video"]["ytid"]


    yt_id = get_id_from_link(ytid)
    if not ytid:
        return invalid_request()
    where = ""
    try:
        cookie_values = list(request.cookies.values())
        check_cookie_ret = check_cookie(request.cookies, cookie_values, roomId)
        where = check_cookie_ret[0]
        # noinspection PyStatementEffect
        rooms[roomId]["user"][where] != request.cookies[where]
    except (KeyError, IndexError):
        try:
            username = request.form["username"]
            if username == "" or username.isspace():
                raise KeyError
            try:
                # noinspection PyStatementEffect
                rooms[roomId]["user"][username]
                return username_already_taken()
            except KeyError:
                return create_cookie(roomId, username)
        except KeyError:
            ret = 'Please provide a username: <br> <br>' \
                  f'<form action="/watchyt?roomid={roomId}" method="post">' \
                  '<input type="text" placeholder="Username" name="username" />' \
                  '<input type="submit"/>' \
                  '</form>'
            return ret

    return render_template("watchyt.html", ytid=yt_id, roomId=roomId, user=where)


@app.route("/generate_room", methods=["POST"])
def generate_room():
    global rooms
    try:
        ytid = request.form["ytid"]
        username = request.form["username"]
        if username == "":
            raise KeyError
    except KeyError:
        return room_not_found()

    roomId = generate_random(15)

    while roomId in rooms:
        roomId = generate_random(15)

    ytid = get_id_from_link(ytid)

    fullUpdate = {roomId: {"video": {"ytid": ytid, "event": "NOTHING", "time": 0.0, "doneBy": "NONE"}}}
    rooms.update(fullUpdate)

    rooms[roomId]["user"] = {}

    return create_cookie(roomId, username)


@app.route("/submit_text", methods=["GET"])
def submit_text():
    try:
        ytid = get_id_from_link(request.args.get("ytid"))
        if not ytid:
            return invalid_request()
        roomid = request.args.get("roomid")
        if not check_if_room_exists(roomid):
            return room_not_found()
        event = request.args.get("event")
        try:
            time = float(request.args.get("time"))
        except ValueError:
            return invalid_request()

        cookie_keys = list(request.cookies.keys())
        cookie_values = list(request.cookies.values())
    except(KeyError, TypeError):
        return invalid_request()

    try:
        cookie_values = list(request.cookies.values())
        check_cookie_ret = check_cookie(request.cookies, cookie_values, roomid)
        where = check_cookie_ret[0]
        hashed_value = hashlib.sha512(request.cookies[where].encode())
        if rooms[roomid]["user"][where] == hashed_value.hexdigest():
            eventToUpdate = convert(event)

            if rooms[roomid]["video"]["event"] == eventToUpdate:
                return "Rooms stay the same"

            rooms[roomid]["video"]["ytid"] = ytid
            rooms[roomid]["video"]["event"] = eventToUpdate
            rooms[roomid]["video"]["time"] = time

            if request.args.get("automaticallydone") == "true":
                if time == rooms[roomid]["video"]["time"]:
                    rooms[roomid]["video"]["doneBy"] = where
            else:
                rooms[roomid]["video"]["doneBy"] = where
            return {"status": "OK", "ytid": ytid}
        else:
            return username_not_found()
    except (KeyError, IndexError, TypeError):
        return username_not_found()


def convert(event):
    eventToUpdate = "NOTHING"
    try:
        event = int(event)
    except:
        return eventToUpdate
    if event == 0:
        eventToUpdate = "ENDED"
    elif event == 1:
        eventToUpdate = "PLAYING"
    elif event == 2:
        eventToUpdate = "PAUSED"
    elif event == 3:
        eventToUpdate = "BUFFERING"

    return eventToUpdate


@app.route("/changed", methods=["GET"])
def changed():
    try:
        roomid = request.args.get("roomid")
        if not check_if_room_exists(roomid):
            return room_not_found()
        event = request.args.get("event")
        ytid = get_id_from_link(request.args.get("ytid"))
        if not ytid:
            return invalid_request()
    except KeyError:
        return invalid_request()

    eventToCheck = convert(event)

    currentEvent = rooms[roomid]["video"]["event"]
    currentYtId = rooms[roomid]["video"]["ytid"]
    currentTime = rooms[roomid]["video"]["time"]
    currentDoneBy = rooms[roomid]["video"]["doneBy"]

    if currentEvent != eventToCheck or currentYtId != ytid:
        return {"status": "OUT", "video": currentYtId, "event": currentEvent, "time": currentTime, "doneBy": currentDoneBy}

    return {"status": "OK", "doneBy": currentDoneBy, "event": currentEvent, "time": currentTime}


@app.route("/js/<path:path>")
def send_js(path):
    return send_from_directory("js", path)


if __name__ == '__main__':
    from waitress import serve
    serve(app, port=5000)