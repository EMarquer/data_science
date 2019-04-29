# --- imports ---
from urllib.request import urlopen, HTTPError
from bs4 import BeautifulSoup
import re

# sentence parsing
import spacy

from random import sample, choices, seed
seed(1)

from collections import Counter
from pprint import pprint

import os

import pandas as pd

VERBOSE = False

# --- constants ---
# program default parameters
AUTHOR_NUMBER = 5  # k
SENTENCE_PER_AUTHOR = 200  # n

# book selection criterion
LANGUAGE_ROLE_REGEX = re.compile(r'\((\w+)\) \(as (\w+)\)')
# - indivdual role in the book
ROLES = {'Illustrator', 'Editor', 'Compiler', 'Translator', 'Contributer', 'Dubious author', 'Author'}
ROLE = 'Author'
assert ROLE in ROLES
# - language
SCIPY_LANGUAGES = {
    'German': 'de',
    'Greek': 'el',
    'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'Italian': 'it',
    'Dutch': 'nl',
    'Portuguese': 'pt'}
LANGUAGE = 'English'
assert LANGUAGE in SCIPY_LANGUAGES.keys()

# minimum number of books per author
BOOK_THRESHOLD = 4

# url for letter search
GUTEMBERG_LETTER_URL = 'http://www.gutenberg.org/browse/authors/{}'

# url for book download
GUTEMBERG_LETTER_UTF = "http://www.gutenberg.org{}.txt.utf-8"

LETTERS = 'abcdefghijklmnopqrstuvwxyz'

# data save directory
SAVE_PATH = 'data'
if not os.path.isdir(SAVE_PATH):
    os.mkdir(SAVE_PATH)
    
# CSV book/bookfile name/author matchup file
CSV_FILE_PATH = os.path.join(SAVE_PATH, 'book_catalogue.csv')
CSV_HEADERS = ['author', 'book_url', 'book_title', 'book_file']

# scipy parser singleton
PARSERS = dict()
def get_parser(language=LANGUAGE):
    # load the sentence parser for the target language
    if language not in PARSERS.keys():
        PARSERS[language] = spacy.load(SCIPY_LANGUAGES[language])
    return PARSERS[language]

# --- code ---
def get_book(book_link, base_url=GUTEMBERG_LETTER_UTF, verbose=VERBOSE):
    url = base_url.format(book_link)
    
    if verbose: print("Downloading book {} from {}".format(book_link, url))
    
    # fetching file content
    text = urlopen(url).read()
    return text

def parse_page(soup: BeautifulSoup, language, role, base_book_url=GUTEMBERG_LETTER_UTF, verbose=VERBOSE):
    """
    This method contains exclusion process for books unopenable using the standard opeing method:
    - if the book's utf-8 file is not available at expected address;
    - if the book's utf-8 file is not correctly utf-8 encoded.
    
    
    """
    content_div = soup.find('div', class_='pgdbbyauthor')
    if not content_div: # if the main div is not found, return empy list of books
        yield None, []
    
    else:
        authors_lists = content_div.find_all(["ul", "h2"])
        
        for elem in authors_lists:
            if elem.name == 'h2':
                # get the first a tag with name attribute as the author name if there is at least one
                name_list = [a_tag.get_text() for a_tag in elem.find_all('a') if a_tag.has_attr('name')]
                author_name = None if len(name_list) < 1 else name_list[0]
                
            elif elem.name == 'ul' and author_name:
                book_li_list = elem.find_all('li', class_="pgdbetext")
                books = dict()
                for book_li in book_li_list:
                    # we try to extract the language and role for the book
                    match = LANGUAGE_ROLE_REGEX.search(book_li.get_text())
                    
                    if match:
                        book_language, book_role = match.group(1, 2)

                        if book_language.lower() == language.lower() and book_role.lower() == role.lower():
                            try: # try to open and decode the book, if it fails we ignore the book
                                book_title = book_li.find('a').get_text()
                                book_link = book_li.find('a')['href']
                                
                                get_book(book_link, base_url=base_book_url, verbose=verbose).decode('utf-8')
                                
                                # add the book to the list of books
                                books[book_title] = book_link
                                
                            except (UnicodeDecodeError, HTTPError):
                                if verbose: print("Book {} is either badly encoded or unavailable at this address, skipping it".format(book_link))
                                pass
                
                yield author_name, books
                
                # clean the memory to avoid getting multiple ul per author
                author_name = None

