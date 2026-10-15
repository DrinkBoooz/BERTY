import sys
import csv
import os

""" 
    CONSTANTS 
"""
VOWELS = "aeiouAEIOU"
CONSONANTS = "bcdfghklmnngpqrstvwyBCDFGHKLMNNGPQRSTVWY"

# Global dictionary for validation
TAGALOG_DICTIONARY = set()

def load_dictionary(dict_file='tgl_wordlist.txt'):
    """
    Load the Tagalog dictionary from a text file
    """
    global TAGALOG_DICTIONARY
    try:
        with open(dict_file, 'r', encoding='utf-8') as file:
            for line in file:
                word = line.strip()
                if word:  # Skip empty lines
                    TAGALOG_DICTIONARY.add(word.lower())
        print(f"Loaded {len(TAGALOG_DICTIONARY)} words from dictionary")
        return True
    except FileNotFoundError:
        print(f"Warning: Dictionary file '{dict_file}' not found. Stemming will proceed without validation.")
        return False
    except Exception as e:
        print(f"Error loading dictionary: {str(e)}")
        return False

"""  
    Affixes 
""" 
PREFIX_SET = [ 
    'di-', 'ipapa', 'ipinagka', 'ipinagkaka', 'kasing',
    'maii', 'maka', 'makaka', 'makakapag', 'makapa',
    'maki', 'makikipag', 'makikipagka', 'mala', 'mam',
    'mina', 'nai', 'naii', 'nakaka', 'nakakapag',
    'nakapa', 'nakikipag', 'nakikipagka', 'nam', 'nan',
    'napa', 'napapa', 'napag', 'paka', 'pakaka',
    'paki', 'pakipag', 'pakipagka', 'pakikipagka',
    'pama', 'pamama', 'pana', 'panana',
    'sa', 'sam', 'san', 'sang', 'sin', 'sim',
    'nakikipag', 'pakikipag', 
    'pinakama', 'pagpapa', 
    'pinagka', 'panganga',  
    'makapag', 'nakapag',  
    'tagapag', 'makipag',  
    'nakipag', 'tigapag', 
    'pakiki', 'magpa', 
    'napaka', 'pinaka', 
    'ipinag', 'pagka',  
    'pinag', 'mapag',  
    'mapa', 'taga',  
    'ipag', 'tiga',  
    'pala', 'pina',  
    'pang', 'naka', 
    'nang', 'mang', 
    'sing', 
    'ipa', 'pam', 
    'pan', 'pag', 
    'tag', 'mai', 
    'mag', 'nam', 
    'nag', 'man', 
    'may', 'ma', 
    'na', 'ni', 
    'pa', 'ka', 
    'um', 'in', 
    'i', 
] 

INFIX_SET = [ 
    'um', 'in', 
] 

SUFFIX_SET = [ 
    'anan', 'anin', 'ito', 'nan', 'nin', 'siyon',
    "'t", "'y",
    'syon','dor',  
    'ita', 'han',  
    'hin', 'ing',  
    'ang', 'ng',  
    'an', 'in',  
    'g', 
]

# Common Tagalog function words and basic vocabulary to help identify Tagalog text
TAGALOG_MARKERS = [
    'ang', 'ng', 'sa', 'at', 'ay', 'mga', 'ko', 'mo', 'niya', 'namin', 'ninyo', 'nila',
    'akin', 'iyo', 'kanya', 'amin', 'inyo', 'kanila', 'ito', 'iyan', 'iyon',
    'dito', 'diyan', 'doon', 'nito', 'niyan', 'noon', 'na', 'pa', 'pala',
    'po', 'ho', 'ba', 'nga', 'lamang', 'lang', 'naman', 'kasi', 'tuloy',
    'sana', 'raw', 'daw', 'din', 'rin', 'muna', 'pang'
]

# Common Tagalog letter combinations that are rare in English
TAGALOG_PATTERNS = ['ng', 'ay', 'kk', 'kl', 'gs', 'gk', 'bh', 'rs', 'll', 'ps', 'ts']

