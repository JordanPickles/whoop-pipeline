from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import insert
from whoop_pipeline.models import Base, Sleep, Recovery, Cycle, Workout
from sqlalchemy.orm import sessionmaker
from whoop_pipeline.config import settings 
import os
import pandas as pd
import datetime as dt
from typing import Dict, List

class WhoopDB():
    def __init__(self):
        self.db_url = settings.db_url
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        """Creates database tables based on the defined models if they don't already exist."""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        return self.SessionLocal()
    
    def upsert_data(self, df:pd.DataFrame , table_name:str):

        """Upserts data into the specified table. Checks for existing records based on primary key(s) and updates them if they exist, otherwise inserts new records."""

        # Returns a dict of table models
        if df is None or df.empty:
            return None

        tables = {
            'fact_cycle': Cycle.__table__,
            'fact_activity_sleep': Sleep.__table__,
            'fact_recovery': Recovery.__table__,
            'fact_workout': Workout.__table__
        }

        primary_keys = {
            'fact_cycle': ['cycle_id'],
            'fact_activity_sleep': ['sleep_id'],
            'fact_recovery': ['sleep_id'],
            'fact_workout': ['workout_id']
        }

        table = tables[table_name] #returns the table model
        table_cols = {c.name for c in table.columns} # list of columns in the dataframe
        
        rows = [{k: v for k, v in r.items() if k in table_cols}
            for r in df.to_dict(orient='records')]

        if not rows:
            return None  # nothing matches table columns
        
        

         # Create an insert statement with the data
        statement = insert(table).values(rows)
        
        updatable = [c for c in table_cols if c not in primary_keys[table_name]]

        # Create the upsert (insert or update) statement. This replaces any existing data records with the new data
        upsert_statement = statement.on_conflict_do_update(
            index_elements= primary_keys[table_name], # Primary Key Column names
            set_={c: statement.excluded[c] for c in updatable} # Updates all columns from row except primary
        )
        with self.engine.begin() as conn:
            conn.execute(upsert_statement)

        

    def get_max_date(self):
        """Fetches the maximum created_at date from the fact_cycle table."""    
        max_date = pd.read_sql("SELECT MAX(created_at) as max_date FROM fact_cycle", con=self.engine)
        return max_date['max_date'][0]
    

if __name__ == "__main__":
    whoop_db = WhoopDB()
    print(whoop_db.get_max_date())