def get_authors_books(letter,
                      book_anti_diplicate_set=set(),
                      language=LANGUAGE,
                      role=ROLE,
                      book_threshold=BOOK_THRESHOLD,
                      author_number=AUTHOR_NUMBER,
                      base_letter_url=GUTEMBERG_LETTER_URL,
                      base_book_url=GUTEMBERG_LETTER_UTF,
                      verbose=VERBOSE):
    url = base_letter_url.format(letter.lower())
    
    # get page
    html = urlopen(url)
    soup = BeautifulSoup(html)
    
    # extract autors and books from list
    author_dict = dict()
    for author_name, books in parse_page(soup, language, role, base_book_url=base_book_url, verbose=verbose):
        books = {book_link: book_title for book_link, book_title in books.items()
                 if book_link not in book_anti_diplicate_set} # remove books already selected
        if len(books) >= book_threshold:
            # add author and books to the list if there is enough books
            author_dict[author_name] = books
            book_anti_diplicate_set |= books.keys()
            
            if verbose: print(author_name, books)
            
        # if we have reached the number of authors we want, break the loop
        if len(author_dict) >= author_number: break
            
    return author_dict, book_anti_diplicate_set

# pick sentences from a book
def get_book_sents(book_link, sentence_number, language=LANGUAGE, base_url=GUTEMBERG_LETTER_UTF, verbose=VERBOSE):
    # get the content of the book
    book_text = get_book(book_link, base_url, verbose=verbose).decode('utf-8')
    book_text = book_text.split("***",2)[-1].strip() # removing gutenberg header
    
    # sentence tokenize using spacy
    book_text = book_text[:500000]  # taking only a sample of the book as spacy puts a limit on the number of characters
    if verbose: print("Parsing book {} with spacy".format(book_link))
    parsed_text = get_parser(language)(book_text)
    sentences = [sent.text for sent in parsed_text.sents]
    
    # random sampling of sentences
    chosen_sentences = sample(sentences, k=sentence_number)
    
    # removing extra spacing characters from selected lines
    chosen_sentences = [re.sub(r'\s+', ' ', sent).strip() for sent in chosen_sentences]
    return chosen_sentences

def get_sentence_per_book(books, sentence_number=SENTENCE_PER_AUTHOR, strategy='random', verbose=VERBOSE):  #decide number of lines per book
    if strategy=='random':
        sentence_per_book_counter = Counter(choices(list(books.values()), k=sentence_number))
        
    elif strategy=='balanced':
        # select the number of sentences to pick from each book, equally divided accorss the books
        sentence_per_book_counter = Counter()
        while sum(sentence_per_book_counter.values()) < sentence_number:
            for book_url in books.values():
                sentence_per_book_counter[book_url] += 1
                if sum(sentence_per_book_counter.values()) >= sentence_number:
                    break
                
    if verbose:
        print("Sentence repartition:")
        pprint(sentence_per_book_counter)
        
    return sentence_per_book_counter

def get_sentences(author_dict,
                  sentence_number=SENTENCE_PER_AUTHOR,
                  language=LANGUAGE,
                  base_book_url=GUTEMBERG_LETTER_UTF,
                  verbose=VERBOSE):
    sentence_dict = dict()
    for author, books in author_dict.items():
        # select the number of sentences to pick from each book of the author
        line_per_book_counter = get_sentence_per_book(books, sentence_number, verbose=verbose)
        
        # load the sentences from each book
        sentence_dict[author] = dict()
        for book_url, book_sentence_number in line_per_book_counter.items():
            sentences = get_book_sents(book_url,
                                       book_sentence_number,
                                       base_url=base_book_url,
                                       language=language,
                                       verbose=verbose)
            sentence_dict[author][book_url] = sentences
            if verbose: 
                print("Sentences from {}:".format(book_url))
                pprint(sentences)
    
    return sentence_dict

