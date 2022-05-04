from flask import Flask, redirect, render_template, request, url_for
from flask_pymongo import PyMongo
import requests

import config


app = Flask(__name__)
app.config["MONGO_URI"] = config.MONGO_URI
app.config.update(TEMPLATES_AUTO_RELOAD=True)
mongo = PyMongo(app)


def get_mmr(user, race):
    season = 11
    while season > 0:
        res = requests.get(config.w3c_url + user.replace("#", "%23") + f'/game-mode-stats?gateWay=20&season={season}')
        for item in res.json():
            if item['gameMode'] == 1 and item['race'] == int(race):
                return int(item["mmr"])
        season -= 1
    return None


@app.route('/', methods=['POST', 'GET'])
def list_brackets():
    users = list(mongo.db.koths.find())
    kings = list(mongo.db.koths.find({'is_king': True}))

    return render_template(
        'index.html',
        title='Gym KOTH!',
        users=users,
        kings=kings,
        )

@app.route('/overlay', methods=['POST', 'GET'])
def show_overlay():
    users = list(mongo.db.koths.find())
    kings = list(mongo.db.koths.find({'is_king': True}))

    return render_template(
        'overlay.html',
        title='GYM KOTH - Twitch Overlay',
        users=users,
        kings=kings,
        )

# TODO: Add forms on /manage to manually input MMR for players that have no S10 stats
@app.route('/manage', methods=['POST', 'GET'])
def query_records():
    users = list(mongo.db.koths.find())
    kings = list(mongo.db.koths.find({'is_king': True}))

    return render_template(
        'manage.html',
        title='Gym KOTH - Management',
        users=users,
        kings=kings,
        )

@app.route('/signup', methods=['POST', 'GET'])
def signup_user():
    return render_template(
        'signup.html',
        title='Gym KOTH - Sign up',
    )

@app.route('/add_users', methods=['POST', 'GET'])
def add_user():
    username = request.form['username']
    race = request.form['race']
    # res = requests.get(config.w3c_url + username + '/game-mode-stats?gateWay=20&season=11')
    # for item in res.json():
    #     if item['gameMode'] == 1 and item['race'] == int(race):
            # determine bracket based on mmr
    mmr = get_mmr(username, race)
    if int(mmr) > 1600:
        bracket = 1
    elif int(mmr) < 1450:
        bracket = 3
    else:
        bracket = 2
    user = {
        'username': username.replace('%23', '#'),
        'race': int(race),
        'mmr': int(mmr),
        'bracket': bracket,
        'is_king': False
    }

    try:
        mongo.db.koths.insert_one(user)
        print('Added document to db')
    except Exception as e:
        print(f'Error adding document: {e}')

    return redirect(request.referrer)

@app.route('/manual_add_users', methods=['POST', 'GET'])
def manual_add_user():
    username = request.form['username']
    race = request.form['race']
    mmr = request.form['mmr']

    # determine bracket based on mmr
    if int(mmr) > 1600:
        bracket = 1
    elif int(mmr) < 1450:
        bracket = 3
    else:
        bracket = 2
    user = {
        'username': username.replace('%23', '#'),
        'race': int(race),
        'mmr': int(mmr),
        'bracket': bracket,
        'is_king': False
    }

    try:
        mongo.db.koths.insert_one(user)
        print('Added document to db')
    except Exception as e:
        print(f'Error adding document: {e}')

    return redirect(request.referrer)

@app.route('/new_signup', methods=['POST', 'GET'])
def user_signup():
    username = request.form['username']
    race = request.form['race']
    # res = requests.get(config.w3c_url + username + '/game-mode-stats?gateWay=20&season=11')
    # for item in res.json():
    #     if item['gameMode'] == 1 and item['race'] == int(race):
            # determine bracket based on mmr
    mmr = get_mmr(username, race)
    if int(mmr) > 1600:
        bracket = 1
    elif int(mmr) < 1450:
        bracket = 3
    else:
        bracket = 2
    user = {
        'username': username.replace('%23', '#'),
        'race': int(race),
        'mmr': int(mmr),
        'bracket': bracket,
        'is_king': False
    }

    try:
        mongo.db.koths.insert_one(user)
        print('Added document to db')
    except Exception as e:
        print(f'Error adding document: {e}')

    return redirect(request.referrer)


@app.route('/delete_user', methods=['GET'])
def delete_user():
    user = {
        'username': request.args.get('username').replace('%23', '#')
    }
    mongo.db.koths.delete_one(user)
    print(f'Deleted {user["username"]} from db')

    return redirect(request.referrer)


@app.route('/make_king', methods=['GET'])
def make_king():
    # delete old king
    bracket = int(request.args.get('bracket'))
    old_king = {
        'is_king': True,
        'bracket': bracket
    }
    mongo.db.koths.delete_one(old_king)
    print(f'Deleted old king: {old_king}')

    # make new king
    user = {'username': request.args.get('username').replace('%23', '#')}
    print(f'Username: {user}')
    new_value = {'$set': {'is_king': True}}
    mongo.db.koths.update_one(user, new_value)
    print(f'Made {user["username"]} king!')

    return redirect(request.referrer)


@app.route('/remove_king', methods=['GET'])
def remove_king():
    # delete old king
    bracket = int(request.args.get('bracket'))
    old_king = {
        'is_king': True,
        'bracket': bracket
    }
    mongo.db.koths.delete_one(old_king)
    print(f'Deleted old king: {old_king}')

    # make king vacant
    user = {
        'username': 'VACANT',
        'race': 0,
        'mmr': 0,
        'bracket': bracket,
        'is_king': True
    }

    try:
        mongo.db.koths.insert_one(user)
        print('Added document to db')
    except Exception as e:
        print(f'Error adding document: {e}')

    return redirect(request.referrer)