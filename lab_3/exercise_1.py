from pandas import DataFrame, Series
import os.path
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.datasets import dump_svmlight_file, load_svmlight_file, load_svmlight_files
from numpy import mean, arange, ndarray
from numpy.random import permutation, seed
seed(12345)
from scipy.sparse import csr_matrix, spmatrix
from typing import Dict, List, Union, Tuple

try:
    from ..lab_2.exercise_2_3 import (load_data_to_dataframe, JSON_PATH, DATAFRAME_AUTHOR, DATAFRAME_BOOK,
        DATAFRAME_POS, DATAFRAME_TOKENS, DATAFRAME_TOKEN_COUNT, DATAFRAME_NE, DATAFRAME_VP_COUNT)
except (ValueError, ImportError):
    import sys, inspect
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir) 
    from lab_2.exercise_2_3 import (load_data_to_dataframe, JSON_PATH, DATAFRAME_AUTHOR, DATAFRAME_BOOK,
        DATAFRAME_POS, DATAFRAME_TOKENS, DATAFRAME_TOKEN_COUNT, DATAFRAME_NE, DATAFRAME_VP_COUNT)
    JSON_PATH = os.path.join(parent_dir, "lab_2", JSON_PATH)

VERBOSE = True

# Hyperparameters
INSTANCES_PER_AUTHOR = 50
SENTENCES_PER_INSTANCE = 2

# Accepted POS for POS-filtered tokens
ACCEPTED_POS = {'ADJ', 'ADV', 'VERB', 'ADV'}

# proportion of the data to use as training set, the rest is used for the test set
TRAIN_RATIO = .8

# data used to compute features
# DATAFRAME_TOKENS (imported)
DATAFRAME_TOKEN_POS = "POS-filtered tokens"
# DATAFRAME_NE (imported)

# feature names and target name
DATAFRAME_TOKEN_TF_IDF = "Token TF-IDF-normalized frequencies"
DATAFRAME_NE_TF_IDF = "Named entity TF-IDF-normalized frequencies"
DATAFRAME_TOKEN_POS_TF_IDF = "POS-filtered tokens TF-IDF-normalized frequencies"
DATAFRAME_VP_COUNT_MEAN = "Average VP number per sentence"
DATAFRAME_TOKEN_COUNT_MEAN = "Average token number per sentence"
DATAFRAME_TARGET = "Target"

# computed features and corresponding raw data columns
TF_IDF_FEATURES = {
    DATAFRAME_TOKEN_TF_IDF: DATAFRAME_TOKENS,
    DATAFRAME_NE_TF_IDF: DATAFRAME_NE,
    DATAFRAME_TOKEN_POS_TF_IDF: DATAFRAME_TOKEN_POS
}
MEAN_FEATURES = {
    DATAFRAME_VP_COUNT_MEAN: DATAFRAME_VP_COUNT,
    DATAFRAME_TOKEN_COUNT_MEAN: DATAFRAME_TOKEN_COUNT
}

# set of all the feature names and set of raw data columns
FEATURES = TF_IDF_FEATURES.keys() | MEAN_FEATURES.keys()
RAW_DATA = set(TF_IDF_FEATURES.values()) | set(MEAN_FEATURES.values())

# save files
# save file for the target / author maping
TARGET_TO_AUTHOR_CSV_FILE_NAME = "target_to_author.csv"
# formattable fole name for the features, the '{dataset}' field and the '{feature}' field will be formatted
FEATURES_FILE_NAME_PATTERN = "{dataset}.{feature}.svmlight"
# dataset file prefix, will be put in the '{dataset}' field of FILE_NAME_FEATURES_PATTERN
FILE_PREFIX_TRAIN, FILE_PREFIX_TEST = "train", "test"
# feature file prefix, will be put in the '{feature}' field of FILE_NAME_FEATURES_PATTERN
FILE_PREFIX_FEATURES = {
    DATAFRAME_TOKEN_TF_IDF: "token_tf_idf",
    DATAFRAME_NE_TF_IDF: "ne_tf_idf",
    DATAFRAME_TOKEN_POS_TF_IDF: "pos_token_tf_idf",
    DATAFRAME_VP_COUNT_MEAN: "vp_count_mean",
    DATAFRAME_TOKEN_COUNT_MEAN: "token_count_mean"
}

# general save directory
SAVE_PATH = 'data'
if not os.path.isdir(SAVE_PATH):
    os.mkdir(SAVE_PATH)

