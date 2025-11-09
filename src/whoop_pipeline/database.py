from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.pool import NullPool
from whoop_pipeline.models import Base, Sleep, Recovery, Cycle, Workout
from sqlalchemy.orm import sessionmaker
from whoop_pipeline.config import settings 
import os
import pandas as pd
import datetime as dt
from typing import Dict, List
import psycopg2
from sqlalchemy import text
import time
from datetime import date, timedelta, datetime as dt

class WhoopDB():
    def __init__(self):
        self.db_url = f"{settings.db_url}?sslmode=require"
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine, future=True)
        # self.session = self.SessionLocal()
        # self.connection = self.engine.connect()

    def create_tables(self):
        """Creates database tables based on the defined models if they don't already exist."""
        Base.metadata.create_all(bind=self.engine)

    
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

    def upsert_data(self, table, primary_key:list, table_cols:list, rows:dict, session=None):
        """Upserts data into the specified table. Checks for existing records based on primary key(s) and updates them if they exist, otherwise inserts new records."""

        if not rows:
            return None  # nothing matches table columns
        
        table_name = table.name

        statement = insert(table).values(rows) # Create an insert statement with the data
        
        updatable = [c for c in table_cols if c not in primary_key] # All columns except primary keys as that will remain the same
        
        # Create the upsert statement. This replaces any existing data records with the new data or just adds them should they not already exist. Effectively Updating or Inserting.
        upsert_statement = statement.on_conflict_do_update(
            index_elements= primary_key, # Primary Key Column name
            set_={c: statement.excluded[c] for c in updatable} # Updates all columns from rows except primary key
        )
        
        
        if session is None: # For the production pipeline using a temporary session which can be run in docker container without pooler connection issues
            with self.SessionLocal() as s:
                try:
                    s.execute(upsert_statement)
                    s.commit()
                    print(f"Upserted {len(rows)} records into {table_name}.")
                except Exception as e:
                    s.rollback()
                    print(f"Error upserting data into {table_name}: {e}")
        else: #This section is for tests where the db upsert needs rolling back and uses the test session
            try:
                session.execute(upsert_statement)
                session.flush
            except Exception as e:
                session.rollback()
                

    def get_access_token_table(self):
        """Creates the access_tokens table if it doesn't exist."""
        metadata = MetaData()
        return Table("access_tokens", metadata, autoload_with=self.engine)

    def upsert_access_token(self, tokens:Dict, provider: str = "whoop", session=None):
        """Upserts the access token into the access_tokens table.""" 
        
        tokens_updated = {"provider": provider, **tokens} # Adds the provider field and follows that with the tokens dict passed into the function
        tokens_updated["expires_at"]  = int(time.time()) + int(tokens.get("expires_in", 0)) - 10
        access_token_table = self.get_access_token_table()
        
        updatable = [c for c in tokens_updated.keys() if c not in 'provider']

        statement = insert(access_token_table).values(tokens_updated)
        upsert_statement = statement.on_conflict_do_update(
            index_elements= ['provider'], # Primary Key Column name
            set_={c: statement.excluded[c] for c in updatable} # Updates all columns except primary key
        )

        if session is None: # For the production pipeline using a temporary session which can be run in docker container without pooler connection issues
            with self.SessionLocal() as s:
                try:
                    s.execute(upsert_statement)
                    s.commit()
                    print(f"Upserted 1 record into {'access_tokens'}.")
                except Exception as e:
                    s.rollback()
                    print(f"Error upserting 1 record into {'access_tokens'}.")
        else: #This section is for tests where the db upsert needs rolling back and uses the test session
            try:
                session.execute(upsert_statement)
                session.flush
            except Exception as e:
                session.rollback()


    def get_access_token(self, connection=None) -> Dict:
        """Fetches the access token from the access_tokens table."""
        if connection == None:
            with self.engine.begin() as conn:
                token_data = pd.read_sql(text("SELECT * FROM ACCESS_TOKENS"), con=conn)
        else:
            token_data = pd.read_sql(text("SELECT * FROM ACCESS_TOKENS"), con=connection)
        
        if not token_data.empty:
            return token_data.iloc[0].to_dict() # convert first row to dict
        else:
            return {}

    def get_max_date(self, connection=None):
        """Fetches the maximum created_at date from the fact_cycle table."""    
        if connection == None:
            with self.engine.begin() as conn: # For the production pipeline using a temporary session which can be run in docker container without pooler connection issues
                max_date = pd.read_sql(text("SELECT MAX(created_at) as max_date FROM fact_cycle"), con=conn)
        else:
            max_date = pd.read_sql(text("SELECT MAX(created_at) as max_date FROM fact_cycle"), con=connection)
        return max_date['max_date'][0]
    

if __name__ == "__main__":
    whoop_db = WhoopDB()
    print(whoop_db.get_max_date())