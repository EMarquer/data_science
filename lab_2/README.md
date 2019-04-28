# Data science exam, lab session 2
Descriptive Statistics and visualization.

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

The Lab session is split in three exercises around the processing of text data, descriptive statisics and visualization database.

The code of exercise 1 is separate form the code of exercise 2 and 3 (see [Files](#files)).

### Exercise 1
The first exercise correspond to the processing of the text files from the previous lab session.

The exercise consist on loading the sentences and removing the punctuation as a preliminary step.
Then, Scipy is used to get the tokens, their POS and the named entities, and to run Stanford syntactic parser to get the parse tree.

The sentences and the additional data are stored in JSON files named after the Gutenberg identifier of the book they come from.

### Exercise 2
The second exercise correspond to the computation of statistics on the processed data.

The statistics computed are:
- the vocabulary size per author;
- the POS distribution per author;
- the mean, max and average number of tokens, NP and VP per author;
- the most frequent named entity of each type per author.

The generated statistics are not stored but printed.

### Exercise 3
The third exercise correspond to generating visualizations.

The visualizations generated are:
- a bar plot for the vocabulary size per author;
- a box plot for the sentence size per author;
- a bar plot for the POS distribution per author;
- a word cloud based on the vocabulary per author, based on the vocabulary of the author.

The bar plots and box plot are stored each in a file named after what they represent.
The word clouds are stored in numbered files, with the author name written at the image.

## Setup
To use the project, you will need a valid `Python 3.7.1` installation as well as the external libraries described in [External dependencies](#external-dependencies) (check that you have the correct versions!) and a working Stanford syntactic parser (see [Stanford Parser or Stanford CoreNLP](#stanford-parser-or-stanford-corenlp)). You will also need to download the correct Spacy language model (see [Spacy models and available languages](#spacy-models-and-available-languages)).

### Built-in Python dependencies
The project relies on the following `Python 3.7.1` built-in libraries:
| Library       |
|---------------|
| json          |
| string        |
| os            |
| re            |
| collections   |
| pprint        |

### External dependencies
The project uses the following python libraries:
| Library       | Version   |
|---------------|-----------|
| nltk          | 3.4.1     |
| wordcloud     | 1.5.0     |
| matplotlib    | 3.0.3     |
| seaborn       | 0.8       |

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

### Stanford Parser or Stanford CoreNLP
The project require a working Stanford Parser or Stanford CoreNLP.

#### If you already have Stanford Parser or Stanford CoreNLP
If you already have one, change the following constants in `exercise_1.py`:
- `PATH_TO_STANFORD`: the path to your Stanford Parser or Stanford CoreNLP folder;
- `PATH_TO_JAR`: the path to the main Stanford Parser or Stanford CoreNLP class;
- `PATH_TO_MODELS_JAR`:  the path to the Stanford Parser or Stanford CoreNLP models;
- `CORENLP_MODE`: `True` if your installation is of CoreNLP, `False` if it is of Stanford Parser.

#### If you don't have Stanford Parser or Stanford CoreNLP
You will need to install Java8 if you do not have it, and download the latest [Stanford Parser](https://nlp.stanford.edu/software/lex-parser.html#Download).

Once you have `stanford-parser-full-<version>.zip`, unzip it in this folder (`lab_2`), and update the constants in `exercise_1.py`:
- `PATH_TO_STANFORD`: the path to your Stanford Parser folder;
- `PATH_TO_JAR`: the path to the main Stanford Parser class;
- `PATH_TO_MODELS_JAR`:  the path to the Stanford Parser models;

## Usage 
To use the project, you will need the three exercise files from the `lab_2` folder in [repository](https://github.com/EMarquer/data_science), as well as the exercises and data from `lab_1`.

Each of those files is runable using `python exercise_#.py` (where `#` is the number of the exercise you want to execute).

Also, you can addapt the effects of the project by changing the value of some of the constants listed in [Constants](#constants).

To run the whole project, you need to run `exercise_1.py` then `exercise_2_3.py`.

### Constants
The constants are stored at the begining of each exercise file. You can change the value of all the constants listed below to adapt the program.
Note that the constants from an exercise may be used in a later exercise.

| Constant | Exercise file | Effect |
|-|-|-|
|VERBOSE| `exercise_1.py` | If `True`, will make the program describe what is going on during execution. |
|VERBOSE| `exercise_2_3.py` | If `True`, will make the program describe what is going on during execution. |
|LANGUAGE| `exercise_1.py` | Language of the parser. Must be a language present in the table in [Spacy models and available languages](#spacy-models-and-available-languages). |
|SAVE_PATH| `exercise_1.py` | Name of the folder in which the JSON  files will be stored |
|CSV_FILE_PATH| `exercise_1.py` | Name of the CSV catalogue file. |
|CSV_HEADERS| `exercise_1.py` | Name of the columns in the CSV file. |
|SPARQ_AUTHOR_NAME| `exercise_2.py` | SPARQL query to get an author URI from their name. |
|SPARQ_MOVEMENTS| `exercise_2.py` | SPARQL query to get all literary movements (`dbc:Literary_movements`) from an URI. |
|SPARQ_ABSTRACTS| `exercise_2.py` | SPARQL query to get all abstracts from an URI. |
|DB_PATH| `exercise_3.py` | Name of the SQL database file. |

## Files
Here is a list of files and a brief description for each of them:
- `data\*.<feature>.json`: `*` being the Gutenberg identifier of a book, `<feature>` being a feature computed in exercise 1, the file containg the feature for the senences from the book;
- `imgs\*.png`: the visualizations produced in exercise 3;
- `data\book_catalogue.csv`: CSV catalogue of books used, containing:
    - the name of the author of the book in Gutenberg;
    - the title;
    - the URI/ebook ID in Gutenberg;
    - the path to the file where the extracted sentences are stored;
- `data\book_catalogue.db`: SQL database containing information about the books and the authors (see [sql_graph.png](sql_graph.png) for the structure of the database);
- `exercise_1.py`: file containing the functions used to solve the exercise 1
- `exercise_2_3.py`: file containing the functions used to solve the exercise 2 and 3
- `README.md`: this file, containing various informations about the project and its files;
- `sql_graph.png`: the structure of the database.