def prepare_features(instance_df: DataFrame) -> Dict[str, Union[str, List[str], List[int]]]:
    """Produce a dictionary of the data necessary to compute the features, given an istance DataFrame.
    
    Currently supported features:
        - author name;
        - book title;
        - list of all the tokens;
        - list of all the tokens filtered by ACCEPTED_POS;
        - list of the token count per sentence (sentence length);
        - list of the VP count per sentence.

    :param instance_df: DataFrame of an instance, one row per sentence.
    :return: A dictionary representing the instance
    """
    # expected to be the same for all the values
    author = instance_df[DATAFRAME_AUTHOR].values[0]
    book = instance_df[DATAFRAME_BOOK].values[0]

    # flatten the lists of tokens, POS and named entities ('NE'/'ne' for named entity, 'nes' for the plural)
    tokens = [token for sentence_tokens in instance_df[DATAFRAME_TOKENS] for token in sentence_tokens]
    pos = [pos for sentence_pos in instance_df[DATAFRAME_POS] for pos in sentence_pos]
    nes = [ne for sentence_nes in instance_df[DATAFRAME_NE] for ne, ne_tag in sentence_nes]

    # Filter the tokes by their POS using ACCEPTED_POS as a filter
    tokens_pos = [token for token, token_pos in zip(tokens, pos) if token_pos in ACCEPTED_POS]

    # store the VP count and token count per sentence
    token_count = instance_df[DATAFRAME_TOKEN_COUNT].values
    vp_count = instance_df[DATAFRAME_VP_COUNT].values

    # store all the information in a dictionary
    instance = {
        # features for instance selection
        DATAFRAME_AUTHOR: author,
        DATAFRAME_BOOK: book,

        # data used to compute features
        DATAFRAME_TOKENS: tokens,
        DATAFRAME_TOKEN_POS: tokens_pos,
        DATAFRAME_NE: nes,
        DATAFRAME_TOKEN_COUNT: token_count,
        DATAFRAME_VP_COUNT: vp_count
    }

    return instance

def compute_target(df: DataFrame, verbose: bool=VERBOSE) -> Dict[int, str]:
    """Add a DATAFRAME_TARGET column to a dataframe, containing the target of the lines.
    
    The target is a numerical representation of the author, used in SVMLight format.
    A dictionary with author as values and the corresponding index as keys is returned, to allow interpretation of the
    targets.

    :param df: The dataframe to process.
    :param verbose: If True, will print the author/index mapping.

    :return: A dictionary with authors as values and the corresponding index as keys.
    """
    # create a mapping from the authors to the natural numbers
    target_to_author =  dict(enumerate(df[DATAFRAME_AUTHOR].unique()))  # dictionary: {index: author_name}
    author_to_target = {author: index for index, author in target_to_author.items()}  # dictionary: {author_name: index}

    if verbose: print("Author to index mapping:\n{}".format(author_to_target))

    # create a new column containig the index of the author, by searching every author in author_to_index
    # (equivalent to applying author_to_index[author] to every author)
    df[DATAFRAME_TARGET] = df[DATAFRAME_AUTHOR].apply(author_to_target.__getitem__)

    # return the mapping index_to_author, to allow the interpretation of targets as authors
    return target_to_author

def compute_means(df: DataFrame, verbose: bool=VERBOSE) -> None:
    """For each mean feature, add columns to a dataframe, containing the mean of the values used as source.

    The mean features are stored in MEAN_FEATURES. It is a dictionary of the mean feature names as keys, and the name
    of the column containing the corresponding source data as values.

    Each cell in the source coulumn is expected to contain an iterable of numbers; the mean of the values in the
    iterable is the mean feature.

    :param df: The DataFrame to process.
    :param verbose: If True, will print each mean feature when it is computed."""
    for mean_feature, source_data in MEAN_FEATURES.items():
        if verbose: print("Computing mean feature '{}' from the data in '{}'".format(mean_feature, source_data))

        df[mean_feature] = df[source_data].apply(mean)

