from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import insert
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
        self.db_url = settings.db_url
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

    def get_access_token_table(self):
        """Creates the access_tokens table if it doesn't exist."""
        metadata = MetaData()
        return Table("access_tokens", metadata, autoload_with=self.engine)

    def upsert_access_token(self, tokens:Dict, provider: str = "whoop"):
        """Upserts the access token into the access_tokens table.""" 
        
        tokens_updated = {"provider": provider, **tokens} # Adds the provider field and follows that with the tokens dict passed into the function
        
        tokens_updated["expires_at"]  = int(time.time()) + int(tokens.get("expires_in", 0)) - 10
        
        print(tokens_updated.items())
        access_token_table = self.get_access_token_table()
        print(access_token_table.columns)
        
        statement = insert(access_token_table).values(tokens_updated)

        upsert_statement = statement.on_conflict_do_update(
            index_elements= ['provider'], # Primary Key Column name
            set_={c: statement.excluded[c] for c in tokens_updated.keys() if c != "provider"} # Updates all columns except primary key
        )

        session = self.get_session()
        session = session()
        try:
            session.execute(upsert_statement)
            session.commit()
            print(f"Upserted access token for {provider}.")
        except Exception as e:
            session.rollback()
            print(f"Error upserting access token for {provider}: {e}")

    def get_access_token(self, provider: str = "whoop") -> Dict:
        """Fetches the access token from the access_tokens table."""
        connection = self.engine.connect()
        token_data = pd.read_sql(text("SELECT * FROM ACCESS_TOKENS"), con=connection)
        
        if not token_data.empty:
            return token_data.iloc[0].to_dict() # convert first row to dict
        else:
            return {}

    def get_max_date(self):
        """Fetches the maximum created_at date from the fact_cycle table."""    
        connection = self.engine.connect()
        max_date = pd.read_sql(text("SELECT MAX(created_at) as max_date FROM fact_cycle"), con=connection)
        return max_date['max_date'][0]
    

if __name__ == "__main__":
    whoop_db = WhoopDB()
    print(whoop_db.get_max_date())