def is_tagalog_word(word):
    """
    Determines if a word is likely Tagalog based on affixes, common words, and letter patterns.
    returns a BOOLEAN value
    """
    # Skip checking very short words or words with numbers
    if len(word) <= 2 or any(c.isdigit() for c in word):
        return False
        
    word_lower = word.lower()
    
    # First check if word is in our dictionary
    if word_lower in TAGALOG_DICTIONARY:
        return True
    
    # Check if the word is in our list of common Tagalog words
    if word_lower in TAGALOG_MARKERS:
        return True
    
    # Check for common Tagalog letter patterns
    for pattern in TAGALOG_PATTERNS:
        if pattern in word_lower:
            return True
    
    # Check for common Tagalog prefixes
    for prefix in PREFIX_SET:
        if word_lower.startswith(prefix) and len(word_lower) > len(prefix) + 2:
            return True
    
    # Check for common Tagalog suffixes
    for suffix in SUFFIX_SET:
        if word_lower.endswith(suffix) and len(word_lower) > len(suffix) + 2:
            return True
    
    # Check for infixes
    for infix in INFIX_SET:
        if infix in word_lower[1:-1] and len(word_lower) > len(infix) + 3:
            return True
    
    # Check for repeated syllables which are common in Tagalog
    if '-' in word_lower and len(word_lower.split('-')) == 2:
        parts = word_lower.split('-')
        if parts[0] == parts[1]:
            return True
    
    # Custom Tagalog characteristics
    if word_lower[-1] in VOWELS and len(word_lower) >= 4:
        return True
        
    return False

def stem_word(token, reset_flags=True):
    """
    variables
    Stems a single Tagalog word.
    token: the word to be stemmed
    reset_flags: whether to reset period and pass flags
    returns STRING of the stemmed word
    """
    # Global flags for processing state
    global PERIOD_FLAG
    global PASS_FLAG
    
    # Initialize these globals if they don't exist
    if 'PERIOD_FLAG' not in globals():
        PERIOD_FLAG = True
    if 'PASS_FLAG' not in globals():
        PASS_FLAG = False

    # Skip empty strings or very short tokens that can't be meaningfully stemmed
    if not token or len(token) < 2:
        return token
        
    # Preserve punctuation at the beginning/end of token
    prefix_punct = ""
    suffix_punct = ""
    
    while token and not (token[0].isalpha() or token[0].isdigit()):
        prefix_punct += token[0]
        token = token[1:]
    
    while token and not (token[-1].isalpha() or token[-1].isdigit()):
        suffix_punct = token[-1] + suffix_punct
        token = token[:-1]
    
    # Skip if no meaningful text left
    if not token:
        return prefix_punct + suffix_punct
        
    # Check if this is a Tagalog word - if not, return the original token
    clean_token = token.strip(".,!?;:'\"()[]{}")
    if not is_tagalog_word(clean_token):
        return prefix_punct + token + suffix_punct

    # Initialize empty arrays for each stemming operation
    PREFIX = []
    INFIX = []
    SUFFIX = []
    DUPLICATE = []
    REPITITION = []
    CLEANERS = []

    original_case = token[0].isupper()
    
    # Process based on capitalization and period flags
    if (PERIOD_FLAG and original_case) or (not PERIOD_FLAG and not original_case):
        token = token.lower()        
        
        # Apply stemming operations in sequence
        du1_stem = clean_duplication(token, DUPLICATE)
        pre_stem = clean_prefix(du1_stem, PREFIX)
        rep_stem = clean_repitition(pre_stem, REPITITION)
        inf_stem = clean_infix(rep_stem, INFIX)
        rep_stem = clean_repitition(inf_stem, REPITITION)
        suf_stem = clean_suffix(rep_stem, SUFFIX)
        du2_stem = clean_duplication(suf_stem, DUPLICATE)
        cle_stem = clean_stemmed(du2_stem, CLEANERS, REPITITION)
        cle_stem = clean_duplication(cle_stem, DUPLICATE)

        if '-' in cle_stem:
            cle_stem = cle_stem.replace('-', '')

        # Verify if the stem is valid using dictionary
        if check_validation(cle_stem):
            stemmed = cle_stem
        else:
            # Try second pass if validation fails
            PASS_FLAG = True
            du1_stem = clean_duplication(cle_stem, DUPLICATE)
            pre_stem = clean_prefix(du1_stem, PREFIX)
            rep_stem = clean_repitition(pre_stem, REPITITION)
            inf_stem = clean_infix(rep_stem, INFIX)
            rep_stem = clean_repitition(inf_stem, REPITITION)
            suf_stem = clean_suffix(rep_stem, SUFFIX)
            du2_stem = clean_duplication(suf_stem, DUPLICATE)
            cle_stem = clean_stemmed(du2_stem, CLEANERS, REPITITION)
            cle_stem = clean_duplication(cle_stem, DUPLICATE)
            PASS_FLAG = False
            
            stemmed = cle_stem
    else:
        # If token doesn't match capitalization pattern, just clean it
        stemmed = clean_stemmed(token.lower(), CLEANERS, REPITITION)
    
    # Reset flags if requested
    if reset_flags:
        PERIOD_FLAG = False
    
    # Check for period at end of token to set flag for next token
    if token.endswith('.') and not PASS_FLAG:
        PERIOD_FLAG = True
    
    # Check if the stemmed word is in dictionary
    if stemmed and stemmed.lower() in TAGALOG_DICTIONARY:
        # Great! We have a valid stem
        pass
    elif token.lower() in TAGALOG_DICTIONARY:
        # If stemming leads to an invalid word but original was valid, use original
        stemmed = token.lower()
        
    # Restore original capitalization
    if original_case and stemmed:
        stemmed = stemmed[0].upper() + stemmed[1:]
        
    # Return stemmed word with preserved punctuation
    return prefix_punct + stemmed + suffix_punct

