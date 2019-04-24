# Data science exam, lab session 1
Extracting and storing text and RDF data.

This README can be found at [https://github.com/EMarquer/data_science](https://github.com/EMarquer/data_science).

## In this README
- [In this README](#in-this-readme)
- [Description](#description)
- [Setup](#setup)
    - [Built-in Python dependencies](#built-in-python-dependencies)
    - [External dependencies](#external-dependencies)
        - [Spacy models and available languages](#spacy-models-and-available-languages)
- [Usage](#usage)
    - [Description of the effect of each exercise file](#description-of-the-effect-of-each-exercise-file)
    - [Constants](#constants)
- [Files](#files)

## Description
This project was done for the UE803: Data Science of the NLP Master Program of Nancy.
It corresponds to the second of three lab sessions of the evaluation of the UE.

// structure of the lab

The code of each exercise is stored in a different file (see [Files](#files)).

### Exercise 1
The first exercise correspond to // topic of the exercise

// What the exercise does

// Output

## Setup
To use the project, you will need a valid `Python 3.7.1` installation as well as the external libraries described in [External dependencies](#external-dependencies) (check that you have the correct versions!). You will also need to download the correct Spacy language model (see [Spacy models and available languages](#spacy-models-and-available-languages)).

### Built-in Python dependencies
The project relies on the following `Python 3.7.1` built-in libraries:
| Library       |
|---------------|
| re            |
| os            |
| random        |
| collections   |
| pprint        |

### External dependencies
The project uses the following python libraries:
| Library       | Version   |
|---------------|-----------|
| urllib3       | 1.24.1    |
| beautifulsoup4| 4.6.3     |
| spacy         | 2.0.12    |
| numpy         | 1.15.4    |
| pandas        | 0.23.4    |
| SPARQLWrapper | 1.8.2     |
| sqlalchemy    | 1.2.15    |

#### Spacy models and available languages
The `en` model is used by default for spacy.
You can get it by executing `python -m spacy download en` in your terminal.

If you wish to use a different language, you need to download the corresponding model by running `python -m spacy download <lang>` (where `<lang>` is the language key of the language you wish to use).

The available languages are:
|Language   |Language key|
|-----------|----|
|German     |`de`|
|Greek      |`el`|
|English    |`en`|
|Spanish    |`es`|
|French     |`fr`|
|Italian    |`it`|
|Dutch      |`nl`|
|Portuguese |`pt`|

## Usage 
To use the project, you will need the three exercise files from the [repository](https://github.com/EMarquer/data_science).

Each of those files is runable using `python exercise_#.py` (where `#` is the number of the exercise you want to execute).

Also, you can addapt the effects of the project by changing the value of some of the constants listed in [Constants](#constants).

To run the whole project, you need to run `exercise_1.py` then `exercise_3.py`. `exercise_2.py` just provides tools for `exercise_3.py`.

### Description of the effect of each exercise file
#### `exercise_1.py`
This program searches the [Gutenberg project](http://www.gutenberg.org/) for `k` authors and `n` sentences per authors.

The selected sentences are stored in TXT files named after the Gutenberg identifier of the book they come from, one sentence per line (ex: [data/748.txt](data/748.txt)).

An extra CSV file ([data/book_catalogue.csv](data/book_catalogue.csv)) contains the catalogue of books used (title and URI/ebook ID), the file where the extracted sentences are stored and the name of the author of the book.

Notes:
- the program is executed by default with verbose, whatever the value of VERBOSE is;
- internet connection is required for the program to work.

**Warning**:
- running this program will overwrite the previously extracted corpus.

#### `exercise_2.py`
This program searches [DBpedia](https://wiki.bdpedia.org/) for abstracts and literary movement.

Running it just serves to demonstrate that the provided functions work on a predefined example.

#### `exercise_3.py`
This program creates a database from the book catalogue ([data/book_catalogue.csv](data/book_catalogue.csv)) and additional information extracted using `exercise_2.py`.

It produces a SQL database ([data/book_catalogue.db](data/book_catalogue.db)) and tests a set of example requests on this database.

**Warning**:
- running this program will overwrite the previously built database.

### Constants
The constants are stored at the begining of each exercise file. You can change the value of all the constants listed below to adapt the program.
Note that the constants from an exercise may be used in a later exercise.

| Constant | Exercise file | Effect |
|-|-|-|
|VERBOSE| `exercise_1.py` | If `True`, will make the program describe what is going on during execution. |
|VERBOSE| `exercise_2.py` | If `True`, will make the program describe what is going on during execution. |
|VERBOSE| `exercise_3.py` | If `True`, will make the program describe what is going on during execution. |
|AUTHOR_NUMBER| `exercise_1.py` | Noted `k` in the instruction sheet. The number of authors to extract from the [Gutenberg project](http://www.gutenberg.org/). |
|SENTENCE_PER_AUTHOR| `exercise_1.py` | Noted `n` in the instruction sheet. The number of sentence to extract per author. |
|ROLE| `exercise_1.py` | Role of the individual in the book (author, translator, ...). |
|LANGUAGE| `exercise_1.py` | Language of the book. Must be a language present in the table in [Spacy models and available languages](#spacy-models-and-available-languages). |
|BOOK_THRESHOLD| `exercise_1.py` | Minimal number of valid books to accept an author. |
|SAVE_PATH| `exercise_1.py` | Name of the folder in which the TXT and CSV files will be stored |
|CSV_FILE_PATH| `exercise_1.py` | Name of the CSV catalogue file. |
|CSV_HEADERS| `exercise_1.py` | Name of the columns in the CSV file. |
|SPARQ_AUTHOR_NAME| `exercise_2.py` | SPARQL query to get an author URI from their name. |
|SPARQ_MOVEMENTS| `exercise_2.py` | SPARQL query to get all literary movements (`dbc:Literary_movements`) from an URI. |
|SPARQ_ABSTRACTS| `exercise_2.py` | SPARQL query to get all abstracts from an URI. |
|DB_PATH| `exercise_3.py` | Name of the SQL database file. |

## Files
Here is a list of files and a brief description for each of them:
- `data\*.txt`: `*` being the Gutenberg identifier of a book, file containg the sentences from the book;
- `data\book_catalogue.csv`: CSV catalogue of books used, containing:
    - the name of the author of the book in Gutenberg;
    - the title;
    - the URI/ebook ID in Gutenberg;
    - the path to the file where the extracted sentences are stored;
- `data\book_catalogue.db`: SQL database containing information about the books and the authors (see [sql_graph.png](sql_graph.png) for the structure of the database);
- `exercise_1.py`: file containing the functions used to solve the exercise 1
- `exercise_2.py`: file containing the functions used to solve the exercise 2
- `exercise_3.py`: file containing the functions used to solve the exercise 3
- `README.md`: this file, containing various informations about the project and its files;
- `sql_graph.png`: the structure of the database.