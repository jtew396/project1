import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv(""))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:    # Loop gives each column a name
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",{"isbn":isbn, "title":title, "author":author, "year":year}) # Substitute values from the CSV line into SQL command, as per books.CSV
    db.commit()


if __name__ == '__main__':
    main()
