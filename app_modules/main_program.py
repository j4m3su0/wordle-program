from colorama import Fore, Style
import game_logic
from database_system import PlayerDatabase, DatabaseConnection
import msvcrt

DIVIDER = "=" * 115 + "\n"  # Divides terminal when a new menu is displayed

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

# Function to display start menu
def display_start_menu():
    print(DIVIDER)
    print(change_text_style("START MENU\n", "BOLD"))
    print("Welcome to WordlePlus!\n")
    start_menu_options = change_text_colour(
        "   1. Create new account\n\n"
        "   2. Log in\n\n"
        "   3. Exit program\n", 
        "CYAN"
        )
    print(start_menu_options)

# Function to display main menu
def display_main_menu():
    print(DIVIDER)
    print(change_text_style("MAIN MENU\n", "BOLD"))
    main_menu_options = change_text_colour(
        "   1. Start new game\n\n"
        "   2. View leaderboard\n\n"
        "   3. Log out\n\n"
        "   4. Delete account\n",  
        "CYAN"
        )
    print(main_menu_options)

# Function to display leaderboard
def display_leaderboard(leaderboard):
    print(DIVIDER)
    print(change_text_style("LEADERBOARD", "BOLD"))
    print(leaderboard)

# Function to validate and retrieve menu option choice from user
def get_menu_option_choice(prompt, first_option, last_option):
    while True:
        try:
            choice = int(input(prompt))
            print()

            # Valid input inputted
            if first_option <= choice <= last_option:
                return choice
            
            # Invalid input inputted (input was not a number in the valid range)
            else:
                print(change_text_colour(f"Please enter a valid menu choice ({first_option}-{last_option}).\n", "RED"))

        # Invalid input inputted (input was not a number)
        except ValueError:
            print(change_text_colour("\nInvalid input. Please enter a number.\n", "RED"))

# Function to mask login password with asterisks
def mask_password_input(prompt):
    print(prompt, end="", flush=True)
    password = ""
    while True:
        char = msvcrt.getch()

        # If enter key is pressed, print a new line
        if char == b'\r':
            print()
            break

        # If backspace key is pressed, remove the last character from the password
        elif char == b'\x08':
            if len(password) > 0:
                password = password[:-1]
                print('\b \b', end='', flush=True)

        # If regular key pressed, masks key with an asterisk
        else:
            password += char.decode("utf-8")
            print('*', end='', flush=True)

    return password

# Function to handle start menu 
def handle_start_menu(player_db):
    while True:
        display_start_menu()
        try:
            start_menu_option_choice = get_menu_option_choice("Enter an option (1-3): ", 1, 3)
            if start_menu_option_choice not in [1, 2, 3]:
                raise ValueError("Invalid choice. Please enter a number between 1 and 3.\n")
            
            # Create new account
            if start_menu_option_choice == 1:
                return handle_account_creation(player_db)
            
            # Log in
            elif start_menu_option_choice == 2:
                return handle_login(player_db)
            
            # Exit program
            elif start_menu_option_choice == 3:
                print(change_text_colour("Exiting the game... Goodbye!\n", "GREEN"))
                exit()

        except ValueError as e:
            print(e)
            print()

# Function to handle account creation
def handle_account_creation(player_db):
    while True:
        username = input("Choose a username: ")
        print()
        password = mask_password_input("Choose a password: ")
        print()
        player_id = player_db.add_player(username, password)#

        # Account creation successful
        if player_id:  
            print(change_text_colour("Account creation successful! You can now log in.\n", "GREEN"))
            return player_id, False  # Go to main menu
        
        # Account creation unsuccessful
        else:
            print(change_text_colour("Username already exists. Please try again.\n", "RED"))
            while True:
                try:
                    response = input(change_text_colour("Do you want to return to the start menu? (y/n): ", "YELLOW")).strip().lower()
                    print()

                    # Invalid input inputted
                    if response not in ['y', 'n']:
                        raise ValueError(change_text_colour("Invalid input. Please enter 'y' or 'n'.\n", "RED"))
                    
                    if response == 'y':
                        return None, True  # Go to start menu
                    break
                except ValueError as e:
                    print(e)
                    print()

# Function to handle login
def handle_login(player_db):
    while True:
        username = input("Enter your username: ")
        print()
        password = mask_password_input("Enter your password: ")
        print()
        player_id = player_db.verify_login(username, password)
        
        # Login successful
        if player_id:
            print(change_text_colour("Logging in...\n", "YELLOW"))
            print(change_text_colour("Login successful! Welcome back!\n", "GREEN"))
            return player_id, False  # Go to main menu
        
        # Login unsuccessful
        else:
            print(change_text_colour("Invalid username or password. Please try again.\n", "RED"))

            while True:
                user_input = input(change_text_colour("Do you want to return to the start menu? (y/n): ", "YELLOW")).strip().lower()
                print()
                
                if user_input == 'y':
                    return None, True  # Go to start menu
                elif user_input == 'n':
                    break 

                # Invalid input inputted
                else:
                    print(change_text_colour("Invalid input. Please enter 'y' for yes or 'n' for no.\n", "RED"))
                    continue

# Function to handle main menu
def handle_main_menu(player_db, player_id):
    while True:
        display_main_menu()
        main_menu_option_choice = None
        while main_menu_option_choice not in [1, 2, 3, 4]:
            try:
                main_menu_option_choice = get_menu_option_choice("Please enter a menu choice (1-4): ", 1, 4)

                # Invalid menu option choice inputted
                if main_menu_option_choice not in [1, 2, 3, 4]:
                    raise ValueError("Invalid choice. Please enter a number between 1 and 4.")
                
            except ValueError as e:
                print(e)
                print()

        # Play new game
        if main_menu_option_choice == 1:
            print(DIVIDER)
            game_logic.play_game(player_id, player_db)
    
        # View leaderboard
        elif main_menu_option_choice == 2:
            display_leaderboard(player_db.get_leaderboard_message())

        # Log out
        elif main_menu_option_choice == 3:
            print(change_text_colour("Logging out...\n", "YELLOW"))
            return True  # Go to start menu
    
        # Delete account
        elif main_menu_option_choice == 4:
            while True:
                try:
                    response = input(change_text_colour("Are you sure you want to delete your account? (y/n): ", "RED")).strip().lower()
                    print()

                    # Invalid input inputted
                    if response not in ['y', 'n']:
                        raise ValueError("Invalid input. Please enter 'y' or 'n'.\n")
                    
                    if response == 'y':
                        player_db.delete_account(player_id)
                        print(change_text_colour("Account deletion successful.\n", "GREEN"))
                        return True  # Exit program
                    break
                except ValueError as e:
                    print(e)
                    print()
            return True

# Function to run main program      
def main():
    db_conn = DatabaseConnection()
    player_db = PlayerDatabase(db_conn)
    go_to_start_menu = True
    print()
    while go_to_start_menu:
        player_id, go_to_start_menu = handle_start_menu(player_db)

        # If a player ID has been returned, the user has logged in or created an account successfully, so go to main menu
        if player_id is not None:
            while True:
                go_to_start_menu = handle_main_menu(player_db, player_id)
                if go_to_start_menu:
                    break # If the user logs out, go to start menu

    db_conn.close()

if __name__ == "__main__":
    main()