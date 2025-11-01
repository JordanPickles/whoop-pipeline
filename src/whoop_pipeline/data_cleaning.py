import pandas as pd
from sqlalchemy import Integer, BigInteger, Float, Numeric, DateTime, String, Boolean

class WhoopDataCleaner():
    
    def classify_sqla_type(self, col_type):
        """Classifies SQLAlchemy column types into simple categories."""
        if isinstance(col_type, (DateTime,)):
            return "datetime"
        if isinstance(col_type, (BigInteger, Integer,)):
            return "integer"
        if isinstance(col_type, (Float, Numeric,)):
            return "float"
        if isinstance(col_type, (Boolean,)):
            return "boolean"
        if isinstance(col_type, (String,)):
            return "string"
        return "other"
    
    def columns_by_type(self, model_class) -> dict:
        """
        Returns a dict of column names grouped by simple types
        using the SQLAlchemy model as source of truth.
        """
        column_data_types = {"datetime": [], "integer": [], "float": [], "boolean": [], "string": [], "other": []}
        for col in model_class.__table__.columns:
            label = self.classify_sqla_type(col.type)
            column_data_types[label].append(col.name)
        return column_data_types

    
    def split_column_names(self, df:pd.DataFrame, endpoint:str) -> pd.DataFrame:
        """Splits column names on '.' and keeps the last part."""
        if endpoint == 'activity/sleep':
            df.columns = df.columns.str.replace('sleep_needed.', 'sleep_needed_', regex=False) # specific to sleep_needed columns

        df.columns = df.columns.str.split('.').str[-1]
        return df
    
    def coerce_datetime(self, df:pd.DataFrame, columns:list) -> pd.DataFrame:
        """Converts specified columns to datetime."""

        for col in columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        return df
    
    def coerce_integer(self, df:pd.DataFrame, columns:list) -> pd.DataFrame:
        """Converts specified columns to integer."""
        for col in columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
        return df
    
    def coerce_float(self, df:pd.DataFrame, columns:list) -> pd.DataFrame:
        """Converts specified columns to float."""
        for col in columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)
        return df
    
    def coerce_string(self, df:pd.DataFrame, columns:list) -> pd.DataFrame:
        """Converts specified columns to string."""
        for col in columns:
            if col in df.columns:
                df[col] = df[col].astype(str)
        return df

    def coerce_boolean(self, df:pd.DataFrame, columns:list) -> pd.DataFrame:
        """Converts specified columns to boolean."""
        for col in columns:
            if col in df.columns:
                df[col] = df[col].astype(bool)
        return df
    
    def tz_offset_to_minutes(self, offset_str):
        if pd.isna(offset_str):
            return 0
        elif isinstance(offset_str, str) and (offset_str.startswith('+') or offset_str.startswith('-')):
            sign = 1 if offset_str[0] == '+' else -1
            try:
                hours, minutes = map(int, offset_str[1:].split(':'))
                return sign * (hours * 60 + minutes)
            except Exception:
                return 0
        else:
            return 0
        
    def rename_id_column(self, df:pd.DataFrame, endpoint:str) -> pd.DataFrame:
        """Renames 'id' column to '{endpoint}_id'."""
        if 'id' in df.columns:
            df = df.rename(columns={'id': f"{endpoint.split('/')[-1]}_id"}) # gets last part of endpoint for id renaming
        return df
    
    def clean_data(self, df:pd.DataFrame, endpoint:str, model_class) -> pd.DataFrame:
        """Cleans data based on the specified data type."""        

        if 'timezone_offset' in df.columns:
            df['timezone_offset'] = df['timezone_offset'].apply(self.tz_offset_to_minutes)

        df = self.split_column_names(df, endpoint)
        df = self.rename_id_column(df, endpoint) 
        

        col_types = self.columns_by_type(model_class)

        df = self.coerce_datetime(df, col_types['datetime'])
        df = self.coerce_integer(df, col_types['integer'])
        df = self.coerce_float(df, col_types['float'])
        df = self.coerce_string(df, col_types['string'])
        df = self.coerce_boolean(df, col_types['boolean'])

        return df
    
if __name__ == '__main__':
    cleaner = WhoopDataCleaner()
    schema = cleaner.classify_sqla_type('workout')
    col_types = cleaner.columns_by_type(schema)
    print(col_types)