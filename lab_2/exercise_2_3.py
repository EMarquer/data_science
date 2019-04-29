import re
from pandas import DataFrame
import os
from pprint import pprint
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS 
from numpy import mean

try:
    from .exercise_1 import load_json, TASK_FILENAME_SCHEME, TASK_FILES, TASK_NER, TASK_POS, TASK_SENTENCE, TASK_SYNTAX, TASK_TOKENIZE
    from ..lab_1.data_management import load_database, Author, Book
except (ValueError, ImportError):
    import sys, inspect
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir) 
    from lab_2.exercise_1 import load_json, TASK_FILENAME_SCHEME, TASK_FILES, TASK_NER, TASK_POS, TASK_SENTENCE, TASK_SYNTAX, TASK_TOKENIZE
    from lab_1.data_management import load_database, Author, Book

VERBOSE = False

# path to the JSON file
JSON_PATH = "data"

# path to the previously constructed database
DATABASE_PATH = "../lab_1/data/book_catalogue.db"

# DataFrame headers
DATAFRAME_AUTHOR = "Author name"
DATAFRAME_BOOK = "Book URI"
DATAFRAME_SENTENCE = "Sentence"
DATAFRAME_SENTENCE_ID = "Sentence ID"
DATAFRAME_TOKENS = "Tokens"
DATAFRAME_NE = "Named entities"
DATAFRAME_POS = "POS"
DATAFRAME_NP_COUNT = "NP count"
DATAFRAME_VP_COUNT = "VP count"
DATAFRAME_TOKEN_COUNT = "Token count"

# mapping to reduce the named entity categories from scipy to person, place and date
NE_CATEGORIES = {
    'PERSON': "person",
    'LOC': "place",
    'FAC': "place",
    'ORG': "person",
    'GPE': "place",
    'EVENT': "date",
    'DATE': "date",
    'TIME': "date"
}

# number of named entity to keep when getting the the most frequent entities for each type of named entity
NE_MOST_FREQUENT_NUMBER = 10

# ploting options
TO_FILE = True  # if True will output the plots to a file
SHOW = False  # if True will open the plots windows

# data save directory
SAVE_PATH = 'imgs'
if not os.path.isdir(SAVE_PATH):
    os.mkdir(SAVE_PATH)

# plot save files
VOC_PLOT_FILE = "voc_size.png"
SENT_PLOT_FILE = "box.png"
POS_PLOT_FILE = "pos.png"

def get_np_count(sent_syntax: str):
    # count all the NPs from a syntactic parsing tree
    np_count = len(re.findall('\(NP:', sent_syntax))
    return np_count

def get_vp_count(sent_syntax: str):
    # count all the VPs from a syntactic parsing tree
    vp_count = len(re.findall('\(VP:', sent_syntax))
    return vp_count

def load_data_to_dataframe(database_path=DATABASE_PATH, json_path=JSON_PATH,  task_filename_scheme=TASK_FILENAME_SCHEME, verbose=VERBOSE) -> DataFrame:
    # load the json data from exercise 1 and the database of lab_1 and construct a DataFrame with it
    session = load_database(database_path, quiet=True)
    task_filename_scheme = os.path.join(json_path, task_filename_scheme)
    
    sent_data = []
    for author in session.query(Author):
        for book in author.books:
            book_title, book_id, author_name = book.title, book.uri.split('/')[-1], author.name
            if verbose: print("Processing book '{title}' (URI: {uri}) from {author}".format(title=book_title, uri=book.uri, author=author_name))

            # load the result of exercise 1 for every book
            book_jsons = {task: load_json(task_filename_scheme.format(task=task_file, prefix=book_id)) for task, task_file in TASK_FILES.items()}

            # load or compute the necessary or interesting data for each sentence of the book
            sent_data += [{
                DATAFRAME_AUTHOR: author_name,
                DATAFRAME_BOOK: book.uri,
                DATAFRAME_SENTENCE: sent,
                DATAFRAME_SENTENCE_ID: sent_id,
                DATAFRAME_TOKENS: book_jsons[TASK_TOKENIZE][sent_id],
                DATAFRAME_TOKEN_COUNT: len(book_jsons[TASK_TOKENIZE][sent_id]),
                DATAFRAME_NE: book_jsons[TASK_NER][sent_id],
                DATAFRAME_POS: book_jsons[TASK_POS][sent_id],
                DATAFRAME_NP_COUNT: get_np_count(book_jsons[TASK_SYNTAX][sent_id]),
                DATAFRAME_VP_COUNT: get_vp_count(book_jsons[TASK_SYNTAX][sent_id])
            } for sent_id, sent in book_jsons[TASK_SENTENCE].items()]

    df = DataFrame(sent_data)
    
    return df

