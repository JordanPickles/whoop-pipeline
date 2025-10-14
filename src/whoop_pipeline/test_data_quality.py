
import numpy as np
import pandas as pd
from numpy import nan
from datetime import date, datetime

class DataValidationTests():
    
    
    def assert_no_null(self, df:pd.DataFrame, pk_column_name:str):
        """Test that the primary key column has unique values."""
        if df[pk_column_name].isnull().any():
            raise AssertionError("Primary key column contains null values.")
        
    def assert_unique_pk(self, df:pd.DataFrame, pk_column_name:str):
        """Test that the primary key column has unique values."""
        if not df[pk_column_name].is_unique: 
            raise AssertionError("Primary key column has duplicate values.")

    def assert_columns_exist(self, df:pd.DataFrame, expected_columns:list):
        """Test that all expected columns are present in the DataFrame."""
        missing_columns = set(expected_columns) - set(df.columns) # set returns unique values
        if missing_columns:
            raise AssertionError(f"Missing columns: {missing_columns}")

    def assert_column_types(self, df:pd.DataFrame, column_types:dict):
        """Test that columns have the expected data types."""
        for col, expected_type in column_types.items():
            if col in df.columns:
                actual_type = df[col].dtype
                if actual_type != expected_type:
                    raise AssertionError(f"Column '{col}' has type {actual_type}, expected {expected_type}")


    def assert_strain_range(self, df:pd.DataFrame, min_value:float=0, max_value:float=21.0):
        """Test that the strain column values are within the expected range."""
        if 'strain' in df.columns:
            if not df['strain'].between(min_value, max_value).all():
                raise AssertionError(f"Strain values are out of range ({min_value}, {max_value}) for activity starting {df.get('start_time')}")
        
    def assert_recovery_score_range(self, df:pd.DataFrame, min_value:int=0, max_value:int=100):
        """Test that the recovery_score column values are within the expected range."""
        if 'recovery_score' in df.columns:
            if not df['recovery_score'].between(min_value, max_value).all():
                raise AssertionError(f"Recovery score values are out of range ({min_value}, {max_value} on {df.get('date')})")
    

    def assertion_tests(self, df:pd.DataFrame, model_class):
        """Runs all validation tests on the DataFrame."""
        pk_column_name = model_class.__table__.primary_key.columns.keys()[0]
        expected_columns = [col.name for col in model_class.__table__.columns]
        column_types = {col.name: str(col.type) for col in model_class.__table__.columns}

        type_annotation_map={
            'INTEGER': 'Int64',
            'VARCHAR': 'object',
            'FLOAT': 'float64',
            'DATE': 'Date',
            'TIMESTAMP': 'datetime64[ns, UTC]',
        }
        column_types = {k: type_annotation_map.get(v, 'other') for k, v in column_types.items()} # dict comprehension to replace the column type with python data types instead of the postgres types



        self.assert_no_null(df, pk_column_name)
        self.assert_unique_pk(df, pk_column_name)
        self.assert_columns_exist(df, expected_columns)
        self.assert_column_types(df, column_types)
        self.assert_strain_range(df)
        self.assert_recovery_score_range(df)

        return True