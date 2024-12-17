from colorama import Fore, Style
from wordle_bot import EntropyMaximisationAgent 
import time
import sys

# Function to change colour of text in the terminal
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

# Function to convert text file with possible answers list into an array
def load_possible_answers(file_name):
    with open(file_name, 'r') as file:
        possible_answers = [line.strip() for line in file.readlines()]
    return possible_answers

# Function to convert text file with allowed words list into an array
def load_allowed_words(file_name):
    with open(file_name, 'r') as file:
        allowed_words = [line.strip() for line in file.readlines()]
    return allowed_words

POSSIBLE_ANSWERS = load_possible_answers("data/possible_answers.txt")
ALLOWED_WORDS = load_allowed_words("data/allowed_words.txt")

# Function to generate a random number (linear congruential generator)
def generate_random_number(multiplier, increment, modulus):
    seed = int(time.time() * 1000)  # Generate "random" seed value
    random_number = (multiplier * seed + increment) % modulus
    return random_number

# Function to choose a random target word
def choose_target_word():
    random_index = generate_random_number(1663, 123, len(POSSIBLE_ANSWERS))
    target_word = POSSIBLE_ANSWERS[random_index]
    return target_word

# Function to return a coloured guess pattern after a particular guess
def get_guess_pattern(guess, target_word):

    # All letters in guess pattern initially set to grey
    guess_pattern = [change_text_colour(letter, "GREY") for letter in guess.upper()]
    target_word = list(target_word)

    # First pass (checks for letters that are in the word and are in the correct spot)
    for i in range(len(guess)):
        if guess[i] == target_word[i]:
            guess_pattern[i] = change_text_colour(guess[i].upper(), "GREEN")
            target_word[i] = None

    # Second pass (checks for letters that are in the word but are not in the correct spot)
    for i in range(len(guess)):
        if Fore.GREEN not in guess_pattern[i] and guess[i] in target_word:
            guess_pattern[i] = change_text_colour(guess[i].upper(), "YELLOW")
            target_word[target_word.index(guess[i])] = None

    guess_pattern = " ".join(guess_pattern)
    return guess_pattern

# Funtion to draw a border (used for game grid and on-screen keyboard)
def draw_border(lines, content_width=9, space_width=1):
    top_border = "┌" + "─" * (content_width + space_width * 2) + "┐"
    bottom_border = "└" + "─" * (content_width + space_width * 2) + "┘"
    space = " " * space_width
    print(top_border)
    for line in lines:
        print("│" + space + line + space + "│")
    print(bottom_border)

MAX_WORD_LENGTH = 5
MAX_ATTEMPTS = 6

# Function to display game grid
def display_game_grid(guess_pattern_list):
    lines = []
    for guess_pattern in guess_pattern_list:
        lines.append(guess_pattern)
    while len(lines) < MAX_ATTEMPTS:
        lines.append(" ".join(["_"] * MAX_WORD_LENGTH))
    draw_border(lines, content_width=MAX_WORD_LENGTH * 2 - 1, space_width=1)

# Function to draw keyboard
def draw_keyboard(key_colors):
    keyboard_layout = [
        ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
        ["Z", "X", "C", "V", "B", "N", "M"]
    ]
    row_formats = [
        "  {} {} {} {} {} {} {} {} {} {}  ",
        "   {} {} {} {} {} {} {} {} {}   ",
        "     {} {} {} {} {} {} {}     "
    ]
    keyboard_rows = []
    for row_index, row_keys in enumerate(keyboard_layout):
        formatted_keys = [change_text_colour(key, key_colors.get(key, "WHITE")) for key in row_keys]
        keyboard_rows.append(row_formats[row_index].format(*formatted_keys))
    draw_border(keyboard_rows, content_width=23, space_width=1)

# Function to update the colours of letters on the on-screen keyboard
def update_keyboard_colors(guess, target_word, key_colors):
    target_word_list = list(target_word)

    # First pass (checks for letters that are in the word and are in the correct spot)
    for i, letter in enumerate(guess):
        if guess[i] == target_word[i]:
            key_colors[letter.upper()] = "GREEN"
            target_word_list[i] = None

    # Second pass (checks for letters that are in the word but are not in the correct spot)
    for i, letter in enumerate(guess):
        if letter.upper() not in key_colors:
            if letter in target_word_list:
                key_colors[letter.upper()] = "YELLOW"
                target_word_list[target_word_list.index(letter)] = None
            else:  # If letter is not in the word, then change letter colour to grey
                key_colors[letter.upper()] = "GREY"

# Function to output text in the terminal like a typewriter
def typewriter_effect(text, delay=0.05):
    result = ""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
        result += char
    return result

# Function to perform a binary search on an array
def binary_search(array, lower_index, upper_index, target_item):

    # Base case (target is not found)
    if lower_index > upper_index:
        return -1
    
    # Search for target item
    middle_index = (upper_index + lower_index) // 2
    if array[middle_index] == target_item:
        return middle_index
    elif array[middle_index] > target_item:
        return binary_search(array, lower_index, middle_index - 1, target_item)
    elif array[middle_index] < target_item:
        return binary_search(array, middle_index + 1, upper_index, target_item)