def count_pos(sentence_group):
    # produce a counter of POS over all the sentences of the group
    result = Counter()
    for sentence in sentence_group:
        result |= Counter(sentence)

    return result

def count_named_entity_per_type(sentence_group):
    # for each NE type, produce a counter of NE, over all the sentences of the group
    ne_types = dict()

    # dictionary of NE type as keys and the corresponding counter of NE
    result = dict()
    def get_category(category):
        if category not in result.keys(): result[category] = Counter()
        return result[category]

    # go through all the NEs and increment the corresponding counters
    for sentence in sentence_group:
        for ne, ne_tag in sentence:
            get_category(NE_CATEGORIES[ne_tag])[ne] += 1

    return result

def exercise_2(df: DataFrame):
    """Produce descriptive statistics from a dataframe"""

    print("Min, max and mean sentence size (token count), VP count and NP count")
    # filter the data on which the statistics will be computed, group it by author then compute the statistics per author
    described_data = df[[DATAFRAME_AUTHOR,DATAFRAME_TOKEN_COUNT,DATAFRAME_NP_COUNT,DATAFRAME_VP_COUNT]].groupby(DATAFRAME_AUTHOR).describe()
    described_data = described_data[[col for col in described_data.columns.values if col[1] in ["min", "max", "mean"]]]  # filter stat type
    print(described_data)

    print("POS distribution per author")
    # transform the groups of named into lists of sentences, then apply count_pos to get a distribution of POS per author
    pos = df.groupby(DATAFRAME_AUTHOR)[DATAFRAME_POS].apply(lambda x: x.tolist()).apply(count_pos)
    print(pos)

    print("Vocabulary size per author")
    # transform the groups of named into lists of sentences, then apply flatten the sentences of each group to a set, the vocabulary
    voc = df.groupby(DATAFRAME_AUTHOR)[DATAFRAME_TOKENS].apply(lambda x: x.tolist()).apply(
        lambda group: {token for sentence in group for token in sentence})
    voc_size = voc.apply(len)
    print(voc_size)

    print("10 most frequent named entity per named entity category per author")
    # transform the groups of named into lists of sentences, then apply count_named_entity_per_type to get a distribution of NE per NE category per author
    ne = df.groupby(DATAFRAME_AUTHOR)[DATAFRAME_NE].apply(lambda x: x.tolist()).apply(count_named_entity_per_type)
    ne_most_frequent = ne.apply(lambda ne_types: {ne_type: counter.most_common(NE_MOST_FREQUENT_NUMBER) for ne_type, counter in ne_types.items()})
    print(ne_most_frequent)

    # return the data used for plotting
    return voc, voc_size, pos

def plot_voc_size_per_author(voc_size, to_file=TO_FILE, show=SHOW):
    """bar plot of vocabulary size per Author"""

    # agregate the necessary data to a DataFrame
    voc_plot_data=[]
    for author_size, author in zip(voc_size, voc_size.index):
        voc_plot_data.append({"Vocabulary Size":author_size, "Author":author, "":""})  # add column "" of "" as a dummy value
    voc_plot_data = DataFrame(voc_plot_data)

    # plot the data
    #sns.barplot(x="Author", hue="Author", dodge=False, y="Vocabulary Size", data = DataFrame(voc_plot_data), ax=ax)
    sns.catplot(x="", hue="Author", y="Vocabulary Size", data=voc_plot_data, kind='bar')
    if to_file: plt.savefig(os.path.join(SAVE_PATH, VOC_PLOT_FILE))
    if show: plt.show()

