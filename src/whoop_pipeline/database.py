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


    def get_max_date(self):
  
        
        max_date = pd.read_sql("SELECT MAX(created_at) as max_date FROM fact_cycle", con=self.engine)

        return max_date['max_date'][0]
    
if __name__ == "__main__":
    whoop_db = WhoopDB()
    print(whoop_db.get_max_date())