def process_csv(input_file, text_column, output_file=None, detailed_info=False, dict_file='tgl_wordlist.txt'):
    """
    Process a CSV file, stemming words in the specified column.
    input_file: path to input CSV file
    text_column: the column name containing text to stem
    output_file: path to output CSV file (defaults to <input_file_name>_stemmed.csv)
    detailed_info: whether to include detailed stemming information
    dict_file: path to the Tagalog dictionary file
    """
    if not output_file:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_stemmed{ext}"
    
    print(f"Processing CSV file: {input_file}")
    print(f"Reading text from column: {text_column}")
    print(f"Output will be written to: {output_file}")
    
    # Load the dictionary
    dict_loaded = load_dictionary(dict_file)
    if not dict_loaded:
        print("Warning: Proceeding without dictionary validation. Results may be less accurate.")
    
    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Read the input CSV file
        with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Check if the specified column exists
            if text_column not in reader.fieldnames:
                print(f"Error: Column '{text_column}' not found in the CSV file.")
                print(f"Available columns: {reader.fieldnames}")
                return
            
            # Prepare the output file with additional columns
            fieldnames = reader.fieldnames.copy()
            if 'processed_text' not in fieldnames:
                fieldnames.append('processed_text')
            
            # Process each row
            rows = []
            processed_count = 0
            
            for row in reader:
                text = row[text_column]
                
                # Preserve original text
                original_text = text
                
                # Process each token in the text
                processed_tokens = []
                
                # Reset flags at the beginning of each sentence
                global PERIOD_FLAG
                PERIOD_FLAG = True
                
                # Split by spaces while preserving punctuation
                import re
                tokens = re.findall(r'\S+|\s+', text)
                
                for token in tokens:
                    # Skip pure whitespace
                    if token.isspace():
                        processed_tokens.append(token)
                        continue
                        
                    # Process non-whitespace tokens
                    stemmed = stem_word(token)
                    processed_tokens.append(stemmed)
                
                # Join the processed tokens back into text
                processed_text = ''.join(processed_tokens)
                
                # Add the processed text to the row
                new_row = row.copy()
                new_row['processed_text'] = processed_text
                rows.append(new_row)
                
                processed_count += 1
                if processed_count % 100 == 0:
                    print(f"Processed {processed_count} rows...")
        
        # Write the processed data to the output file
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"Processing complete. Stemmed text written to {output_file}")
        print(f"Processed {len(rows)} rows.")
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

