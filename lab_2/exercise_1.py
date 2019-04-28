import json
import spacy
import os
import string
from nltk.parse.stanford import StanfordParser
from nltk.parse.corenlp import CoreNLPParser, CoreNLPServer

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

# data save directory
SAVE_PATH = 'data'
if not os.path.isdir(SAVE_PATH):
    os.mkdir(SAVE_PATH)

# punctuation remover
PUNCT_REMOVER = str.maketrans('', '', string.punctuation)

# task-specific information
TASK_FILENAME_SCHEME = "{prefix}.{task}.json"
NER_ACCEPTED_LABELS = {'PERSON', 'LOC', 'FAC', 'ORG', 'GPE', 'EVENT', 'DATE', 'TIME'} # see https://spacy.io/api/annotation#named-entities
TASK_SENTENCE = "sentence parsing and cleaning"
TASK_TOKENIZE = "tokenize"
TASK_NER = "named entity recognition (ner)"
TASK_POS = "POS"
TASK_SYNTAX = "syntactic parsing"
TASK_FILES = {
    TASK_SENTENCE: "sentence",
    TASK_TOKENIZE: "tokens",
    TASK_NER: "ner",
    TASK_POS: "pos",
    TASK_SYNTAX: "syntax"
}

# standford parser options
JAVA_PATH = os.path.join("C:\\","Program Files","Java","jdk-11.0.2")#,"bin","java.exe")  # set to False or None to use the default Java path
JAVA_OPTIONS = '-mx6g'
CORENLP_MODE = False  # if True, will use a CoreNLP server for the parser; necessary if file contains \ or /; was buggy for me
PATH_TO_STANFORD = "stanford-corenlp-full-2018-10-05" if CORENLP_MODE else "stanford-parser-full-2018-10-17"
PATH_TO_JAR = os.path.join(PATH_TO_STANFORD, "stanford-corenlp-3.9.2.jar" if CORENLP_MODE else "stanford-parser.jar")
PATH_TO_MODELS_JAR = os.path.join(PATH_TO_STANFORD, "stanford-corenlp-3.9.2-models.jar" if CORENLP_MODE else "stanford-parser-3.9.2-models.jar")


# standford parser singleton
STANDFORD = dict()
def get_standford(corenlp_mode=CORENLP_MODE):
    # load the parser
    if not STANDFORD:
        if JAVA_PATH: os.environ['JAVAHOME'] = JAVA_PATH

        if corenlp_mode:
            STANDFORD["server"] = CoreNLPServer(
                path_to_jar = PATH_TO_JAR,
                path_to_models_jar = PATH_TO_MODELS_JAR,
                java_options=JAVA_OPTIONS, verbose=True)
            print("starting server")
            STANDFORD["server"].start()
            print("server on")
            STANDFORD["parser"] = CoreNLPParser(url=STANDFORD["server"].url)
        else:
            STANDFORD["parser"] = StanfordParser(
                path_to_jar = PATH_TO_JAR,
                path_to_models_jar = PATH_TO_MODELS_JAR,
                java_options=JAVA_OPTIONS)
    return STANDFORD["parser"]

# scipy parser singleton
PARSERS = dict()

def get_parser(language=LANGUAGE):
    # load the sentence parser for the target language
    if language not in PARSERS.keys():
        PARSERS[language] = spacy.load(SCIPY_LANGUAGES[language])
    return PARSERS[language]

def parse(text, language=LANGUAGE):
    return get_parser(language)(text)

def load_and_remove_punct(file_name: str, sentence_per_line=True):
    # load file and split into sentences
    with open(file_name) as f:
        if sentence_per_line:
            sentences = f.read().strip().split('\n')
        else:
            sentences = [sent for sent in parse(f.read()).sents]

    # remove punctuation from every sentence
    sentences = [sent.strip().translate(PUNCT_REMOVER).strip() for sent in sentences]
    sentences = [sent for sent in sentences if sent]

    return sentences

def get_tokens(sent_parsed):
    return [str(token) for token in sent_parsed]
def get_ner(sent_parsed):
    return [(ent.text, ent.label_) for ent in sent_parsed.ents if ent.label_ in NER_ACCEPTED_LABELS]
def get_pos(sent_parsed):
    return [token.pos_ for token in sent_parsed]

#task 6: Apply syntactic parser bu using StanfordParser
def get_syntax(sent: str):
    parse_trees = list(get_standford().raw_parse(sent))
    return parse_trees[0]._pformat_flat(nodesep=":", parens='()', quotes=True)

def save_json(data, file_name):
    # dump data to file
    with open(file_name, 'w') as f:
        f.write(json.dumps(data))

def load_json(file_name):
    # load data from json file
    with open(file_name, 'r') as f:
        data = json.loads(f.read())

    return data

def process_file(file_name: str, target_file_prefix: str=None, save_to_file=True):
    # automatic target_file_prefix: source file name without extension
    if not target_file_prefix:
        target_file_prefix = file_name.replace(".txt", '')

    # read file, parse sentences and remove ponctuation
    sentences = load_and_remove_punct(file_name)

    # dictionary of results per task, each result is a dictionary of result per sentence
    task_results = {
        TASK_SENTENCE: dict(),
        TASK_TOKENIZE: dict(),
        TASK_NER: dict(),
        TASK_POS: dict(),
        TASK_SYNTAX: dict()
    }

    # process every sentence
    for sent_id, sent in enumerate(sentences):
        # run SciPy parser to get tokens, NEs, and POS
        parsed_sent = parse(sent)
        tokens, ner, pos = get_tokens(parsed_sent), get_ner(parsed_sent), get_pos(parsed_sent)

        # run Stanford syntactic parser
        syntax = get_syntax(sent)

        # add the result of each task to the result dictionnary
        task_results[TASK_SENTENCE][sent_id] = sent
        task_results[TASK_TOKENIZE][sent_id] = tokens
        task_results[TASK_NER][sent_id] = ner
        task_results[TASK_POS][sent_id] = pos
        task_results[TASK_SYNTAX][sent_id] = syntax

    # write the results of each task to the corresponding the files
    if save_to_file:
        for task, task_file in TASK_FILES.items():
            # prepare output file name
            out_file_name = TASK_FILENAME_SCHEME.format(task=task_file, prefix=target_file_prefix)

            # write data to file
            save_json(task_results[task], out_file_name)

    return task_results
        

if __name__=="__main__":
    # import management tools for data from lab 1
    try:
        from ..lab_1.data_management import load_csv, CSV_FILE_PATH, CSV_HEADERS
    except ValueError:
        import sys, inspect
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        sys.path.insert(0, parent_dir) 
        from lab_1.data_management import load_csv, CSV_FILE_PATH, CSV_HEADERS

    # load books from csv
    source_root = os.path.join("..", "lab_1")

    print("data path", os.path.join(source_root, CSV_FILE_PATH))
    df = load_csv(os.path.join(source_root, CSV_FILE_PATH))

    for book_uri, book_file in zip(df[CSV_HEADERS[1]], df[CSV_HEADERS[3]]):
        print("processing", book_uri)
        process_file(os.path.join(source_root, book_file), os.path.join(SAVE_PATH, book_uri.split('/')[-1]))