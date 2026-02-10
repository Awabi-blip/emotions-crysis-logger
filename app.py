import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from constants import EMOTIONS, TRIGGERS
import datetime
from pprint import pprint
from collections import Counter
from crypt import encrypt_text, decrypt_text
from helpers import login_required, get_12_hour_time

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///crysis.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def get_rows_and_total_logs():
    user_id = session.get("user_id")
    rows = db.execute("SELECT emotion, chain, trigger, strftime('%H', time) as hour from logs where user_id = ?", user_id)
    total_logs = len(rows)
    return rows, total_logs

def trigger_processor():
    rows, total_logs = get_rows_and_total_logs()
    triggers_dict = {}
    for row in rows:
        tr = row['trigger']
        trigger = TRIGGERS[tr]
        if trigger not in triggers_dict:
            triggers_dict[trigger] = {'count':1, 'percentage': 0}
        else:
            triggers_dict[trigger]['count'] += 1

    for key in list(triggers_dict.keys()):
        numerator3 = triggers_dict[key]['count']
        if numerator3 > 0:
            percentage3 = (numerator3/total_logs) * 100
            triggers_dict[key]['percentage'] = percentage3

    return triggers_dict

def get_logs_dict():
    user_id = session.get("user_id")

    rows, total_logs = get_rows_and_total_logs()

    logs_dict = {}

    for emotion in EMOTIONS:
        logs_dict[emotion] = {"totalChains" : 0, "chains":{}, "times":{"all_times":[]}, "totalCounts": 0}

    all_hours = []

    for row in rows:
        chainedEmotion = row["chain"]
        primaryEmotion = row["emotion"]
        hour = int(row['hour'])

        logs_dict[primaryEmotion]["times"]["all_times"].append(hour)
        all_hours.append(hour)

        if chainedEmotion != 'None':
            if chainedEmotion not in logs_dict[primaryEmotion]["chains"]:
                logs_dict[primaryEmotion]["chains"][chainedEmotion] = {"count":1, "percentage": 0}
                logs_dict[primaryEmotion]["totalChains"] += 1
            else:
                logs_dict[primaryEmotion]["chains"][chainedEmotion]["count"]+= 1
                logs_dict[primaryEmotion]["totalChains"] += 1

    for e in EMOTIONS:
        for c in logs_dict[e]['chains']:
            numerator2 = logs_dict[e]['chains'][c]['count']
            denominator2 = logs_dict[e]['totalChains']
            if numerator2 > 0:
                percentage2 = numerator2/denominator2 * 100
                logs_dict[e]['chains'][c]['percentage'] = percentage2


    counts = Counter(all_hours)

    if len(counts) > 0:
        most_common_hour_24: int  = counts.most_common(1)[0][0]
        most_common_hour_12: str = get_12_hour_time(most_common_hour_24)
    else:
        most_common_hour_24 = 0
        most_common_hour_12: str = "No Entries :("

    for emiti in EMOTIONS:
        hours_emiti = logs_dict[emiti]["times"]['all_times']
        counts = Counter(hours_emiti)
        if len(counts) > 0:
            most_common_hour_for_each_emotion_24 = counts.most_common(1)[0][0]
        else:
            most_common_hour_for_each_emotion_24 = None

        logs_dict[emiti]["times"]["most_common_trigger_hour"] = most_common_hour_for_each_emotion_24


    total_counts = db.execute("SELECT COUNT(*) as n, emotion from logs where user_id = ? GROUP BY emotion", user_id)

    for counts in total_counts:
        emo = counts['emotion']
        logs_dict[emo]['totalCounts'] = counts['n']

    for emotion2 in EMOTIONS:
        numerator2 = logs_dict[emotion2]['totalCounts']
        if numerator2 > 0:
            total_percentage = (numerator2/total_logs*100)
            logs_dict[emotion2]['total_percentage'] = total_percentage

    return logs_dict, most_common_hour_12

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username").lower()
        if not username:
            return render_template("register.html", error = "please provide us with a username, your honour 🥰")

        for i in username:
            if i == " ":
                return render_template("login.html", error = "cookie, please dont add a space in your username 🥰")

        password = request.form.get("password")
        if not password:
            return render_template("register.html", error = "please provide us with a password, your honour 🥰")

        confirmation = request.form.get("confirmation")
        if not confirmation:
            return render_template("register.html", error = "please provide us with a confirmation, your honour 🥰")

        if password != confirmation:
            return render_template("register.html", error = "your honour the password does not match the re-entered password, please type it again for us 🥰")

        rows = db.execute("SELECT * FROM users WHERE username = ?;", username)

        if len(rows) != 0:
            return render_template("register.html", error = "your honour, thee cool username you entered seems to have been taken, please try another one 🥰" )

        hash = generate_password_hash(password)

        db.execute("INSERT INTO users (username, hash) VALUES(?,?);", username, hash)

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":

        username = request.form.get("username").lower().strip()
        if not username:
            return render_template("login.html", error = "please provide us with a username, your honour 🥰")

        password = request.form.get("password")
        if not password:
            return render_template("login.html", error = "please provide us with a password, your honour 🥰")

        rows = db.execute("SELECT * from users where username = ?", username)

        if len(rows) != 1:
            return render_template("login.html", error = "username seems to be incorrect, might have made a typo? 🥰")

        if not check_password_hash(rows[0]["hash"], password):
            return render_template("login.html", error= "password seems to not match, try again cookie🥰")

        session["user_id"] = rows[0]["id"]

        return redirect("/")

    return render_template("login.html")


