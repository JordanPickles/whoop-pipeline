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

    def teardown_method(self, method):
        self.transaction.rollback()
        self.connection.close()

    def test_upsert_data(self):
        
        self.db.upsert_access_token(tokens=self.test_tokens, provider="whoop", session=self.session)
        token_data = self.db.get_access_token(connection=self.connection)

        assert token_data["access_token"] == self.test_tokens["access_token"]
        assert token_data["refresh_token"] == self.test_tokens["refresh_token"]
        assert token_data["expires_in"] == self.test_tokens["expires_in"]
 





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


    
