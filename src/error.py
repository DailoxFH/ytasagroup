from flask import render_template


def room_not_found():
    return render_template("error.html", msg="Room not found OR could not be created"), 404


def username_not_found():
    return render_template("error.html", msg="Username not found"), 401


def invalid_request(template=None, message=None):
    if template is not None:
        return render_template(template, msg="Invalid Request. Please try again!"), 400
    elif message is not None:
        return message, 400


def username_errors(room_id, message):
    return render_template("username.html", room_id=room_id, msg=message), 400


def username_already_taken(room_id):
    return username_errors(room_id, "This username is already taken")


def username_too_long(room_id):
    return username_errors(room_id, "Username is too long. Please choose a shorter one")


def invalid_username(room_id):
    return username_errors(room_id, "Invalid username. Please choose a different one")
