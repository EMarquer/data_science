# Data science exam, lab session 2
Pre-processing of datasets, training and optimisation of machine learning models.

This README can be found at [https://github.com/EMarquer/data_science](https://github.com/EMarquer/data_science).

## In this README
- [In this README](#in-this-readme)
- [Description](#description)
    - [Exercise 1](#exercise-1)
    - [Exercise 2](#exercise-2)
- [Setup](#setup)
    - [Built-in Python dependencies](#built-in-python-dependencies)
    - [External dependencies](#external-dependencies)
- [Usage](#usage)
    - [Description of the effect of each exercise file](#description-of-the-effect-of-each-exercise-file)
        - [`exercise_1.py`](#exercise_1py)
        - [`exercise_2.py`](#exercise_2py)
    - [Constants](#constants)
- [Files](#files)

## Description
This project was done for the UE803: Data Science of the NLP Master Program of Nancy.
It corresponds to the third of three lab sessions of the evaluation of the UE.

The lab session is split in two exercises around the pre-processing of machine learning datasets and the training and optimisation of machine learning models.

The code of each exercise is stored in a different file (see [Files](#files)).

### Exercise 1
The first exercise correspond to the pre-processing and storage of different features.

The data from exercise 2 of lab 2 is packed into instances (groups of sentences), such that:
- each author have at most a certain number of instances, to keep the data balanced;
- the instances do not span over multiple books;
- instances do not overlap (if a sentence is in an instance, it is not present in any other).

The data is processed to obtain the following features:
- token TF-IDF-normalized frequencies;
- named entity TF-IDF-normalized frequencies;
- POS-filtered tokens TF-IDF-normalized frequencies;
- average VP number per sentence;
- average token number per sentence.

Also, the authors are prepared as targets, and a mapping of the authors to numbers is done.

All the features and the correspondig target are saved to SVMLight format, and the mapping is saved to CSV.

### Exercise 2
The first exercise correspond to the training and optimisation of machine learning models: the Naive Bayes and the Logitic Regression models.

The features produced in exercise 1 are used to train the two models using grid-search and cross validation.

In each of the training setups (a feature, a model, and an optimisation score), the best model is evaluated. This evaluation is stored as plots, one for each feature.

## Setup
To use the project, you will need a valid `Python 3.7.1` installation as well as the external libraries described in [External dependencies](#external-dependencies) (check that you have the correct versions!). Also, the files and scripts from `lab_1` and `lab_2` are required.

### Built-in Python dependencies
The project relies on the following `Python 3.7.1` built-in libraries:
| Library       |
|---------------|
| os            |
| typing        |
| sys           |
| inspect       |
| pprint        |

### External dependencies
The project uses the following python libraries:
| Library       | Version   |
|---------------|-----------|
| pandas        | 0.23.4    |
| scikit-learn  | 0.20.1    |
| numpy         | 1.15.4    |
| scipy         | 1.1.0     |

## Usage 
To use the project, you will need all the files from the [repository](https://github.com/EMarquer/data_science).

Each of the exercise files is runable using `python exercise_#.py` (where `#` is the number of the exercise you want to execute).

Also, you can addapt the effects of the project by changing the value of some of the constants listed in [Constants](#constants).

To run the whole project, you need to run `exercise_1.py` then `exercise_2.py`.

### Description of the effect of each exercise file
#### `exercise_1.py`
This program loads the data from the `lab_2\data` and `lab_1\data` folders, using the methods in `lab_2\exercise_2_3.py`.

The data is packed into instances (groups of sentences) and split into a training and a test set (with a 80% to 20% repartition of the instances). The data is finally processed to obtain the following set of features, each of which is saved to two files in `data/` (see more detail in [Constants](#constants)):
- token TF-IDF-normalized frequencies, saved in `train.token_tf_idf.svmlight` and `test.token_tf_idf.svmlight`;
- named entity TF-IDF-normalized frequencies, saved in `train.ne_tf_idf.svmlight` and `test.ne_tf_idf.svmlight`;
- POS-filtered tokens TF-IDF-normalized frequencies, saved in `train.pos_token_tf_idf.svmlight` and `test.pos_token_tf_idf.svmlight`;
- average VP number per sentence, saved in `train.vp_count_mean.svmlight` and `test.vp_count_mean.svmlight`;
- average token number per sentence, saved in `train.token_count_mean.svmlight` and `test.token_count_mean.svmlight`.

The target is computed from a mapping of the authors to integers, which is stored in `target_to_author.csv` (see `TARGET_TO_AUTHOR_CSV_FILE_NAME` in)
TARGET_TO_AUTHOR_CSV_FILE_NAME = "target_to_author.csv"

**Warning**:
- running this program will overwrite the previously extracted datasets.

#### `exercise_2.py`
This program uses the features produced in exercise 1 to train a MultinomialNB and a LogisticRegression using GridSearchCV, and using two optimisation scores: `precision_macro` and `recall_macro`.

An artificial feature composed of all the features together is also used.

Each of the best models found by GridSearchCV is tested, and the performance is printed in the console.

Finally, to visualize the performance, a set of bar plots is generated for each feature, and stored into `imgs\<feature>.png`, where the file name for the feature is the same as the one from exercise 1.

**Warning**:
- running this program will overwrite the previously generated plots.

### Constants
The constants are stored at the begining of each exercise file. You can change the value of all the constants listed below to adapt the program.
Note that the constants from an exercise may be used in a later exercise.

| Constant | Exercise file | Line | Effect |
|-|-|-|-|
|VERBOSE| `exercise_1.py` | 24 | If `True`, will make the program describe what is going on during execution. |
|VERBOSE| `exercise_2.py` | 11 | If `True`, will make the program describe what is going on during execution. |
|INSTANCES_PER_AUTHOR| `exercise_1.py` | 27 | The maximum number of instances to create for each author. |
|SENTENCES_PER_INSTANCE| `exercise_1.py` | 28 | The number of sentence to pack in each instance. |
|ACCEPTED_POS| `exercise_1.py` | 31 | List of the Spacy POS tags for the POS-filtered feature. |
|TRAIN_RATIO| `exercise_1.py` | 34 | Proportion of the data to use as training set, the rest is used for the test set. |
|DATAFRAME_*| `exercise_1.py` | 38 | Name of the columns in the DataFrame used to store the information on each instance. Also used as keys in some dictionaries like `TF_IDF_FEATURES`. |
|TF_IDF_FEATURES| `exercise_1.py` | 50 | Maping of the features using TF-IDF normalization to the column containing the data used to compute them. |
|MEAN_FEATURES| `exercise_1.py` | 55 | Maping of the features using a mean over the sentences to the column containing the data used to compute them. |
|FEATURES| `exercise_1.py` | 61 | Set of all the features. |
|RAW_DATA| `exercise_1.py` | 62 | Set of all the data used to compute the features. |
|FILE_PREFIX_TRAIN| `exercise_1.py` | 70 | File name element that will be put in the  `{dataset}` field of `FEATURES_FILE_NAME_PATTERN` for the training set. |
|FILE_PREFIX_TEST| `exercise_1.py` | 70 | File name element that will be put in the  `{dataset}` field of `FEATURES_FILE_NAME_PATTERN` for the training test. |
|FILE_PREFIX_FEATURES| `exercise_1.py` | 72 | Mapping of the feature to the corresponding file name element, that will be put in the  `{feature}` field of `FEATURES_FILE_NAME_PATTERN`. |
|SAVE_PATH| `exercise_1.py` | 81 | Name of the folder in which the SVMLight files will be stored. |
|CLF_PARA_DICT| `exercise_2.py` | 15 | Mapping of the classifier classes to the corresponding tuning parameters used in grid-search. |
|CLF_PARA_DICT| `exercise_2.py` | 21 | List of the scores used in grid-search to sellect the best model. |
|CV| `exercise_2.py` | 21 | Number of cross validataion to do. |
|SAVE_PATH| `exercise_2.py` | 27 | Name of the folder in which the plots will be stored. |

## Files
Here is a list of files and a brief description for each of them:
- `data\<dataset>.<feature>.svmlight`: `<dataset>` either the training or the test set, `<feature>` being a feature computed in exercise 1, the file containg the dataset for the feature, more information in [`exercise_1.py`](#exercise_1py);
- `data\target_to_author.csv`: CSV file containing the mapping of the authors to integers targets, computed in [`exercise_1.py`](#exercise_1py);
- `imgs\<feature>.png`: `<feature>` being a feature used in exercise 2, the plot abouut the performances of the models on the feature, more information in [`exercise_2.py`](#exercise_2py);
- `exercise_1.py`: file containing the functions used to solve the exercise 1;
- `exercise_2.py`: file containing the functions used to solve the exercise 2;
- `README.md`: this file, containing various informations about the project and its files;