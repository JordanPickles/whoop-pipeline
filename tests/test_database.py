from whoop_pipeline.database import WhoopDB
from whoop_pipeline.models import Sleep
import pandas as pd
import pytest
from pytest_mock import mocker
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker
from whoop_pipeline.config import settings 
import datetime
import whoop_pipeline.models as WhoopModels
from sqlalchemy import text

class TestWhoopDB():
    def setup_method(self, method):
        self.db_url = settings.db_url
        self.engine = create_engine(self.db_url)
        
        self.connection = self.engine.connect()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.connection)
        self.session = self.SessionLocal()
        self.transaction = self.connection.begin()

        self.db = WhoopDB()
   
        self.test_tokens = {
            "provider": "whoop",
            "access_token": "test_access_token",
            "expires_in": 3600,
            "scope": "read write",
            "token_type": "Bearer",
            "refresh_token": "test_refresh_token",
        }
        self.test_data = {
            "cycle_id": 123,
            "user_id": 234,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
            "start": datetime.datetime.now(),
            "end": datetime.datetime.now(),
            "timezone_offset": 60,
            "score_state": "TEST",
            "kilojoule": 1000.00,
            "average_heart_rate": 50,
            "max_heart_rate": 150

        }
        
    def teardown_method(self, method):
        self.transaction.rollback()
        self.connection.close()

    def test_upsert_access_token(self):

        self.db.upsert_access_token(tokens=self.test_tokens, provider="whoop", session=self.session)
        token_data = self.db.get_access_token(connection=self.connection)
        assert token_data["access_token"] == self.test_tokens["access_token"]
        assert token_data["refresh_token"] == self.test_tokens["refresh_token"]
        assert token_data["expires_in"] == self.test_tokens["expires_in"]
 

    def test_upsert_data(self):
        
        table = WhoopModels.Cycle.__table__
        primary_key = [key.name for key in table.primary_key.columns]
        table_cols = [col.name for col in table.columns]
        
        self.db.upsert_data(table, primary_key=primary_key, table_cols=table_cols, rows=self.test_data, session=self.session)
        data = pd.read_sql(text("SELECT * FROM FACT_CYCLE WHERE CYCLE_ID=123"), con=self.connection)
        print(data["cycle_id"].iloc[0])
        assert data["cycle_id"].iloc[0] == self.test_data["cycle_id"]
        assert data["timezone_offset"].iloc[0] == self.test_data["timezone_offset"]
        assert data["score_state"].iloc[0] == self.test_data["score_state"]



    def test_get_model_class_data(self):
        sleep_model = Sleep()
        table, primary_key, table_cols = self.db.get_model_class_data(model_class=sleep_model.__class__)

        assert table.name != None
        assert primary_key != None
        assert len(table_cols) > 0


    def test_get_max_date(self):
        max_date = self.db.get_max_date(self.connection)

        assert max_date != None
        assert isinstance(max_date, pd.Timestamp)

    def test_get_access_token(self):
        db = WhoopDB()
        token_data = self.db.get_access_token(self.connection)

        assert isinstance(token_data, dict)


    