@app.route("/")
@login_required
def index():
    user_id = session.get("user_id")
    print("USER_ID" , user_id)
    if request.method == "POST":
        return redirect("/entry")

    logs_dict, common_hour = get_logs_dict()
    rows , total_logs = get_rows_and_total_logs()
    rows = 0
    emotions_data = db.execute("SELECT emotion, COUNT(*) as n FROM logs WHERE user_id = ? GROUP BY emotion ORDER BY n DESC LIMIT 1;", user_id)

    if total_logs == 0:
        dominant = "null"
        count_highest_emotion = 0
        percentage_highest_emotion = 0
        dominantEmotion = dominant
        highestPercentageChain = 0
        dominantChainPercentage = 0
        dominantChain = "null"
    else:
        dominant = emotions_data[0]['emotion'] # make it so that it can grab multiple highest emotions
        count_highest_emotion = emotions_data[0]['n']
        dominantEmotion = dominant
        percentage_highest_emotion = (count_highest_emotion/total_logs) * 100
        chains = logs_dict[dominantEmotion]['chains']
        percentagesChain = []
        Chains = []
        if chains:
            for i in chains:
                percentagesChain.append(chains[i]['percentage'])
                Chains.append(i)

            if percentagesChain:
                highestPercentageChain = max(percentagesChain)
                index = percentagesChain.index(highestPercentageChain)
                dominantChainPercentage = percentagesChain[index]
                dominantChain = Chains[index]
            else:
                dominantChainPercentage = 0
                dominantChain = "None"
        else:
            dominantChainPercentage = 0
            dominantChain = "None"

    triggers_data = db.execute("SELECT trigger, COUNT(*) as t FROM logs WHERE user_id = ? GROUP BY trigger ORDER BY t DESC LIMIT 1;", user_id)
    if triggers_data:
        tr = triggers_data[0]['trigger']
        most_common_trigger_name = TRIGGERS[tr]
        most_common_trigger_count = triggers_data[0]['t']
        percentage_most_common_trigger = most_common_trigger_count/total_logs * 100
    else:
        most_common_trigger_name = "null"
        percentage_most_common_trigger = 0

    history = db.execute("SELECT emotion, chain, trigger from logs where user_id = ? ORDER BY log_id DESC LIMIT 3", user_id)
    print(history)
    return render_template("index.html", EMOTIONS=EMOTIONS, dominantEmotion = dominantEmotion, percentage=percentage_highest_emotion,
                            total_logs = total_logs, dominantChainPercentage = dominantChainPercentage, dominantChain=dominantChain, common_hour = common_hour,
                            most_common_trigger_name = most_common_trigger_name, percentage_most_common_trigger = percentage_most_common_trigger, history=history)

@app.route("/chains", methods = ["GET", "POST"])
@login_required
def chains():
    logs_dict, hour = get_logs_dict()
    return render_template("chains.html", EMOTIONS = EMOTIONS, logs_dict = logs_dict)

@app.route("/frequent_emotions", methods=["GET", "POST"])
@login_required
def frequent_emotions():
    user_id = session.get("user_id")
    logs_dict, hours = get_logs_dict()


    return render_template("frequent_emotions.html", logs_dict = logs_dict, EMOTIONS = EMOTIONS)

@app.route("/times", methods = ["GET", "POST"])
@login_required
def times():
    logs_dict, hours_frequent = get_logs_dict()
    return render_template("times.html", logs_dict = logs_dict, EMOTIONS = EMOTIONS)


@app.route("/triggers", methods = ["GET", "POST"])
@login_required
def triggers():
    triggers_dict = trigger_processor()
    print(triggers_dict)
    return render_template("triggers.html", triggers_dict = triggers_dict)

@app.route("/entry", methods = ["GET", "POST"])
@login_required
def entry():
    if request.method == "POST":

        user_id = session.get("user_id")

        emotion = request.form.get("emotion")

        chain = request.form.get("chain")

        if not chain:
            chain = "null"

        trigger = request.form.get("trigger")

        time_option = request.form.get("time_option")

        if time_option == 'now':
            time = datetime.datetime.now()
        elif time_option == 'custom':
            raw_time = request.form.get("custom_time")
            try:
                time = datetime.datetime.strptime(raw_time, "%Y-%m-%dT%H:%M")
            except ValueError:
                # Fallback if parsing fails
                time = datetime.datetime.now()

        note = request.form.get("note")

        if not note:
            note = "null"

        secure_note = encrypt_text(note)
        db.execute("INSERT INTO logs (user_id, emotion, trigger, chain, note, time) VALUES (?,?,?,?,?,?)", user_id, emotion, trigger, chain, secure_note,time)

    return render_template("entry.html", emotions = EMOTIONS, triggers = TRIGGERS)

@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    user_id = session.get("user_id")
    if request.method == "POST":
        delete_button = request.form.get("delete")
        if delete_button:
            delete_id = int(delete_button)
            db.execute("DELETE from logs WHERE log_id = ? AND user_id = ?", delete_id, user_id)

        rows = db.execute("SELECT strftime('%I:%M %p, %d/%m/%Y', time) as pretty_time, log_id ,emotion, trigger, chain, note from logs where user_id =?;", user_id)

        for row in rows:
            row["note"] = decrypt_text(row["note"])
        return render_template("history.html", rows= rows)

    rows = db.execute("SELECT strftime('%I:%M %p, %d/%m/%Y', time) as pretty_time, log_id ,emotion, trigger, chain, note from logs where user_id =?;", user_id)
    for row in rows:
            row["note"] = decrypt_text(row["note"])
            tr = row["trigger"]
            row["trigger"] = TRIGGERS[tr]
    return render_template("history.html", rows= rows)

@app.route("/faq")
@login_required
def faq():
    return render_template("faq.html")

@app.route("/logout")
@login_required
def logout():
    session.clear()

    return render_template("login.html")
