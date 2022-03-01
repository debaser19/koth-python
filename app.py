from flask import Flask, redirect, render_template, request, url_for
from flask_pymongo import PyMongo
import requests

import config


app = Flask(__name__)
app.config["MONGO_URI"] = config.MONGO_URI
app.config.update(TEMPLATES_AUTO_RELOAD=True)
mongo = PyMongo(app)


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
        title='Gym KOTH!',
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
        title='Gym KOTH!',
        users=users,
        kings=kings,
        )

@app.route('/signup', methods=['POST', 'GET'])
def signup_user():
    return render_template(
        'signup.html',
        title='KOTH Sign up',
    )

@app.route('/add_users', methods=['POST', 'GET'])
def add_user():
    username = request.form['username'].replace('#', '%23')
    race = request.form['race']
    res = requests.get(config.w3c_url + username + '/game-mode-stats?gateWay=20&season=10')
    for item in res.json():
        if item['gameMode'] == 1 and item['race'] == int(race):
            # determine bracket based on mmr
            if int(item['mmr']) > 1600:
                bracket = 1
            elif int(item['mmr']) < 1450:
                bracket = 3
            else:
                bracket = 2
            user = {
                'username': username.replace('%23', '#'),
                'race': int(race),
                'mmr': int(item["mmr"]),
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
    username = request.form['username'].replace('#', '%23')
    race = request.form['race']
    res = requests.get(config.w3c_url + username + '/game-mode-stats?gateWay=20&season=10')
    for item in res.json():
        if item['gameMode'] == 1 and item['race'] == int(race):
            # determine bracket based on mmr
            if int(item['mmr']) > 1600:
                bracket = 1
            elif int(item['mmr']) < 1450:
                bracket = 3
            else:
                bracket = 2
            user = {
                'username': username.replace('%23', '#'),
                'race': int(race),
                'mmr': int(item["mmr"]),
                'bracket': bracket,
                'is_king': False
            }

            try:
                mongo.db.koths.insert_one(user)
                print('Added document to db')
            except Exception as e:
                print(f'Error adding document: {e}')

    return redirect('/')


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
    print('HOTDOGS')
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
    new_value = {'$set': {'is_king': True}}
    mongo.db.koths.update_one(user, new_value)
    print(f'Made {user["username"]} king!')

    return redirect(request.referrer)
