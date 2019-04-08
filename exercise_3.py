# --- imports ---
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, func

Base = declarative_base() 

import pandas as pd

from exercise_1 import CSV_FILE_PATH, SAVE_PATH, os
from exercise_2 import exercise_2

# --- constants ---
VERBOSE=False
DB_PATH = os.path.join(SAVE_PATH, "book_catalogue.db")

# --- alchemy ---
# setup SQL database

class Author(Base):
    __tablename__ = 'author'
    id   = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    uri  = Column(String(250))
    books             = relationship("Book", back_populates="author")
    abstracts         = relationship("Abstract", back_populates="author")
    movement_mappings = relationship("AuthorMovementMapping", back_populates="author")

class Book(Base):
    __tablename__ = 'book'
    uri             = Column(String(250), primary_key=True)
    author_id       = Column(Integer, ForeignKey('author.id'))
    title           = Column(String(250))
    file_path       = Column(String(250))
    sentence_number = Column(Integer)
    author = relationship("Author", back_populates="books")

class Abstract(Base):
    __tablename__ = 'abstract'
    author_id = Column(Integer, ForeignKey('author.id'), primary_key=True)
    lang      = Column(String(4), primary_key=True)
    abstract  = Column(String(250))
    author = relationship("Author", back_populates="abstracts")

class Movement(Base):
    __tablename__ = 'movement'
    id    = Column(Integer, primary_key=True)
    uri   = Column(String(250), nullable=False)
    label = Column(String(250), nullable=False)
    author_mappings = relationship("AuthorMovementMapping", back_populates="movement")

class AuthorMovementMapping(Base):
    __tablename__ = 'author_movement_mapping'
    author_id   = Column(Integer, ForeignKey('author.id'), primary_key=True)
    movement_id = Column(Integer, ForeignKey('movement.id'), primary_key=True)    
    author   = relationship("Author", back_populates="movement_mappings")
    movement = relationship("Movement", back_populates="author_mappings")

# --- code ---

def count_sentences(book_file):
    with open(book_file) as f:
        return len(f.read().strip().split('\n'))
    
# load the data from exetcise 1
def load(csv_file):
    df = pd.read_csv(csv_file, index_col=0)
    
    df["sentence_number"] = df["book_file"].apply(count_sentences)
    return df

# initialize SQL database
def author_and_book_to_database(csv_file_name, session):
    df = load(csv_file_name)
    
    # Bind the engine to the metadata of the Base 
    # class from base.py 

    # initialize the singleton of movements with the movements already in the database
    authors={author.name: author for author in session.query(Author)}
    def get_author(author_name): # Singleton of each author
        if author_name not in authors.keys():
            authors[author_name] = Author(name=author_name)
            session.add(authors[author_name])
        return authors[author_name]
    
    for author, book_url, book_title, book_file, sentence_number in df.itertuples(index=False):
        book = Book(uri=book_url,
                    title=book_title,
                    file_path=book_file,
                    sentence_number=sentence_number,
                    author=get_author(author))
        session.add(book)
        
    return authors

# get the data from exercise 2 for every author of exercise 1
# (by loading from the database) and add it to the database
def apply_exercise_2(authors, session, verbose=VERBOSE):
    
    # initialize the singleton of movements with the movements already in the database
    movements={movement.uri: movement for movement in session.query(Movement)}
    def get_movement(movement_uri, movement_name): # Singleton of each movement
        if movement_uri not in movements.keys():
            movements[movement_uri] = Movement(uri=movement_uri, label=movement_name)
            session.add(movements[movement_uri])
        return movements[movement_uri]
    
    for author_name, author_object in authors.items():
        author_uri, abstracts, movements = exercise_2(author_name, verbose=verbose)
    
        if author_uri:
            author_object.uri = author_uri
            
            author_object.abstracts = [
                Abstract(lang = lang,
                         abstract = abstract)
                for lang, abstract in abstracts.items()
            ]
            
            author_movements = [get_movement(movement_uri, movement_name)
                                for movement_uri, movement_name in movements.items()]
            
            author_object.movement_mappings = [
                AuthorMovementMapping(movement=movement)
                for movement in author_movements
            ]
            


# --- main ---
if __name__ == "__main__":
    mode = 'test' #'populate'

    if mode == 'populate':
        # Create an engine that stores data in the local 
        # directory's example.db file.
        engine = create_engine('sqlite:///' + DB_PATH)

        # Create all tables in the engine. This is equivalent 
        # to "Create Table" statements in raw SQL.
        Base.metadata.create_all(engine)
        
        # use engine to run the two main functions
        Base.metadata.bind = engine
        session = sessionmaker(bind=engine)()
        authors = author_and_book_to_database(CSV_FILE_PATH, session)
        apply_exercise_2(authors, session)
        session.commit()

    else:
        # Create an engine that stores data in the local 
        # directory's example.db file.
        engine = create_engine('sqlite:///' + DB_PATH)
        session = sessionmaker(bind=engine)()

        # Example query 1
        author='Zangwill, Israel, 1864-1926'
        print("Retrieve all book title for a given author ({})".format(author))
        for book, in session.query(Book.title).join(Author).filter_by(name=author):
            print(book)

        print("Retrieve all book title for all authors")
        for author, book, in session.query(Author.name, Book.title).join(Book):
            print(author, ':', book)
        
        # Example query 2
        print("Retrieve the author list ordered in lexicographic ordering")
        for author, in session.query(Author.name).order_by(Author.name):
            print(author)

        # Example query 3
        print("Retrieve the number of book per author")
        for count, author, in session.query(func.count(Book.author_id), Author.name).join(Author).group_by(Author.name):
            print(author, ':', count)

        # Example query 4
        print("Retrieve all book files for a given author ({})".format(author))
        for book, in session.query(Book.file_path).join(Author).filter_by(name=author):
            print(book)