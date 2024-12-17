import math
import time

def load_possible_answers(file_name):
    with open(file_name, 'r') as file:
        possible_answers = [line.strip() for line in file.readlines()]
    return possible_answers

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

class EntropyMaximisationAgent:
    def get_coded_guess_pattern(self, guess, target_word):
        coded_guess_pattern = ["B", "B", "B", "B", "B"]
        target_word = list(target_word)

        for i in range(len(guess)):
            if guess[i] == target_word[i]:
                coded_guess_pattern[i] = "G"
                target_word[i] = None
        for i in range(len(guess)):
            if coded_guess_pattern[i] != "G" and guess[i] in target_word:
                coded_guess_pattern[i] = "Y"
                target_word[target_word.index(guess[i])] = None

        return coded_guess_pattern
    
    def generate_coded_guess_pattern_combinations(self):
        combinations_list = []
        characters = ["G", "Y", "B"]

        for a in characters:
            for b in characters:
                for c in characters:
                    for d in characters:
                        for e in characters:
                            combinations_list.append([a, b, c, d, e])

        return combinations_list

    def calculate_guess_pattern_probability(self, guess, coded_guess_pattern, possible_words):
        possible_words_before_guess = possible_words

        for i in range(len(guess)):
            if coded_guess_pattern[i] == "G":
                possible_words = [word for word in possible_words if guess[i] == word[i]]
            elif coded_guess_pattern[i] == "Y":
                possible_words = [word for word in possible_words if guess[i] in word and guess[i] != word[i]]
            elif coded_guess_pattern[i] == "B":
                possible_words = [word for word in possible_words if guess[i] not in word]

        possible_words_after_guess = possible_words
        
        if len(possible_words_before_guess) == 0:
            return 0 
        
        guess_pattern_probability = len(possible_words_after_guess) / len(possible_words_before_guess)
        return guess_pattern_probability
    
    def calculate_expected_information(self, guess):
        guess_pattern_combinations = self.generate_coded_guess_pattern_combinations()
        expected_information = 0

        for guess_pattern in guess_pattern_combinations:
            guess_pattern_probability = self.calculate_guess_pattern_probability(guess, guess_pattern, ALLOWED_WORDS)
            if guess_pattern_probability > 0:
                expected_information += guess_pattern_probability * math.log(1 / guess_pattern_probability, 2)

        return expected_information

    def generate_expected_information_dictionary(self, word_list):
        expected_information_dict = {}
        possible_words = word_list

        for word in possible_words:
            expected_information = round(self.calculate_expected_information(word), 3)
            expected_information_dict[word] = expected_information

        sorted_expected_information_dict = dict(sorted(expected_information_dict.items(), key=lambda item: item[1], reverse=True))
        return sorted_expected_information_dict

    def choose_best_guess(self, expected_information_dict):
        return max(expected_information_dict, key=expected_information_dict.get)

    def simulate_game(self, target_word):
        possible_words = ALLOWED_WORDS
        attempts = 0
        guessed_correctly = False
        first_guess = "tares"
        
        guess = first_guess
        attempts += 1

        if guess == target_word:
            return True, attempts
        else:
            guess_pattern = self.get_coded_guess_pattern(guess, target_word)
            possible_words = [word for word in possible_words if self.get_coded_guess_pattern(guess, word) == guess_pattern]

        while not guessed_correctly and attempts < 6:
            expected_information_dict = self.generate_expected_information_dictionary(possible_words)
            guess = self.choose_best_guess(expected_information_dict)
            attempts += 1

            if guess == target_word:
                guessed_correctly = True
            else:
                guess_pattern = self.get_coded_guess_pattern(guess, target_word)
                possible_words = [word for word in possible_words if self.get_coded_guess_pattern(guess, word) == guess_pattern]

        return guessed_correctly, attempts
    
    def simulate_multiple_games(self, num_games):
        wins = 0
        total_attempts = 0

        for _ in range(num_games):
            target_word = ALLOWED_WORDS[generate_random_number(0, len(ALLOWED_WORDS))]
            
            guessed_correctly, attempts = self.simulate_game(target_word)
            if guessed_correctly:
                wins += 1
            total_attempts += attempts

        win_percentage = (wins / num_games) * 100
        average_attempts = total_attempts / num_games

        return win_percentage, average_attempts