def author_per_letter(author_number=AUTHOR_NUMBER, letters=LETTERS):
    """Return a Counter object over randomly chosen letters among 'letters'.
    The total of the elements in the counter is equal to 'author_number'.
    
    :param author_number: number of elements to choose accross the letters (int)
    :param letters: sequence of elements to choose from (itterable)
    
    :return: a counter where keys are letters and values add up to author_number (Counter)"""
    return Counter(choices(letters, k=author_number))

def get_file_name(book_url, path=SAVE_PATH):
    return os.path.join(path, book_url.split('/')[-1] + ".txt")

def save(sentence_dict,
         author_dict,
         book_path=SAVE_PATH,
         csv_path=CSV_FILE_PATH,
         csv_headers=CSV_HEADERS,
         verbose=VERBOSE):
    book_to_path = dict()
    for author_sentence_dict in sentence_dict.values():
        for book_url, book_sentences in author_sentence_dict.items():
            file_name = get_file_name(book_url, path=book_path)

            with open(file_name, 'w') as f:
                f.write("\n".join(book_sentences))

                # stores the path to the file
                book_to_path[book_url] = file_name
                if verbose: print("{} line(s) from book '{}' written to '{}'".format(len(book_sentences), book_url, file_name))
    
    # save the information about books from which sentences were chosen (their URL, their title, and the file where the sentences were saved)
    csv_data = [[author_name, book_url, book_title, book_to_path[book_url]]
                for author_name, books in author_dict.items()
                for book_title, book_url in books.items()
                if book_url in book_to_path.keys()]
    
    # write the data to CSV
    df = pd.DataFrame(csv_data, columns=csv_headers)
    df.to_csv(CSV_FILE_PATH)
    if verbose: print("book catalogue written to {}".format(csv_path))

def exercice_1(author_number=AUTHOR_NUMBER,
               sentence_number=SENTENCE_PER_AUTHOR,
               language=LANGUAGE,
               role=ROLE,
               book_threshold=BOOK_THRESHOLD,
               base_letter_url=GUTEMBERG_LETTER_URL,
               base_book_url=GUTEMBERG_LETTER_UTF,
               letters=LETTERS,
               book_path=SAVE_PATH,
               csv_path=CSV_FILE_PATH,
               csv_headers=CSV_HEADERS,
               verbose=VERBOSE):
    book_anti_diplicate_set = set()
    author_dict = dict()
    
    # Step 1: selecting the k authors
    for letter, count in author_per_letter(author_number=author_number, letters=letters).items():
        if verbose: print("Picking {} author(s) from letter {}".format(count, letter))
            
        # generate a dictionnary of authors and their books
        author_dict_temp, book_anti_diplicate_set = get_authors_books(letter,
                                                                      book_anti_diplicate_set=book_anti_diplicate_set, 
                                                                      language=language,
                                                                      book_threshold=book_threshold,
                                                                      author_number=count,
                                                                      base_letter_url=base_letter_url,
                                                                      base_book_url=base_book_url,
                                                                      verbose=verbose)
        author_dict.update(author_dict_temp)
        
    # Step 2: getting n sentences per author
    sentence_dict = get_sentences(author_dict,
                                  sentence_number=sentence_number,
                                  language=language,
                                  base_book_url=base_book_url,
                                  verbose=verbose)
    
    # Step 3: storing the sentences, 1 file per book, adn 1 file to link the books to their main author
    save(sentence_dict,
         author_dict,
         book_path=book_path,
         csv_path=csv_path,
         csv_headers=csv_headers,
         verbose=verbose)
    return author_dict, sentence_dict
        
# --- main ---
if __name__ == "__main__":
    print(exercice_1())