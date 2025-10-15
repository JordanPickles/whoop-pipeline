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
        print(self.db_url)
        self.engine = create_engine(self.db_url)

    def create_tables(self):
        """Creates database tables based on the defined models if they don't already exist."""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        """Creates a new database session."""
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        return  SessionLocal
    
    def get_model_class_data(self, model_class):
        """Returns the table, primary key(s) and column names for a given SQLAlchemy model class."""
        table = model_class.__table__
        primary_key = [key.name for key in table.primary_key.columns]
        table_cols = [col.name for col in table.columns]
        return table, primary_key, table_cols
    
    def process_dataframe(self, df:pd.DataFrame, table_cols:list) -> list:
        """Processes the DataFrame to match the database table schema."""

        df = df[table_cols] # Keep only columns that exist in the table
        df = df.where(df.notna(), None) # Replace pandas NaN with None for SQL compatibility
        rows = df.to_dict(orient='records') # Convert DataFrame to list of dictionaries for upserting to database

        return rows
    
    def upsert_data(self, df:pd.DataFrame, model_class, table_name:str):

        """Upserts data into the specified table. Checks for existing records based on primary key(s) and updates them if they exist, otherwise inserts new records."""

        if df is None or df.empty:
            return None
        
        table, primary_key, table_cols = self.get_model_class_data(model_class)
        rows = self.process_dataframe(df, table_cols)

        if not rows:
            return None  # nothing matches table columns
         
        statement = insert(table).values(rows) # Create an insert statement with the data
        
        updatable = [c for c in table_cols if c not in primary_key] # All columns except primary keys as that will remain the same
        
        # Create the upsert statement. This replaces any existing data records with the new data or just adds them should they not already exist. Effectively Updating or Inserting.
        upsert_statement = statement.on_conflict_do_update(
            index_elements= primary_key, # Primary Key Column name
            set_={c: statement.excluded[c] for c in updatable} # Updates all columns from rows except primary key
        )
        
        session = self.get_session()
        session = session()
        try:
            session.execute(upsert_statement)
            session.commit()
            print(f"Upserted {len(rows)} records into {table_name}.")
        except Exception as e:
            session.rollback()
            print(f"Error upserting data into {table_name}: {e}")


        

    def get_max_date(self):
        """Fetches the maximum created_at date from the fact_cycle table."""    
        max_date = pd.read_sql("SELECT MAX(created_at) as max_date FROM fact_cycle", con=self.engine)
        return max_date['max_date'][0]
    

if __name__ == "__main__":
    whoop_db = WhoopDB()
    print(whoop_db.get_max_date())