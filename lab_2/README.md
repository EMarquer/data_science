# Data science exam, lab session 2
Descriptive Statistics and visualization.

This README can be found at [https://github.com/EMarquer/data_science](https://github.com/EMarquer/data_science).

## In this README
- [In this README](#in-this-readme)
- [Description](#description)
    - [Exercise 1](#exercise-1)
    - [Exercise 2](#exercise-2)
    - [Exercise 3](#exercise-3)
- [Setup](#setup)
    - [Built-in Python dependencies](#built-in-python-dependencies)
    - [External dependencies](#external-dependencies)
        - [Spacy models and available languages](#spacy-models-and-available-languages)
    - [Stanford Parser or Stanford CoreNLP](#stanford-parser-or-stanford-corenlp)
        - [If you already have Stanford Parser or Stanford CoreNLP](#if-you-already-have-stanford-parser-or-stanford-corenlp)
        - [If you don't have Stanford Parser or Stanford CoreNLP](#if-you-don't-have-stanford-parser-or-stanford-corenlp)
- [Usage](#usage)
    - [Description of the effect of each exercise file](#description-of-the-effect-of-each-exercise-file)
        - [`exercise_1.py`](#exercise_1py)
        - [`exercise_2_3.py`](#exercise_2_3py)
    - [Constants](#constants)
- [Files](#files)

## Description
This project was done for the UE803: Data Science of the NLP Master Program of Nancy.
It corresponds to the second of three lab sessions of the evaluation of the UE.

The lab session is split in three exercises around the processing of text data, descriptive statisics and visualization.

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
To use the project, you will need a valid `Python 3.7.1` installation as well as the external libraries described in [External dependencies](#external-dependencies) (check that you have the correct versions!) and a working Stanford syntactic parser (see [Stanford Parser or Stanford CoreNLP](#stanford-parser-or-stanford-corenlp)). You will also need to download the correct Spacy language model (see [Spacy models and available languages](#spacy-models-and-available-languages)). Also, the files and scripts from `lab_1` are required.

### Built-in Python dependencies
The project relies on the following `Python 3.7.1` built-in libraries:
| Library       |
|---------------|
| json          |
| string        |
| os            |
| sys           |
| inspect       |
| re            |
| collections   |
| pprint        |

### External dependencies
The project uses the following python libraries:
| Library       | Version   |
|---------------|-----------|
| numpy         | 1.15.4    |
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
If you already have one, change the following constants in `exercise_1.py` (see [Constants](#constants) for the line number):
- `PATH_TO_STANFORD`: the path to your Stanford Parser or Stanford CoreNLP folder, relative to this folder (`lab_2`) or absolute;
- `PATH_TO_JAR`: the path to the main Stanford Parser or Stanford CoreNLP class, relative to this folder (`lab_2`) or absolute;
- `PATH_TO_MODELS_JAR`:  the path to the Stanford Parser or Stanford CoreNLP models, relative to this folder (`lab_2`) or absolute;
- `CORENLP_MODE`: `True` if your installation is of CoreNLP, `False` if it is of Stanford Parser.

#### If you don't have Stanford Parser or Stanford CoreNLP
You will need to install Java8 if you do not have it, and download the latest [Stanford Parser](https://nlp.stanford.edu/software/lex-parser.html#Download).

Once you have `stanford-parser-full-<version>.zip`, unzip it in this folder (`lab_2`).
Finally, update the constants in `exercise_1.py` (see [Constants](#constants) for the line number):
- `PATH_TO_STANFORD`: the path to your Stanford Parser folder, relative to this folder (`lab_2`) or absolute;
- `PATH_TO_JAR`: the path to the main Stanford Parser class, relative to this folder (`lab_2`) or absolute;
- `PATH_TO_MODELS_JAR`:  the path to the Stanford Parser models, relative to this folder (`lab_2`) or absolute;
- `CORENLP_MODE`: check that it is still set to `False`.

## Usage 
To use the project, you will need the two exercise files from the `lab_2` folder in [repository](https://github.com/EMarquer/data_science), as well as the exercises and data from `lab_1`.

Each of the exercise files is runable using `python exercise_#.py` (where `#` is the number of the exercise you want to execute).

Also, you can addapt the effects of the project by changing the value of some of the constants listed in [Constants](#constants).

To run the whole project, you need to run `exercise_1.py` then `exercise_2_3.py`.

### Description of the effect of each exercise file
#### `exercise_1.py`
This program load data generated from the [Gutenberg project](http://www.gutenberg.org/) during `lab_1`, and saved as a CSV catalogue, a SQL database, and TXT files containing a sentence per line.

The sentences are cleaned of their punctuation using the `string` package.

The sentences are then parsed by Scipy and Stanford Syntactic Parser (from Stanford Parser or Stanford CoreNLP, depending on your instalation and the value of `CORENLP_MODE`, see [Stanford Parser or Stanford CoreNLP](#stanford-parser-or-stanford-corenlp) for more information).

A set of features are extracted and stored into corresponding files, one of each per book:
- the sentences of the book, in a dictionary of `{sentence_ID: sentence_text}`, saved in `<book>.sentence.json`;
- the tokens of the sentences of the book, in a dictionary of `{sentence_ID: [token_text, ...]}`, saved in "`<book>.tokens.json`;
- the named entities of the sentences of the book and their tag, in a dictionary of `{sentence_ID: [[ne_text, ne_tag], ...]}`,: `<book>.ner.json`;
- the POS of the tokens of the sentences of the book, in a dictionary of `{sentence_ID: [token_POS, ...]}`, saved in `<book>.pos.json`;
- the syntactic tree oof the sentence, computed with Stanford's tool, in a dictionary of `{sentence_ID: "(ROOT: (...))"}`, saved in  `<book>.syntax.json`.

**Warning**:
- internet connection is required for the program to work;
- to run the program and not only import it, access to `../lab_1` is required;
- running this program will overwrite the previously processed data.

#### `exercise_2_3.py`
This program load the information from the JSON files producesd by `exercise_1.py`, and extract information from it to produce descriptive statistics.

It prints the following statistics in the console:
- the min, max and mean of the sentence size (token count), the VP count and the NP count;
- the POS distribution per author, as a Counter;
- the vocabulary size (unique token count) per author;
- the 10 most frequent named entity per named entity category per author, as a Counter.

It also produces the visualizations, that are saved to a file in `imgs/` if `TO_FILE` is `True`, and/or showed in a window if `TO_FILE` is `True` (see more detail in [Constants](#constants)).
The visualizations are the following:
- a bar plot of vocabulary size per author, saved in `voc_size.png` by default (see `VOC_PLOT_FILE`);
- a box plot of mean, min and max sentence size per author, saved in `sent_box.png` by default (see `SENT_PLOT_FILE`);
- a bar plot of distribution of POS per author, saved in `pos.png` by default (see `POS_PLOT_FILE`);
- a word cloud per author, saved in `<number>.png`, where `<number>` is an arbitrary number designating the author, the author name being written at the top of the word cloud.

**Warning**:
- running this program will overwrite the previously produced plots.

### Constants
The constants are stored at the begining of each exercise file. You can change the value of all the constants listed below to adapt the program.
Note that the constants from an exercise may be used in a later exercise.

| Constant | Exercise file | Line | Effect |
|-|-|-|-|
|VERBOSE| `exercise_2_3.py` | 23 | If `True`, will make the program describe what is going on during execution. |
|LANGUAGE| `exercise_1.py` | 18 | Language of the Scipy language model. Must be a language present in the table in [Spacy models and available languages](#spacy-models-and-available-languages). |
|SAVE_PATH| `exercise_1.py` | 22 |  Name of the folder in which the JSON files will be stored. |
|TASK_FILENAME_SCHEME| `exercise_1.py` | 30 | Structure of the names of the JSON files. The slots `{prefix}` and `{task}` will be replaced respectively by the book identifier and the parsing task to which the file correspond. |
|NER_ACCEPTED_LABELS| `exercise_1.py` | 31 | List of the Scipy named entity tags kept in the named entity parsing task. |
|TASK_SENTENCE| `exercise_1.py` | 32 | Name of the sentence parsing task. Used as a key to designate the task in multiple dictionaries, including `TASK_FILES`. |
|TASK_TOKENIZE| `exercise_1.py` | 33 | Name of the tokenisation task. Used as a key to designate the task in multiple dictionaries, including `TASK_FILES`. |
|TASK_NER| `exercise_1.py` | 34 | Name of the named entity recognition task. Used as a key to designate the task in multiple dictionaries, including `TASK_FILES`. |
|TASK_POS| `exercise_1.py` | 35 | Name of the token part-of-speech extraction task. Used as a key to designate the task in multiple dictionaries, including `TASK_FILES`. |
|TASK_SYNTAX| `exercise_1.py` | 36 | Name of the syntax parsing task. Used as a key to designate the task in multiple dictionaries, including `TASK_FILES`. |
|TASK_FILES| `exercise_1.py` | 37 | Mapping of the task to the corresponding file name element, that will be put in the  `{task}` field of `TASK_FILENAME_SCHEME`. |
|JAVA_PATH| `exercise_1.py` | 46 | Path to java installation *folder*. |
|JAVA_OPTIONS| `exercise_1.py` | 47 | Options to use when running Stanford Parser or CoreNLP Parser. |
|CORENLP_MODE| `exercise_1.py` | 48 | If `True`, will use a CoreNLP server for the parser. Otherwise, Stanford Parser is used. It is recomended to use Stanford Parser to avoid port issues. |
|PATH_TO_STANFORD| `exercise_1.py` | 49 | Path to the *folder* of the Stanford tool of your choice. |
|PATH_TO_JAR| `exercise_1.py` | 50 | Path to the *JAR file* of the main class of the Stanford tool of your choice. |
|PATH_TO_MODELS_JAR| `exercise_1.py` | 51 | Path to the *JAR file* of the models of the Stanford tool of your choice. |
|JSON_PATH| `exercise_2_3.py` | 26 | Name of the folder of the JSON files from `axercise_1.py`. |
|DATABASE_PATH| `exercise_2_3.py` | 29 | Name of the SQL database file, relative to the current directory (`lab_2`). |
|DATAFRAME_*| `exercise_2_3.py` | 33 | Name of the columns in the DataFrame. |
|NE_CATEGORIES| `exercise_2_3.py` | 44 | Mapping to reduce the named entity categories from scipy to `person`, `place` and `date`. |
|NE_MOST_FREQUENT_NUMBER| `exercise_2_3.py` | 56 | The number of most fequent named entity of each category to keep for the most frequent named entities distribution. |
|TO_FILE| `exercise_2_3.py` | 59 | If `True` will output the plots to files. |
SHOW = False  # if True will open the plots windows
|SHOW| `exercise_2_3.py` | 59 | If `True` will open the plots windows. |
|SAVE_PATH| `exercise_2_3.py` | 63 | Name of the folder in which the plots will be stored |
|VOC_PLOT_FILE| `exercise_2_3.py` | 68 | Name of save file of the bar plot of vocabulary size per author. |
|SENT_PLOT_FILE| `exercise_2_3.py` | 69 | Name of save file of the box plot of mean, min and max sentence size per author. |
|POS_PLOT_FILE| `exercise_2_3.py` | 70 | Name of save file of the bar plot of distribution of POS per author. |

## Files
Here is a list of files and a brief description for each of them:
- `data\<book>.<feature>.json`: `<book>` being the Gutenberg identifier of a book, `<feature>` being a feature computed in exercise 1, the file containg the feature for the senences from the book, more information in [`exercise_1.py`](#exercise_1py);
- `imgs\*.png`: the visualizations produced in exercise 3, more information in [`exercise_2_3.py`](#exercise_2_3py);
- `exercise_1.py`: file containing the functions used to solve the exercise 1;
- `exercise_2_3.py`: file containing the functions used to solve the exercise 2 and 3;
- `README.md`: this file, containing various informations about the project and its files.