def compute_tf_idf(train_df: DataFrame, test_df: DataFrame, verbose: bool=VERBOSE) -> Tuple[Dict[str, csr_matrix],
    Dict[str, csr_matrix]]:
    """For each TF-IDF feature, train a TfidfVectorizer on the training data and apply it on the training and test data.

    The TF-IDF features are stored in TF_IDF_FEATURES. It is a dictionary of the TF-IDF feature names as keys, and the
    name of the collumn containing the corresponding source data as values.
    
    :param train_df: The DataFrame of the training set.
    :param test_df: The DataFrame of the test set.
    :param verbose: If True, will print each TF-IDF feature when it is computed.

    :return: Two dictionaries, the first for the training set and the second for the test set.
        Each dictionary has TF-IDF feature names as keys and the corresponding sparse matrix as values.
        The sparse matrices are scipy.csr_martix.
    """
    # generate a TfidfVectorizer per feature to process
    tf_idfs = {tf_idf_feature: TfidfVectorizer(smooth_idf=True) for tf_idf_feature in TF_IDF_FEATURES.keys()}

    # TF-IDF normalised frequencies from list of values (train and apply TfidfVectorizer)
    train_tf_idf, test_tf_idf = dict(), dict()
    for tf_idf_feature, source_data in TF_IDF_FEATURES.items():
        if verbose: print("Computing TF-IDF feature '{}' from the data in '{}'".format(tf_idf_feature, source_data))

        # need to join the lists of values into single strings for the TfidfVectorizer
        train_data, test_data = train_df[source_data].apply(' '.join), test_df[source_data].apply(' '.join)

        # train and apply the TfidfVectorizer on the training data, and apply it on the test data
        train_tf_idf[tf_idf_feature] = tf_idfs[tf_idf_feature].fit_transform(train_data)
        test_tf_idf[tf_idf_feature] = tf_idfs[tf_idf_feature].transform(test_data)

    return train_tf_idf, test_tf_idf

def group_sentenses_to_instances(
        sentence_df: DataFrame,
        sentences_per_instance: int=SENTENCES_PER_INSTANCE,
        verbose: bool=VERBOSE) -> List[DataFrame]:
    """Produce packets (instances) of a specific number of sentences, leftover sentences are ignored.

    Instances do not overlap with eah other (is a sentence is in one instance, it can not be in another instance).
    
    :param sentence_df: The DataFrame containing the sentences.
    :param sentences_per_instance: The number of sentence per instance.
    :param verbose: If True, will print the new instances when they are computed.

    :return: A list of DataFrame, each of them corresponding to an instance. The rows of those DataFrame are sentences.
    """
    # group sentences into packets of size exactly sentences_per_instance; there may be leftovers
    instances = [sentence_df[i: i+sentences_per_instance] for i in range(0, len(sentence_df) - sentences_per_instance, sentences_per_instance)]
    if verbose:
        for instance in instances: print("New instance:\n{}".format(instance))

    return instances

def produce_instances(
        data: DataFrame,
        instances_per_author: int=INSTANCES_PER_AUTHOR,
        sentences_per_instance: int=SENTENCES_PER_INSTANCE,
        verbose=VERBOSE) -> DataFrame:
    """Produce a DataFrame of instances, containing the data necesssary to compute the features and targets.
    
    Each row correspond to a different instance.
    An instance is a set of sentences from the same book of an author.
    
    :param sentence_df: The DataFrame containing the sentences.
    :param instances_per_author: The target number of instances per author. If there is not enough data, will use as
        many instances as possible.
    :param sentences_per_instance: The number of sentence per instance.
    :param verbose: If True, will print the new instances when they are computed.

    :return: A list of DataFrame, each of them corresponding to an instance. The rows of those DataFrame are sentences.
    """
    # group by book
    books = data.groupby(DATAFRAME_BOOK)

    # for each book, produce as many instances as possible
    instances_per_book = books.apply(group_sentenses_to_instances, sentences_per_instance=sentences_per_instance, verbose=verbose)

    # prepare the data used for the features for each instance
    features = [prepare_features(instance) for book_instances in instances_per_book for instance in book_instances]
    features_df = DataFrame(features)

    # get only the required number of instances per author, and filter the necessary columns
    df_reduced = features_df.groupby(DATAFRAME_AUTHOR).apply(lambda x: x.head(instances_per_author))
    df_reduced = df_reduced[[DATAFRAME_AUTHOR, *RAW_DATA]]
    if verbose: print("Dataframe with {} instances of {} sentences per author:\n{}".format(instances_per_author, sentences_per_instance, df_reduced))

    return df_reduced

