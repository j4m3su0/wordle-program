from colorama import Fore, Style
import sqlite3
import time

# Function to change the color of text in the terminal
def change_text_colour(text, colour):
    if colour == "GREEN":
        return Fore.GREEN + text + Fore.RESET
    elif colour == "YELLOW":
        return Fore.YELLOW + text + Fore.RESET
    elif colour == "WHITE":
        return Fore.WHITE + text + Fore.RESET
    elif colour == "RED":
        return Fore.RED + text + Fore.RESET
    elif colour == "CYAN":
        return Fore.CYAN + text + Fore.RESET
    elif colour == "GREY":
        return Fore.BLACK + text + Fore.RESET

# Function to change the style of text in the terminal
def change_text_style(text, style):
    if style == "BOLD":
        return Style.BRIGHT + text + Style.RESET_ALL

# Function to generate a random number (linear congruential generator)
def generate_random_number(multiplier, increment, modulus):
    seed = int(time.time() * 1000)  # Generate "random" seed value
    random_number = (multiplier * seed + increment) % modulus
    return random_number

# Function to generate a random string of characters to serve as a salt
def generate_random_salt(salt_length=32):
    salt = []
    multiplier = 1103515245
    increment = 12345
    modulus = 2**32  # Salt must be 32 bits long
    for _ in range(salt_length):
        random_byte = generate_random_number(multiplier, increment, modulus) & 0xFF
        salt.append(chr(random_byte))  # Convert byte to character
    return ''.join(salt)

# Function to hash a password using a simple hashing function with a salt
def hash_password(password):
    salt = generate_random_salt()  # Generate a random salt
    salted_password = salt + password
    hash_value = 0

    # Hashing mechanism using character encoding and bitwise operations
    for char in salted_password:
        hash_value = (hash_value * 31 + ord(char)) & 0xFFFFFFFF
        hash_value ^= (hash_value >> 16) | (hash_value << 16)

    hashed_password = format(hash_value, '08x')  # Convert hash value to hexadecimal string
    return salt, hashed_password

