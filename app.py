from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3
import random
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)

# Database functions
def get_db_connection():
    conn = sqlite3.connect('poker_games.db')
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

# Create tables if they don't exist
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_name TEXT UNIQUE NOT NULL,
            chip_to_money_ratio REAL NOT NULL,
            casino_man_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (casino_man_id) REFERENCES users(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            buy_ins INTEGER DEFAULT 0,
            final_chips INTEGER DEFAULT 0,
            FOREIGN KEY (game_id) REFERENCES games(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games(id),
            FOREIGN KEY (player_id) REFERENCES players(id)
        )
    ''')
    conn.commit()
    conn.close()

create_tables()

# Load environment variables
SECRET_KEY = os.getenv('SECRET_KEY')
if SECRET_KEY:
    app.secret_key = SECRET_KEY
else:
    print("Error: SECRET_KEY not found in environment variables.")
    exit()

# User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       (username, generate_password_hash(password)))
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        conn.rollback()
        return jsonify({'message': 'Username already exists'}), 409
    finally:
        conn.close()

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']  # Store user ID in the session
        return jsonify({'message': 'Login successful', 'user_id': user['id']}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# User Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)  # Remove user ID from the session
    return jsonify({'message': 'Logout successful'}), 200

# Create a New Game
@app.route('/create_game', methods=['POST'])
def create_game():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.get_json()
    game_name = data.get('game_name')
    chip_to_money_ratio = data.get('chip_to_money_ratio')
    casino_man_type = data.get('casino_man_type')  # 'random' or 'select'
    selected_casino_man_id = data.get('selected_casino_man_id')

    if not game_name or not chip_to_money_ratio:
        return jsonify({'message': 'Game name and chip to money ratio are required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if casino_man_type == 'random':
            cursor.execute("SELECT id FROM users ORDER BY RANDOM() LIMIT 1")
            casino_man_id = cursor.fetchone()['id']
        elif casino_man_type == 'select' and selected_casino_man_id:
            casino_man_id = selected_casino_man_id
        else:
            return jsonify({'message': 'Invalid casino man selection'}), 400

        cursor.execute("INSERT INTO games (game_name, chip_to_money_ratio, casino_man_id) VALUES (?, ?, ?)",
                       (game_name, chip_to_money_ratio, casino_man_id))
        game_id = cursor.lastrowid
        conn.commit()
        return jsonify({'message': 'Game created successfully', 'game_id': game_id, 'casino_man_id': casino_man_id}), 201
    except sqlite3.IntegrityError:
        conn.rollback()
        return jsonify({'message': 'Game name already exists'}), 409
    finally:
        conn.close()

# Add Player to Game
@app.route('/add_player', methods=['POST'])
def add_player():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.get_json()
    game_id = data.get('game_id')
    user_id = data.get('user_id')  # User ID of the player to add

    if not game_id or not user_id:
        return jsonify({'message': 'Game ID and User ID are required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO players (game_id, user_id) VALUES (?, ?)", (game_id, user_id))
        conn.commit()
        return jsonify({'message': 'Player added successfully'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'message': 'Failed to add player', 'error': str(e)}), 500
    finally:
        conn.close()

# Update Buy-ins (Casino Man Only)
@app.route('/update_buy_ins', methods=['POST'])
def update_buy_ins():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.get_json()
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    buy_ins = data.get('buy_ins')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify Casino Man
    cursor.execute("SELECT casino_man_id FROM games WHERE id = ?", (game_id,))
    game = cursor.fetchone()
    if not game or game['casino_man_id'] != session['user_id']:
        conn.close()
        return jsonify({'message': 'Only the Casino Man can update buy-ins'}), 403

    # Verify Player
    cursor.execute("SELECT user_id from players where id = ?", (player_id,))
    player_to_update = cursor.fetchone()
    if player_to_update:
        player_user_id = player_to_update['user_id']
    else:
        conn.close()
        return jsonify({'message': 'Player not found'}), 404
    
    if player_user_id != session['user_id']:
        conn.close()
        return jsonify({'message': 'Player must verify themselves'}), 403

    try:
        cursor.execute("UPDATE players SET buy_ins = ? WHERE id = ? AND game_id = ?", (buy_ins, player_id, game_id))
        conn.commit()
        return jsonify({'message': 'Buy-ins updated successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'message': 'Failed to update buy-ins', 'error': str(e)}), 500
    finally:
        conn.close()

# Update Final Chip Count
@app.route('/update_final_chips', methods=['POST'])
def update_final_chips():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.get_json()
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    final_chips = data.get('final_chips')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE players SET final_chips = ? WHERE id = ? AND game_id = ?", (final_chips, player_id, game_id))
        conn.commit()
        return jsonify({'message': 'Final chips updated successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'message': 'Failed to update final chips', 'error': str(e)}), 500
    finally:
        conn.close()

# Suggest Players
@app.route('/suggest_players', methods=['GET'])
def suggest_players():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, username FROM users")
        users = [{'id': row['id'], 'username': row['username']} for row in cursor.fetchall()]
        return jsonify(users), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch user suggestions', 'error': str(e)}), 500
    finally:
        conn.close()

# Calculate and Return Results
@app.route('/calculate_results', methods=['POST'])
def calculate_results():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
    data = request.get_json()
    game_id = data.get('game_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Fetch game details and players' data
        cursor.execute("SELECT * FROM games WHERE id = ?", (game_id,))
        game = cursor.fetchone()
        if not game:
            return jsonify({'message': 'Game not found'}), 404
        cursor.execute("SELECT p.id, u.username, p.buy_ins, p.final_chips FROM players p JOIN users u ON p.user_id = u.id WHERE p.game_id = ?", (game_id,))
        players = cursor.fetchall()
        # Perform calculations
        total_buy_ins = sum(player['buy_ins'] for player in players)
        total_chips = sum(player['final_chips'] for player in players)
        chip_value = game['chip_to_money_ratio']
        results = []
        for player in players:
            amount = (player['final_chips'] - (player['buy_ins'] * chip_value))
            results.append({
                'player_id': player['id'],
                'username': player['username'],
                'buy_ins': player['buy_ins'],
                'final_chips': player['final_chips'],
                'amount': amount
            })
        # You can add more detailed transaction calculations here
        # For now, let's just return the basic results
        return jsonify({'results': results, 'game_name': game['game_name']}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to calculate results', 'error': str(e)}), 500
    finally:
        conn.close()

# Get Game Stats
@app.route('/game_stats/<int:game_id>', methods=['GET'])
def game_stats(game_id):
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Example: Get total buy-ins, total players, etc.
        cursor.execute("SELECT COUNT(id) AS total_players, SUM(buy_ins) AS total_buy_ins FROM players WHERE game_id = ?", (game_id,))
        stats = cursor.fetchone()

        return jsonify({
            'total_players': stats['total_players'],
            'total_buy_ins': stats['total_buy_ins']
        }), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch game stats', 'error': str(e)}), 500
    finally:
        conn.close()

# Get User Stats
@app.route('/user_stats/<int:user_id>', methods=['GET'])
def user_stats(user_id):
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Example: Get total games played, total buy-ins, etc.
        cursor.execute("SELECT COUNT(DISTINCT game_id) AS total_games, SUM(buy_ins) AS total_buy_ins FROM players WHERE user_id = ?", (user_id,))
        stats = cursor.fetchone()

        return jsonify({
            'total_games': stats['total_games'],
            'total_buy_ins': stats['total_buy_ins']
        }), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch user stats', 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/game_players/<int:game_id>', methods=['GET'])
def game_players(game_id):
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT p.id, u.username FROM players p JOIN users u ON p.user_id = u.id WHERE p.game_id = ?", (game_id,))
        players = [{'id': row['id'], 'username': row['username']} for row in cursor.fetchall()]
        return jsonify(players), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch players for game', 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/game')
def game_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('game.html')

if __name__ == '__main__':
    app.run(debug=True)