def clean_duplication(token, DUPLICATE):
    """
    Checks token for duplication. (ex. araw-araw = araw)
    token: word to be stemmed duplication
    DUPLICATE: list to store detected duplications
    returns STRING
    """
    if not token or check_validation(token):
        return token

    if '-' in token and token.index('-') != 0 and \
        token.index('-') != len(token) -  1:

        split = token.split('-')

        if all(len(tok) >= 3 for tok in split):
            if split[0] == split[1] or \
               (split[0][-1] == 'u' and change_letter(split[0], -1, 'o') == split[1]) or \
               (split[0][-2] == 'u' and change_letter(split[0], -2, 'o') == split[1]):
                DUPLICATE.append(split[0])
                return split[0]

            elif split[0] == split[1][0:len(split[0])]:
                DUPLICATE.append(split[1])
                return split[1]

            elif split[0][-2:] == 'ng':
                if split[0][-3] == 'u':
                    if split[0][0:-3] + 'o' == split[1]:
                        DUPLICATE.append(split[1])
                        return split[1]

                if split[0][0:-2] == split[1]:
                    DUPLICATE.append(split[1])
                    return split[1]

        else:
            return '-'.join(split)
    
    return token


def clean_repitition(token, REPITITION):
    """
    Checks token for repitition. (ex. nakakabaliw = nabaliw)
    token: word to be stemmed repitition
    REPITITION: list to store detected repetitions
    returns STRING
    """
    if not token or check_validation(token):
        return token

    if len(token) >= 4:
        if check_vowel(token[0]):
            if token[0] == token[1]:
                REPITITION.append(token[0])
                return token[1:]

        elif check_consonant(token[0]) and count_vowel(token) >= 2:
            if token[0:2] == token[2:4] and len(token) - 2 >= 4:
                REPITITION.append(token[2:4])
                return token[2:]
            
            elif token[0:3] == token[3:6] and len(token) - 3 >= 4:
                REPITITION.append(token[3:6])
                return token[3:]

    return token


def clean_prefix(token, PREFIX):
    """
    Checks token for prefixes. (ex. naligo = ligo)
    token: word to be stemmed for prefixes
    PREFIX: list to store detected prefixes
    returns STRING
    """
    if not token or check_validation(token):
        return token

    for prefix in PREFIX_SET:
        if len(token) - len(prefix) >= 3 and \
           count_vowel(token[len(prefix):]) >= 2:

            if prefix == ('i') and check_consonant(token[2]):
                continue

            if '-' in token:    
                token_parts = token.split('-')

                if token_parts[0] == prefix and check_vowel(token_parts[1][0]):
                    PREFIX.append(prefix)
                    return token_parts[1]

                token = '-'.join(token_parts)

            if token[0:len(prefix)] == prefix:
                if count_vowel(token[len(prefix):]) >= 2:
                    if prefix == 'panganga':
                        PREFIX.append(prefix)
                        return 'ka' + token[len(prefix):]
                    
                    PREFIX.append(prefix)
                    return token[len(prefix):]

    return token

 
def clean_infix(token, INFIX):
    """
    Checks token for infixes. (ex. bumalik = balik)
    token: word to be stemmed for infixes
    INFIX: list to store detected infixes
    returns STRING
    """
    if not token or check_validation(token):
        return token

    for infix in INFIX_SET:
        if len(token) - len(infix) >= 3 and count_vowel(token[len(infix):]) >= 2:
            if len(token) >= 5 and token[0] == token[4] and token[1:4] == infix:
                INFIX.append(infix)
                return token[4:]

            elif len(token) >= 5 and token[2] == token[4] and token[1:3] == infix:
                INFIX.append(infix)
                return token[0] + token[3:]

            elif len(token) >= 4 and token[1:3] == infix and check_vowel(token[3]):
                INFIX.append(infix)
                return token[0] + token[3:]

    return token