def save_feature(X: Union[csr_matrix, Series], y: Series, file_name: str) -> None:
    """Save a feature to a SVMLight file.

    :param X: The data to save, should be either a mean feature (Series of numbers) or a TF-IDF feature 
    (scipy.csr_matrix).
    :param y: The target to save, should be either a mean feature (Series of integer).
    :param file_name: The name of the output file.
    """
    # is the data is a Series, transform it into a 2D array
    if isinstance(X, Series): X = X.values.reshape(-1, 1)
    dump_svmlight_file(X, y, file_name)

def save_data(
        train_df: DataFrame,
        test_df: DataFrame,
        train_tf_idf: Dict[str, csr_matrix],
        test_tf_idf: Dict[str, csr_matrix],
        target_to_author: Dict[int, str],
        file_path: str=SAVE_PATH,
        features_file_name_pattern: str=FEATURES_FILE_NAME_PATTERN,
        target_to_author_file_name: str=TARGET_TO_AUTHOR_CSV_FILE_NAME,
        verbose: bool=VERBOSE) -> None:
    """Save all the TF-IDF and mean features to SVMLight files, and the target to author mapping to a CSV file.
    
    Currently supported features:
        - author name;
        - book title;
        - list of all the tokens;
        - list of all the tokens filtered by ACCEPTED_POS;
        - list of the token count per sentence (sentence length);
        - list of the VP count per sentence.
    
    :param train_df: The Dataframe of the training set, containing the targets and mean features.
    :param test_df: The Dataframe of the test set, containing the targets and mean features.
    :param train_tf_idf: The dictionary of csr_matrix of the training set, containing the TF-IDF features.
    :param test_tf_idf: The dictionary of csr_matrix of the test set, containing the TF-IDF features.
    :param target_to_author: The target to author mapping dictionary.

    :param file_path: The folder in which save the data.
    :param features_file_name_pattern: A string containing formatable slots named 'feature' and 'dataset'.
        When formated with a feature prefix from FILE_PREFIX_FEATURES and a dataset prefix (either FILE_PREFIX_TRAIN or
        FILE_PREFIX_TEST), will be the name of the file where the feature for the dataset will be saved.
    :param target_to_author_file_name: The name of the CSV file where the target to author maping will be saved.

    :param verbose: If True, will print where the features are saved when they are saved.
    """
    features_file_name_pattern = os.path.join(file_path, features_file_name_pattern)
    
    # save TF-IDF features
    for tf_idf_feature in TF_IDF_FEATURES.keys():
        # prepare the file name
        train_file_name = features_file_name_pattern.format(
            dataset=FILE_PREFIX_TRAIN,
            feature=FILE_PREFIX_FEATURES[tf_idf_feature])
        test_file_name  = features_file_name_pattern.format(
            dataset=FILE_PREFIX_TEST,
            feature=FILE_PREFIX_FEATURES[tf_idf_feature])

        # saving the training set for the feature
        if verbose:
            print("Saving TF-IDF feature '{}' to '{}' and '{}'".format(tf_idf_feature, train_file_name, test_file_name))
        save_feature(X = train_tf_idf[tf_idf_feature], y = train_df[DATAFRAME_TARGET], file_name = train_file_name)
        save_feature(X = test_tf_idf[tf_idf_feature],  y = test_df[DATAFRAME_TARGET],  file_name = test_file_name)

    # save the mean features
    for mean_feature in MEAN_FEATURES.keys():
        # prepare the file name
        train_file_name = features_file_name_pattern.format(
            dataset=FILE_PREFIX_TRAIN,
            feature=FILE_PREFIX_FEATURES[mean_feature])
        test_file_name  = features_file_name_pattern.format(
            dataset=FILE_PREFIX_TEST,
            feature=FILE_PREFIX_FEATURES[mean_feature])

        # saving the training set for the feature
        if verbose:
            print("Saving mean feature '{}' to '{}' and '{}'".format(mean_feature, train_file_name, test_file_name))
        save_feature(X = train_df[mean_feature], y = train_df[DATAFRAME_TARGET], file_name = train_file_name)
        save_feature(X = test_df[mean_feature],  y = test_df[DATAFRAME_TARGET],  file_name = test_file_name)

    # save the target to author maping
    target_to_author_file_name = os.path.join(file_path, target_to_author_file_name)
    if verbose: print("Saving target to author maping to '{}'".format(target_to_author_file_name))
    DataFrame.from_dict(target_to_author, orient='index', columns=[DATAFRAME_AUTHOR]).to_csv(target_to_author_file_name)

