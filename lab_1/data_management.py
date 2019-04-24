from .exercise_3 import DB_PATH, CSV_FILE_PATH, load, sessionmaker, create_engine, Author, Book, Abstract, Movement, AuthorMovementMapping
from pandas import DataFrame


def load_database(db_path = DB_PATH, read_only=True):
    # Create an engine that stores data in the local 
    # directory's example.db file.
    engine = create_engine('sqlite:///' + db_path)
    session = sessionmaker(bind=engine, autocommit=False)()

    # overwrite flush method if in read only mode
    if read_only:
        session.flush = lambda: print("Database '{}' loaded in read only mode".format(db_path))   # now it won't flush!

    return session
    
def load_csv(csv_path=CSV_FILE_PATH) -> DataFrame:
    return load(csv_path)