# Class to manage the database connection and structure
class DatabaseConnection:
    def __init__(self, db_name='wordleplus.db'):
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()
        self.create_tables()  # Ensure required tables are created upon initialization

    # Method to create the players table if it doesn't already exist
    def create_tables(self):
        # self.c.execute('DROP TABLE IF EXISTS players')  # Uncomment to reset the database
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                salt TEXT NOT NULL UNIQUE,
                win_points REAL DEFAULT 0.0,
                loss_points REAL DEFAULT 0.0,
                total_games INTEGER DEFAULT 0,
                total_attempts INTEGER DEFAULT 0,
                attempt_average REAL DEFAULT 0.0
            )
        ''')
        self.conn.commit()

    # Method to close the database connection
    def close(self):
        self.conn.close()

# Class to manage player-related operations in the database
class PlayerDatabase:
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self.c = self.db_conn.c  # Use the cursor from the database connection

    # Method to add a new player to the database
    def add_player(self, username, password):
        salt, hashed_password = hash_password(password)  # Hash the player's password
        self.c.execute('SELECT id FROM players WHERE username = ?', (username,))  # Check if username already exists
        if self.c.fetchone() is None:
            self.c.execute('INSERT INTO players (username, password, salt) VALUES (?, ?, ?)', (username, hashed_password, salt))
            self.db_conn.conn.commit()
            return self.c.lastrowid  # Return the ID of the newly added player
        return None  # Return None if the username already exists

    # Method to check if a player exists in the database
    def check_player_exists(self, username):
        self.c.execute('SELECT 1 FROM players WHERE username = ?', (username,))
        return self.c.fetchone() is not None

    # Method to verify login credentials for a player
    def verify_login(self, username, password):
        self.c.execute('SELECT password, salt, id FROM players WHERE username = ?', (username,))
        result = self.c.fetchone()
        if result:
            stored_password, stored_salt, player_id = result

            # Recreate the salted password hash to compare with the stored e
            salted_input_password = stored_salt + password
            hash_value = 0
            for char in salted_input_password:
                hash_value = (hash_value * 31 + ord(char)) & 0xFFFFFFFF
                hash_value ^= (hash_value >> 16) | (hash_value << 16)
            input_hash = format(hash_value, '08x')

            if input_hash == stored_password:
                return player_id  # Return player ID if credentials are valid
        return None  # Return None if credentials are invalid

    # Method delete a player's account from the database
    def delete_account(self, player_id):
        self.c.execute('DELETE FROM players WHERE id = ?', (player_id,))
        self.db_conn.conn.commit()

    # Method to update a player's game statistics in the database
    def update_player_stats(self, player_id, won, attempts, bot_guesses_used):
        self.c.execute('SELECT win_points, loss_points, total_games, total_attempts, attempt_average FROM players WHERE id = ?', (player_id,))
        player_data = self.c.fetchone()
        win_points, loss_points, total_games, total_attempts, attempt_average = player_data

        # Update points based on whether the player won or lost
        if won:
            if bot_guesses_used == 0:
                win_points += 1
            else:
                win_points += (1 / bot_guesses_used + 1)
        else:
            if bot_guesses_used == 0:
                loss_points += 1
            else:
                loss_points += bot_guesses_used
        
        total_games += 1  # Increment the number of games played
        total_attempts += attempts  # Calculate the total attempts so far

        if total_games > 0:
            attempt_average = total_attempts / total_games  # Recalculate the average attempts per game
        else:
            attempt_average = 0
        self.c.execute(
            'UPDATE players SET win_points = ?, loss_points = ?, total_games = ?, total_attempts = ?, attempt_average = ? WHERE id = ?',
            (win_points, loss_points, total_games, total_attempts, attempt_average, player_id)
        )
        self.db_conn.conn.commit()

    # Method to calculate the leaderboard score for a player
    def calculate_leaderboard_score(self, win_points, loss_points, total_games, attempt_average):
        if total_games == 0:
            return 0  # Return 0 if no games have been played
        
        base_score = win_points * 100
        win_percentage = win_points / total_games
        attempts_multiplier = max(1, (7 - attempt_average) / 2)  # Higher multiplier for fewer attempts
        loss_penalty = min(0.3, loss_points / total_games)  # Penalty for losses
        leaderboard_score = base_score * win_percentage * attempts_multiplier * (1 - loss_penalty)
        return round(leaderboard_score)

    # Method to generate a leaderboard message displaying player rankings
    def get_leaderboard_message(self):
        self.c.execute('SELECT username, win_points, loss_points, total_games, attempt_average FROM players')
        leaderboard = self.c.fetchall()
        if not leaderboard:
            return change_text_colour("No players available on the leaderboard yet.\n", "RED")

        # Calculate scores for all players and sort them
        scored_leaderboard = [
            (username, win_points, loss_points, total_games, attempt_average, self.calculate_leaderboard_score(win_points, loss_points, total_games, attempt_average))
            for username, win_points, loss_points, total_games, attempt_average in leaderboard
        ]
        scored_leaderboard.sort(key=lambda x: x[5], reverse=True)
        # Format the leaderboard into a message
        leaderboard_message = ""
        for rank, (username, win_points, loss_points, total_games, attempt_average, score) in enumerate(scored_leaderboard, start=1):
            leaderboard_message += (
                f"\n    {rank}. {username}: "
                f"{change_text_colour(f'Leaderboard Score: {score}', 'GREEN')}" + " | "
                f"{change_text_colour(f'Win Pts.: {round(win_points, 1)}', 'CYAN')}" + " | "
                f"{change_text_colour(f'Loss Pts.: {round(loss_points, 1)}', 'RED')}" + " | "
                f"{change_text_colour(f'Total Games: {total_games}', 'YELLOW')}" + " | "
                f"{change_text_colour(f'Avg. Attempts: {round(attempt_average, 1)}', 'GREY')}\n"
            )
        return leaderboard_message
