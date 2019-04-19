import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))                               # database engine object from SQLAlchemy that manages connections to the database
                                                                                # DATABASE_URL is an environment variable that indicates where the database lives
db = scoped_session(sessionmaker(bind=engine))                                  # create a 'scoped session' that ensures different users' interactions with the
                                                                                # database are kept separate

def main():

    # Create a table for users
    # table = db.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR NOT NULL, hash VARCHAR NOT NULL)")

    # Create a table for reviews
    reviews = db.execute("CREATE TABLE reviews (id SERIAL PRIMARY KEY, username VARCHAR NOT NULL, isbn VARCHAR NOT NULL, content VARCHAR NOT NULL, rating INTEGER NOT NULL)")

    db.commit()


if __name__ == '__main__':
    main()
