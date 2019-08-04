import functools, requests, json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, abort
)

from app.db import get_db

from app.auth import login_required

bp = Blueprint('result', __name__, url_prefix='/result')

class UserResultPair:
    """ Pair representing tuple of user and its result """
    def __init__(self):
        self.username = ""
        self.user_id = 0
        self.score = 0

    def get_id_from_name(self):
        db = get_db()
        user = db.execute("SELECT * FROM user WHERE username = '{}'".format(self.username)).fetchone()
        if user:
            print("user_id", user['id'])
            self.user_id = user['id']

class GameEntry:
    """" Entry for any played game """
    def __init__(self):
        self.date = ""
        self.map_url = ""
        self.results = []
        self.winner = ""

def get_sorted_results(formula):
    db = get_db()
    output = db.execute(formula)
    results = dict()
    for entry in output:
        winner = entry['winner']
        if winner in results:
            results[winner] += 1
        else:
            results[winner] = 1
    sorted_results = sorted(results.items(), key = lambda x : x[1])
    sorted_results.reverse()
    return sorted_results

def get_winner_and_results(request_form):
    db = get_db()
    winner = ["",0]
    results = []
    for entry in list(request_form)[1:]:
        if (str(request_form[entry]).isdigit()):
            user_result_pair = UserResultPair()
            user_result_pair.user_id = str(entry.split("_")[-1])
            user_result_pair.score = int(request_form[entry])
            results.append(user_result_pair)
            if winner[1] < user_result_pair.score:
                command = "SELECT id, username FROM user WHERE id = {}".format(user_result_pair.user_id)
                user = db.execute(command).fetchone()
                username = user['username']
                winner = [username, user_result_pair.score]
    return (winner, results)

def link_parser(link):
    content = str(requests.get(link).content)
    query_string = "window.apiModel = "
    start = content.find(query_string) + len(query_string)
    end = content[start:].find(";\\n")
    parsed = json.loads(content[start:start+end])
    map_id = parsed['mapSlug']
    keyword = 'hiScores'
    results = parsed[keyword]
    return_list = []
    winner = [results[0]['playerName'], results[0]['totalScore']]
    for entry in results:
        user_result_pair = UserResultPair()
        user_result_pair.username = entry['playerName']
        user_result_pair.score = entry['totalScore']
        user_result_pair.get_id_from_name()
        return_list.append(user_result_pair)
    return (winner, return_list, map_id)

def get_game_hash(link):
    return link.split("/")[-1]

def check_if_user_exists(username):
    db = get_db()
    formula = "SELECT * FROM user WHERE username = '{}'".format(username)
    result = db.execute(formula).fetchone()
    return result

def get_url_to_map(url_hash):
    return "https://geoguessr.com/maps/" + url_hash

@bp.route('/add')
@login_required
def add():
    return render_template('result/add.html')

@bp.route('/all_results')
def all_results():
    current_month_formula = "SELECT * FROM game WHERE datestamp BETWEEN date('now', 'start of month') AND date('now', 'start of month', '+1 month', '-1 day');"
    last_month_formula = "SELECT * FROM game WHERE datestamp BETWEEN date('now', 'start of month', '-1 month') AND date('now', 'start of month', '-1 day');"
    all_time_formula = "SELECT * FROM game"

    current_month = get_sorted_results(current_month_formula)
    last_month = get_sorted_results(last_month_formula)
    all_time = get_sorted_results(all_time_formula)
    return render_template('result/all_results.html', current_month=current_month, last_month=last_month, all_time=all_time)

@bp.route('/add_manually', methods=('GET', 'POST'))
@login_required
def add_manually():
    db = get_db()
    if request.method == 'POST':
        played_map = request.form['map']
        winner, results = get_winner_and_results(request.form)
        cur = db.execute(
            'INSERT INTO game (map, winner) VALUES (?, ?)',
             (played_map, winner[0])
        )
        for result in results:
            db.execute(
                'INSERT INTO result (user_id, game_id, score) VALUES (?, ?, ?)',
                (result.user_id, cur.lastrowid, result.score)
            )
        db.commit()

    users = db.execute('SELECT * FROM user').fetchall()
    return render_template('result/add_manually.html', users=users)

@bp.route('/add_by_link', methods=('GET', 'POST'))
@login_required
def add_by_link():
    ghost_users = []
    if request.method == 'POST':
        db = get_db()
        link_to_results = request.form['link']
        winner, results, map_id = link_parser(link_to_results)
        cur = db.execute(
            'INSERT INTO game (map, winner) VALUES (?, ?)',
             (map_id, winner[0])
        )
        for result in results:
            if (check_if_user_exists(result.username)):
                db.execute(
                    'INSERT INTO result (user_id, game_id, score) VALUES (?, ?, ?)',
                    (result.user_id, cur.lastrowid, result.score)
                )
            else:
                ghost_users.append(result.username)
        game_hash = get_game_hash(link_to_results)
        db.execute("INSERT INTO link (game_id, map_hash, game_hash) VALUES ('{}','{}','{}')".format(cur.lastrowid, map_id, game_hash))
        db.commit()
    if len(ghost_users) > 0:
        ghosts = ", ".join(ghost_users)
        flash("Poniżsi użytkownicy nie istnieją i nie zostają uwzględnieni w bazie danych wyników: {}".format(ghosts))
    return render_template('result/add_by_link.html')

@bp.route('/summary')
@login_required
def summary():
    class Player:
        def __init__(self):
            self.id = ""
            self.name = ""

    class Score:
        def __init__(self):
            self.value = 0
            self.winner = False

    db = get_db()
    games = []
    players = []

    # Prepare the players
    users_db = db.execute('SELECT * FROM user').fetchall()
    for user in users_db:
        if (user['username'] != 'admin'):
            player = Player()
            player.id = user['id']
            player.name = user['username']
            players.append(player)

    # Get list of all games
    games_db = db.execute('SELECT * FROM game').fetchall()
    # For every game
    for game in games_db:
        # Create an instance of GameEntry
        game_entry = GameEntry()
        game_id = game['id']
        game_entry.date = game['datestamp']
        game_entry.map_url = get_url_to_map(game['map'])
        game_entry.winner = game['winner']

        for player in players:
            formula = "SELECT * FROM result WHERE user_id = '{}' AND game_id = '{}'".format(player.id, game_id)
            result = db.execute(formula).fetchone()
            score = Score()
            if result:
                score.value = result['score']
            else:
                score.value = "x"
            score.winner = True if player.name == game_entry.winner else False
            game_entry.results.append(score)

        games.append(game_entry)

    return render_template('result/summary.html', games=games, players=players)