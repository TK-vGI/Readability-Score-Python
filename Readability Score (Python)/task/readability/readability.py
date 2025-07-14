import sys
import math
import re
from nltk.tokenize import sent_tokenize, regexp_tokenize


def print_output(text: str, tokens: list, ari_score: list, fk_score: list, dc_score: list , avg_age:float) -> None:
    print("Text:", text.strip())
    print()
    print("Characters:", tokens[0])
    print("Sentences:", tokens[1])
    print("Words:", tokens[2])
    print("Difficult Words:", tokens[4])
    print("Syllables:", tokens[3])
    print()
    print(f"Automated Readability Index: {ari_score[0]} (this text should be understood by {ari_score[1]} year olds).")
    print(f"Flesch–Kincaid Readability Test: {fk_score[0]} (about {fk_score[1]} year olds).")
    print(f"Dale-Chall Readability Index: {dc_score[0]}. The text can be understood by {dc_score[1]} year olds.")
    print(f"This text should be understood in average by {avg_age:.1f} year olds.")

def get_age(score: int) -> str:
    age_table = {
        1: "5-6",
        2: "6-7",
        3: "7-8",
        4: "8-9",
        5: "9-10",
        6: "10-11",
        7: "11-12",
        8: "12-13",
        9: "13-14",
        10: "14-15",
        11: "15-16",
        12: "16-17",
        13: "17-18",
        14: "18-22",
    }
    return age_table.get(min(score, 14), "Unknown")

def get_ari(tokens: list) -> list:
    # tokens = [num_sentences, num_words, characters]
    ari = 4.71 * (tokens[0] / tokens[2]) + 0.5 * (tokens[2] / tokens[1]) - 21.43
    rounded_score = math.ceil(ari)
    age = get_age(rounded_score)
    return [rounded_score, age]

def get_fk(tokens: list) -> list:
    fk = 0.39 * (tokens[2] / tokens[1]) + 11.8 * (tokens[3] / tokens[2]) - 15.59
    rounded_score = math.ceil(fk)
    age = get_age(rounded_score)
    return [rounded_score, age]

def get_dc(tokens: list) -> list:
    difficult_ratio = tokens[4] / tokens[2]
    base_score = 0.1579 * difficult_ratio * 100 + 0.0496 * (tokens[2] / tokens[1])
    if difficult_ratio > 0.05:
        base_score += 3.6365
    rounded_score = math.ceil(base_score)
    age = get_age(rounded_score)
    return [rounded_score, age]

def count_syllables(words: list) -> int:
    syllable_count = 0

    for word in words:
        word = word.lower()
        syllables_in_word = 0

        # Remove silent trailing 'e'
        if word.endswith("e"):
            word = word[:-1]

        # Find all vowel groups
        vowel_groups = re.findall(r'[aeiouy]+', word)

        if len(vowel_groups) == 0:
            syllables_in_word = 1
        else:
            for vg in vowel_groups:
                if len(vg) == 3:
                    syllables_in_word += 2
                else:
                    syllables_in_word += 1

        syllable_count += syllables_in_word

    return syllable_count

def count_difficult_words(words: list, easy_words: list) -> int:
    return sum(1 for word in words if word not in easy_words)

def get_tokens(text: str, easy_words: list) -> list | None:
    sentences = sent_tokenize(text)
    words = regexp_tokenize(text, r"[0-9A-z']+")
    # print("Debug: Tokenized words:", words)  # Debug
    characters = sum(1 for char in text if char not in [' ', '\n', '\t'])

    num_sentences = len(sentences)
    num_words = len(words)

    if num_words == 0 or num_sentences == 0:
        return None

    syllables = count_syllables(words)
    difficult_words = count_difficult_words(words, easy_words)

    return [characters, num_sentences, num_words, syllables, difficult_words]

def main():
    # Get the filename from command line
    if len(sys.argv) < 2:
        print("Usage: python3 readability.py <filename> <easy_words_file>")
        return

    filename = sys.argv[1]
    easy_words_file = sys.argv[2]

    try:
        with open(filename, 'r', encoding='utf-8') as file1:
            text = file1.read()
        with open(easy_words_file, 'r', encoding='utf-8') as file2:
            easy_words = file2.read().split('\n')

        # Tokenize into sentences, words, characters
        tokens = get_tokens(text, easy_words)
        if tokens is None:
            print("Text must contain at least one word and one sentence.")
            return

        # Compute and get ARI score
        ari_score = get_ari(tokens)
        fk_score = get_fk(tokens)
        dc_score = get_dc(tokens)

        # Average age calculation
        def parse_age_range(age_str):
            return sum(map(int, age_str.split('-'))) / 2
        average_age = sum(map(parse_age_range, [ari_score[1], fk_score[1], dc_score[1]])) / 3

        # Output results
        print_output(text, tokens, ari_score, fk_score, dc_score, average_age)

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")

if __name__ == "__main__":
    main()