def clean_suffix(token, SUFFIX):
    """
    Checks token for suffixes. (ex. bigayan = bigay)
    token: word to be stemmed for suffixes
    SUFFIX: list to store detected suffixes
    returns STRING
    """
    if not token or check_validation(token):
        return token

    SUF_CANDIDATE = []
    
    for suffix in SUFFIX_SET:
        if len(token) - len(suffix) >= 3 and count_vowel(token[0:len(token) - len(suffix)]) >= 2:
            if token[len(token) - len(suffix):] == suffix:
                if len(suffix) == 2 and not count_consonant(token[0:len(token) - len(suffix)]) >= 1:
                    continue

                if count_vowel(token[0:len(token) - len(suffix)]) >= 2:
                    if suffix == 'ang' and check_consonant(token[-4]) \
                        and token[-4] != 'r' and len(token) >= 5 and token[-5] != 'u':
                        continue

                    if check_validation(token[0:len(token) - len(suffix)]):
                        SUFFIX.append(suffix)
                        return token[0:len(token) - len(suffix)] + 'a' if suffix == 'ita' \
                            else token[0:len(token) - len(suffix)]

                    elif len(SUF_CANDIDATE) == 0:
                        SUF_CANDIDATE.append(suffix)
                        SUF_CANDIDATE.append(token[0:len(token) - len(suffix)])

    if len(SUF_CANDIDATE) == 2:
        suffix = SUF_CANDIDATE[0]
        SUFFIX.append(suffix)
        return SUF_CANDIDATE[1] + 'a' if suffix == 'ita' else SUF_CANDIDATE[1]

    return token


def check_vowel(substring):
    """
    Checks if the substring contains only vowels.
    substring: substring to be tested
    returns BOOLEAN
    """
    if not substring:
        return False
    return all(letter in VOWELS for letter in substring)


def check_consonant(substring):
    """
    Checks if the substring contains only consonants.
    substring: substring to be tested
    returns BOOLEAN
    """
    if not substring:
        return False
    return all(letter in CONSONANTS for letter in substring)


def count_vowel(token):
    """
    Count vowels in a given token.
    token: string to be counted for vowels
    returns INTEGER
    """
    if not token:
        return 0
        
    count = 0
    for tok in token:
        if tok in VOWELS:
            count += 1
    return count


def count_consonant(token):
    """
    Count consonants in a given token.
    token: string to be counted for consonants
    returns INTEGER
    """
    if not token:
        return 0
        
    count = 0
    for tok in token:
        if tok in CONSONANTS:
            count += 1
    return count


def change_letter(token, index, letter):
    """
    Replaces a letter in a token.
    token: word to be used
    index: index of the letter
    letter: letter used to replace
    returns STRING
    """
    if not token:
        return token
        
    _list = list(token)
    try:
        _list[index] = letter
        return ''.join(_list)
    except IndexError:
        return token


