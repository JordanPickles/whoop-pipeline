from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from whoop_pipeline.models import Base
from sqlalchemy.orm import sessionmaker
from whoop_pipeline.config import settings 
import os
import pandas as pd
import datetime as dt


class WhoopDB():
    def __init__(self):
        self.db_url = settings.db_url
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        return self.SessionLocal()
    
    def upsert_data(self, df:pd.DataFrame , table_name:str):
        df.to_sql(table_name, con=self.engine, if_exists='append', index=False)


    # def get_max_date(self):
    #     """
    #     Retrieves the maximum date from the dim_match table.
    #     Returns:
    #         datetime: The maximum date found in the dim_match table.
    #         If no date is found, returns datetime(1900, 1, 1).
    #         If an error occurs, returns 0."""
        
    #     if not self.connection:
    #         return None
    #     try:
    #         cursor = self.connection.cursor()
    #         query = sql.SQL("SELECT MAX(datetime) FROM dim_match") # Gets the max date from the database table
    #         cursor.execute(query)
    #         max_date = cursor.fetchone()[0]
    #         cursor.close()
    #         if max_date == None or max_date == 0:
    #             return datetime(1900, 1, 1) # Returns a date should no date be found: e.g. the first time the code is run so that the rest of the code can stil run returning all matches
    #         return max_date
    #     except Exception as e:
    #         print(f"Error executing query: {e}")
    #         return 0
    
if __name__ == "__main__":
    whoop_db = WhoopDB()
    whoop_db.create_tables()