def load_feature(
        feature: str,
        file_path: str=SAVE_PATH,
        features_file_name_pattern: str=FEATURES_FILE_NAME_PATTERN) -> Tuple[spmatrix, ndarray, spmatrix, ndarray]:
    """Load a train and test set for a feature.
    
    :param feature: The file prefix of the feature to load.
    :param file_path: The folder in which save the data.
    :param features_file_name_pattern: A string containing formatable slots named 'feature' and 'dataset'.
        When formated with a feature prefix from FILE_PREFIX_FEATURES and a dataset prefix (either FILE_PREFIX_TRAIN or
        FILE_PREFIX_TEST), will be the name of the file where the feature for the dataset will be saved.

    :return: The scipy.sparse matrix of shape (n_samples, n_features) of the feature data, and the ndarray of shape
        (n_samples,) of the feature targets, for the train and the test datasets
        (a total of 4 elements: X_train, y_train, X_test, y_test).
    """
    # add the file path to the file name
    features_file_name_pattern = os.path.join(file_path, features_file_name_pattern)

    # load train and test for the feature
    X_train, y_train = load_svmlight_file(features_file_name_pattern.format(feature=feature, dataset=FILE_PREFIX_TRAIN))
    X_test, y_test = load_svmlight_file(features_file_name_pattern.format(feature=feature, dataset=FILE_PREFIX_TEST))

    # resize the Xs to the same number of features
    n_features = max(X_train.shape[1], X_test.shape[1])
    X_train.resize((X_train.shape[0], n_features))
    X_test.resize((X_test.shape[0], n_features))

    return X_train, y_train, X_test, y_test

def load_and_process(
        instances_per_author: int=INSTANCES_PER_AUTHOR,
        sentences_per_instance: int=SENTENCES_PER_INSTANCE,
        train_ratio: float=TRAIN_RATIO,
        save_path: str=SAVE_PATH,
        features_file_name_pattern: str=FEATURES_FILE_NAME_PATTERN,
        target_to_author_file_name: str=TARGET_TO_AUTHOR_CSV_FILE_NAME,
        json_path=JSON_PATH,
        verbose=VERBOSE) -> None:
    """Load book data from JSON files, pack the sentences into instances, and produce SVMLight files for a set of 
    featrues.
    
    Currently supported features:
        - author name;
        - book title;
        - list of all the tokens;
        - list of all the tokens filtered by ACCEPTED_POS;
        - list of the token count per sentence (sentence length);
        - list of the VP count per sentence.
    
    :param instances_per_author: The target number of instances per author. If there is not enough data, will use as
        many instances as possible.
    :param sentences_per_instance: The number of sentence per instance.
    :param train_ratio: The ratio of the DataFrame corresponding to the training set. The rest of the DataFrame
        corresponds to the test set. Must be strictly between 0 and 1, otherwise an AssertionError is raised.
    :param save_path: The folder in which save the data.
    :param features_file_name_pattern: A string containing formatable slots named 'feature' and 'dataset'.
        When formated with a feature prefix from FILE_PREFIX_FEATURES and a dataset prefix (either FILE_PREFIX_TRAIN or
        FILE_PREFIX_TEST), will be the name of the file where the feature for the dataset will be saved.
    :param target_to_author_file_name: The name of the CSV file where the target to author maping will be saved.

    :param verbose: If True, will print where the features are saved when they are saved.
    """

    # load data
    df = load_data_to_dataframe(json_path=json_path, verbose=verbose)

    # split into instances and extract usefull data
    instances_df = produce_instances(
        df,
        instances_per_author = instances_per_author,
        sentences_per_instance = sentences_per_instance,
        verbose = verbose)

    # compute count features, independent from train/test splitting
    compute_means(instances_df, verbose = verbose)  # inplace operation adding a column
    # compute target value, independent from train/test splitting
    target_to_author = compute_target(instances_df, verbose = verbose)  # inplace operation adding a column

    # split into train/test with stratification to avoid problems in exercise 2
    train_df, test_df = train_test_split(instances_df, train_size=train_ratio)

    # compute tf-idf normalized features, dependent of train/test splitting
    train_tf_idf, test_tf_idf = compute_tf_idf(train_df, test_df, verbose=verbose)

    # save data to 
    save_data(train_df, test_df, train_tf_idf, test_tf_idf, target_to_author,
        file_path=save_path,
        features_file_name_pattern=features_file_name_pattern,
        target_to_author_file_name=target_to_author_file_name,
        verbose=verbose)

    if verbose: print("\nProcessing completed sucessfully.")

if __name__=="__main__":
    load_and_process()