def clean_stemmed(token, CLEANERS, REPITITION):
    """
    Checks for left-over affixes and letters.
    token: word to be cleaned for excess affixes/letters
    returns STRING
    """
    global PERIOD_FLAG
    global PASS_FLAG
    
    if not token:
        return token

    CC_EXP = ['dr', 'gl', 'gr', 'ng', 'kr', 'kl', 'kw', 'ts', 'tr', 'pr', 'pl', 'pw', 'sw', 'sy'] # Consonant + Consonant Exceptions

    # Check for period and set flag
    if token.endswith('.') and not PASS_FLAG:
        PERIOD_FLAG = True
        token = token[:-1]  # Remove period for processing
        
    # Remove non-alphabetic characters at beginning/end
    while token and not (check_vowel(token[-1]) or check_consonant(token[-1])):
        CLEANERS.append(token[-1])
        token = token[:-1]

    while token and not (check_vowel(token[0]) or check_consonant(token[0])):
        CLEANERS.append(token[0])
        token = token[1:]

    if not token or check_validation(token):
        return token

    if len(token) >= 3 and count_vowel(token) >= 2:
        token = clean_repitition(token, REPITITION)

        if len(token) >= 2 and check_consonant(token[-1]) and token[-2] == 'u':
            CLEANERS.append('u')
            token = change_letter(token, -2, 'o')

        if len(token) >= 1 and token[-1] == 'u':
            CLEANERS.append('u')
            token = change_letter(token, -1, 'o')

        if len(token) >= 1 and token[-1] == 'r':
            CLEANERS.append('r')
            token = change_letter(token, -1, 'd')

        if len(token) >= 2 and token[-1] == 'h' and check_vowel(token[-2:]):
            CLEANERS.append('h')
            token = token[:-1]

        if len(token) >= 2 and token[0] == token[1]:
            CLEANERS.append(token[0])
            token = token[1:]

        if len(token) >= 3 and (token[0:2] == 'ka' or token[0:2] == 'pa') and \
           check_consonant(token[2]) and count_vowel(token) >= 3:
            CLEANERS.append(token[0:2])
            token = token[2:]

        if len(token) >= 3 and token[-3:] == 'han' and count_vowel(token[:-3]) == 1:
            CLEANERS.append('han')
            token = token[:-3] + 'i'

        if len(token) >= 3 and token[-3:] == 'han' and count_vowel(token[:-3]) > 1:
            CLEANERS.append('han')
            token = token[:-3]

        if len(token) >= 2 and count_vowel(token) >= 3:
            if token[-1] == 'h' and check_vowel(token[-2]):
                CLEANERS.append('h')
                token = token[:-1]

        if len(token) >= 6 and token[0:2] == token[2:4]:
            CLEANERS.append('0:2')
            token = token[2:]

        if REPITITION and any(REP[0] == 'r' for REP in REPITITION):
            CLEANERS.append('r')
            token = change_letter(token, 0, 'd')

        if len(token) >= 3 and token[-2:] == 'ng' and token[-3] == 'u':
            CLEANERS.append('u')
            token = change_letter(token, -3, 'o')

        if len(token) >= 1 and token[-1] == 'h':
            CLEANERS.append('h')
            token = token[:-1]

        if len(token) >= 2 and all(token[0:2] != CC for CC in CC_EXP) and check_consonant(token[0:2]):
            CLEANERS.append(token[0:2])
            token = token[1:]

    return token


def check_validation(token):
    """
    Checks if a token is in the validation list.
        token: word to be validated
    returns BOOLEAN
    """
    if not token:
        return False
        
    # First check our loaded dictionary
    if token.lower() in TAGALOG_DICTIONARY:
        return True
        
    # Fall back to validation.txt if available
    try:
        with open('validation.txt', 'r') as valid:
            data = valid.read().replace('\n', ' ').split(' ')
        return token in data
    except FileNotFoundError:
        return False


def main():
    """
    Main function to run via command-line or debugger
    """
    print("TAGALOG CSV STEMMER")
    print("===================")
    
    # Check if running as script with arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        text_column = sys.argv[2] if len(sys.argv) > 2 else "Text"
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
        detailed_info = len(sys.argv) > 4 and sys.argv[4].lower() == 'true'
        dict_file = sys.argv[5] if len(sys.argv) > 5 else 'tgl_wordlist.txt'
        
        process_csv(input_file, text_column, output_file, detailed_info, dict_file)
    else:
        # Interactive mode
        input_file = input("Enter CSV file path: ")
        text_column = input("Enter column name containing text (default: 'Text'): ") or "Text"
        output_file = input("Enter output file path (leave blank for auto-naming): ") or None
        detailed_info = input("Include detailed stemming info? (y/n): ").lower() == 'y'
        dict_file = input("Enter dictionary file path (default: 'tgl_wordlist.txt'): ") or 'tgl_wordlist.txt'
        
        # Create output directory if it doesn't exist
        if output_file and os.path.dirname(output_file):
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
        process_csv(input_file, text_column, output_file, detailed_info)


# Initialize global flags
PERIOD_FLAG = True
PASS_FLAG = False

if __name__ == "__main__":
    main()