def plot_sent_size_per_author(df, to_file=TO_FILE, show=SHOW):
    """box plot sent size per author"""

    # aggregate the data to a DataFrame
    box_plot_data = []
    df_grouped = df.groupby(DATAFRAME_AUTHOR)[DATAFRAME_TOKEN_COUNT].apply(lambda x: x.tolist())
    for token_counts, author in zip(df_grouped.values, df_grouped.index):
        box_plot_data.append({
            "Statistic": "Mean token count",
            "Value": mean(token_counts),
            DATAFRAME_AUTHOR: author})
        box_plot_data.append({
            "Statistic": "Min token count",
            "Value": min(token_counts),
            DATAFRAME_AUTHOR: author})
        box_plot_data.append({
            "Statistic": "Max token count",
            "Value": max(token_counts),
            DATAFRAME_AUTHOR: author})
    box_plot_df = DataFrame(box_plot_data)

    # plot the data
    g = sns.catplot(x="Statistic", y="Value",
        data=box_plot_df,
        kind="box")
    if TO_FILE: plt.savefig(os.path.join(SAVE_PATH, SENT_PLOT_FILE))
    if SHOW: plt.show()

def plot_pos_per_author(pos, to_file=TO_FILE, show=SHOW):
    """stacked bar POS distrib (hist)"""

    # agregate the necessary data to a DataFrame
    pos_plot_data=[]
    for author_counter, author in zip(pos, pos.index):
        for pos_tag, pos_count in author_counter.items():
            pos_plot_data.append({"POS":pos_tag, "Count":pos_count, "Author":author})
    pos_plot_data=DataFrame(pos_plot_data)

    # plot the data
    sns.catplot(x="POS", y="Count", hue="Author", data = pos_plot_data,kind='bar',
                       legend_out=True, height=5, aspect=2)
    if TO_FILE: plt.savefig(os.path.join(SAVE_PATH, POS_PLOT_FILE))
    if SHOW: plt.show()

def plot_word_clouds(voc, to_file=TO_FILE, show=SHOW):
    """plot a word cloud per author"""

    i = 0  # index used for the file name
    for author, tokens in zip(voc.index, voc):
        # generate the word cloud for the author
        wordcloud = WordCloud(width = 800, height = 800, 
                background_color ='white', 
                collocations = False,
                stopwords = set(STOPWORDS), 
                min_font_size = 10).generate(' '.join(tokens))
  
        # plot the WordCloud image                        
        plt.figure(figsize = (8, 8), facecolor = None) 
        plt.imshow(wordcloud) 
        plt.axis("off") 
        plt.title(author)
        plt.tight_layout() 
        if TO_FILE: plt.savefig(os.path.join(SAVE_PATH, '{:02}'.format(i))); i+=1
        if SHOW: plt.show()

def exercise_3(df, voc, voc_size, pos, to_file=TO_FILE, show=SHOW):
    """Plot the data for the statistics"""
    # bar plot of vocabulary size per Author
    plot_voc_size_per_author(voc_size, to_file=to_file, show=show)

    # box plot sent size per author 
    plot_sent_size_per_author(df, to_file=to_file, show=show)

    # stacked bar pos distrib (hist)    
    plot_pos_per_author(pos, to_file=to_file, show=show)

    # word cloud
    plot_word_clouds(voc, to_file=to_file, show=show)

if __name__=="__main__":
    # load the data from exercise
    df = load_data_to_dataframe()

    # get raw statistics
    voc, voc_size, pos = exercise_2(df)

    # produce plots
    exercise_3(df, voc, voc_size, pos)


    

    


