from .exercise_1 import CSV_HEADERS
from .exercise_3 import DB_PATH, CSV_FILE_PATH, load, sessionmaker, create_engine, Author, Book, Abstract, Movement, AuthorMovementMapping
from sqlalchemy.orm import Session
from pandas import DataFrame, read_csv


def load_database(db_path = DB_PATH, read_only=True, quiet=False) -> Session:
    # Create an engine that stores data in the local 
    # directory's example.db file.
    engine = create_engine('sqlite:///' + db_path)
    session = sessionmaker(bind=engine, autocommit=False)()

    # overwrite flush method if in read only mode
    if read_only:
        session.flush = (lambda: None) if quiet else (lambda: print("Database '{}' loaded in read only mode".format(db_path))) # now it won't flush!

    return session
    
def load_csv(csv_path=CSV_FILE_PATH) -> DataFrame:
    return read_csv(csv_path, index_col=0)