# Function to run the main game loop
def play_game(player_id, player_db, max_bot_guesses=3):
    target_word = choose_target_word()  # Select a random target word for the player to guess
    guess = None
    target_word_guessed = False
    attempts = 0
    bot_guesses_used = 0
    guess_pattern_list = []  # Stores feedback patterns for each guess
    key_colors = {}  # Tracks the colour-coded status of letters on the virtual keyboard
    entropy_bot = EntropyMaximisationAgent()
    possible_guesses = ALLOWED_WORDS

    # Introduction and tutorial section
    print(change_text_style("NEW GAME\n", "BOLD"))
    typewriter_effect(f"Hello, I'm {change_text_colour('Lexi', 'CYAN')} the Wordle bot!\n\n")
    typewriter_effect("I'll be guiding you through this Wordle game. Let's see how quickly you can guess the word!\n\n")
    
    while True:
        try:
            # Prompt player to decide if they want a tutorial
            typewriter_effect("Would you like me to explain how to play? (y/n): ")
            display_rules = input().strip().lower()
            print()
            if display_rules not in ["y", "n"]:
                raise ValueError(change_text_colour("Invalid input. Please enter 'y' or 'n'.\n", "RED"))
            
            # Show tutorial if player agrees
            if display_rules == "y":
                typewriter_effect("How To Play:\n\n")
                typewriter_effect("    • You have six attempts to guess a five-letter word.\n\n")
                typewriter_effect("    • The colour of a letter will show you how close your guess was.\n\n")
                typewriter_effect(f"    • If the letter is {change_text_colour('green', 'GREEN')}, the letter is in the word and in the correct spot.\n\n")
                typewriter_effect(f"    • If the letter is {change_text_colour('yellow', 'YELLOW')}, the letter is in the word but in the wrong spot.\n\n")
                typewriter_effect(f"    • If the letter is {change_text_colour('grey', 'BLACK')}, the letter is not in the word at all.\n\n")
                typewriter_effect(f"    • By typing {change_text_colour('generate guess', 'CYAN')}, I'll find the best possible guess based on remaining words and display it.\n\n")
                typewriter_effect("    • You are allowed three generated guesses per game.\n\n")
                typewriter_effect(f"    • Using them will affect the amount of {change_text_colour('win', 'GREEN')}/{change_text_colour('loss', 'RED')} points you receive, so use them wisely!\n\n")
            
            # Start the game after tutorial
            typewriter_effect("Okay, let's begin the game!\n\n")
            break

        except ValueError as e:
            print(f"\n{e}")
            continue

    # Display the initial game grid and keyboard
    display_game_grid(guess_pattern_list)
    draw_keyboard(key_colors)

    print()

    # Main game loop, continues until player runs out of attempts or guesses the word
    while attempts < MAX_ATTEMPTS and not target_word_guessed:
        valid_guess = False
        while not valid_guess:

            # Show remaining bot guesses if any are available
            if bot_guesses_used < max_bot_guesses:
                print(change_text_colour(f"Generated guesses remaining: {max_bot_guesses - bot_guesses_used} (type 'generate guess' to use hint)\n", "GREY"))

            # Prompt player to enter a guess
            prompt_text = f"Attempt {attempts + 1}. Enter a 5-letter word: "
            guess = input(prompt_text).lower().strip()
            print()

            # Handle bot-generated guess request
            if guess == "generate guess":
                if bot_guesses_used < max_bot_guesses:
                    bot_guesses_used += 1
                    if attempts == 0:
                        suggested_guess = "tares"  # Predefined first guess for optimization
                    else:
                        typewriter_effect(change_text_colour("Generating guess. One moment please...\n", "CYAN")) 
                        print()
                        suggested_guess = entropy_bot.choose_best_guess(entropy_bot.generate_expected_information_dictionary(possible_guesses))  # Generate a guess based on entropy maximization
                    print(change_text_colour(f"Suggested guess: {suggested_guess.upper()}\n", "YELLOW"))
                else:
                    print(change_text_colour("No remaining bot guesses available.\n", "RED"))  # Notify player if no bot guesses are available
                continue

            # Validate player's guess
            if len(guess) != MAX_WORD_LENGTH:
                print(change_text_colour("Please enter a 5-letter word.\n", "RED"))
            elif binary_search(ALLOWED_WORDS, 0, len(ALLOWED_WORDS) - 1, guess) == -1:
                print(change_text_colour("Word not in allowed word list. Try again.\n", "RED"))
            else:
                valid_guess = True  # Mark guess as valid

        # Generate feedback for the guess
        guess_pattern = get_guess_pattern(guess, target_word)
        guess_pattern_list.append(guess_pattern)  # Add feedback to the game grid

        # Update and display the game grid and keyboard colors
        display_game_grid(guess_pattern_list)
        update_keyboard_colors(guess, target_word, key_colors)
        draw_keyboard(key_colors)
        print()

        # Check if the guess matches the target word
        if guess == target_word:
            print(change_text_colour("Congratulations! You've guessed the word!\n", "GREEN"))
            target_word_guessed = True

            # Update player's stats in the database
            player_db.update_player_stats(player_id, True, attempts + 1, bot_guesses_used)
            
            break

        # Filter possible guesses based on the feedback pattern
        coded_pattern = entropy_bot.get_coded_guess_pattern(guess, target_word)
        possible_guesses = [
            word for word in possible_guesses
            if entropy_bot.get_coded_guess_pattern(guess, word) == coded_pattern
        ]

        attempts += 1

    # Handle case where player uses all attempts without guessing the word
    if not target_word_guessed:
        print(change_text_colour("Sorry, you've used all your attempts.\n", "RED")) 
        print("The word was " + change_text_colour(str(target_word), "GREEN") + ".\n")

        # Update player's stats in the database for a loss
        player_db.update_player_stats(player_id, False, 6, bot_guesses_used)