
import numpy as np
import pandas as pd
import pytest
from numpy import nan

class DataValidationTests():
    
    
    def test_null_check(self, df:pd.DataFrame, pk_column_name:str):
        """Test that the primary key column has unique values."""
        assert np.where(df[pk_column_name].isnull()), "Primary key column has null values."

    def test_unique_pk(self, df:pd.DataFrame, pk_column_name:str):
        """Test that the primary key column has unique values."""
        assert df[pk_column_name].is_unique, "Primary key column has duplicate values."

    def test_columns_exist(self, df:pd.DataFrame, expected_columns:list):
        """Test that all expected columns are present in the DataFrame."""
        missing_columns = [col for col in expected_columns if col not in df.columns]
        assert not missing_columns, f"Missing columns: {missing_columns}"

    def test_column_types(self, df:pd.DataFrame, column_types:dict):
        """Test that columns have the expected data types."""
        for col, expected_type in column_types.items():
            if col in df.columns:
                actual_type = df[col].dtype
                assert actual_type == expected_type, f"Column '{col}' has type {actual_type}, expected {expected_type}"

    def test_strain_range(self, df:pd.DataFrame, min_value:float=0, max_value:float=21.0):
        """Test that the strain column values are within the expected range."""
        if 'strain' in df.columns:
            assert df['strain'].between(min_value, max_value).all(), f"Values in column Strain are out of range ({min_value}, {max_value})"
        
    def test_recovery_score_range(self, df:pd.DataFrame, min_value:int=0, max_value:int=100):
        """Test that the recovery_score column values are within the expected range."""
        if 'recovery_score' in df.columns:
            assert df['recovery_score'].between(min_value, max_value).all(), f"Values in column recovery_score are out of range ({min_value}, {max_value})"



    def run_tests(self, df:pd.DataFrame, pk_column_name:str, expected_columns:list, column_types:dict):
        """Runs all validation tests on the DataFrame."""
        self.test_null_check(df, pk_column_name)
        self.test_unique_pk(df, pk_column_name)
        self.test_columns_exist(df, expected_columns)
        self.test_column_types(df, column_types)
        self.test_strain_range(df)
        self.test_recovery_score_range(df)