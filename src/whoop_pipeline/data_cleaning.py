import pandas as pd


class WhoopDataCleaner():
    def clean_sleep_data(self, df:pd.DataFrame) -> pd.DataFrame:
        """Cleans the sleep data DataFrame."""
 
        df.columns = df.columns.str.split('score.').str[-1] 
        df.columns = df.columns.str.split('stage_summary.').str[-1] 
        df.columns = df.columns.str.replace('.', '_', regex=False)
  
        # Convert date columns to datetime
        datetime_columns = ['created_at', 'updated_at', 'start', 'end']
        for col in datetime_columns: # Converts all date columns to datetime
            df[col] = pd.to_datetime(df[col])

        df['timezone_offset'] = df['timezone_offset'].apply(self.tz_offset_to_minutes)
        
        int_cols = [col for col in df.columns if col.endswith("milli") or col.endswith("count") or col.endswith("_id")] # lists all columns ending with milli to be converted to in
        for col in int_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        float_columns = [col for col in df.columns if col.endswith("percentage") or col.endswith("rate")]
        for col in float_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float) 
            if col.endswith("percentage"): #converts all percentages to a decimal
                df[col] = df[col] / 100

        df = df.rename(columns={'id':'sleep_id'})
        df['sleep_id'] = df['sleep_id'].astype(str)
        
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

    
    def clean_recovery_data(self, df:pd.DataFrame) -> pd.DataFrame:
        """Cleans the recovery data DataFrame."""
        df.columns = df.columns.str.split('score.').str[-1] # Keeps everything after score.

        # Convert date columns to datetime
        datetime_columns = ['created_at', 'updated_at']
        for col in datetime_columns:
            df[col] = pd.to_datetime(df[col])
        
        print(df.columns)
        
        df['cycle_id'] = pd.to_numeric(df['cycle_id']).astype(int)

        return df
    
    def clean_workout_data(self, df:pd.DataFrame) -> pd.DataFrame:
        """Cleans the workout data DataFrame."""
        df = df.drop(columns=['score'], errors='ignore') # Drops the score column if it exists

        df.columns = df.columns.str.split('score.').str[-1] # Keeps everything after score.
        df.columns = df.columns.str.split('zone_durations.').str[-1] # Keeps everything after zone_durations.
        
        df['timezone_offset'] = df['timezone_offset'].apply(self.tz_offset_to_minutes)
        
        # Convert date columns to datetime
        datetime_columns = ['created_at', 'updated_at', 'start', 'end']
        for col in datetime_columns:
            df[col] = pd.to_datetime(df[col])
        

        int_cols = [col for col in df.columns if col in ['_id', 'rate', 'milli']]
        for col in int_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype(int)

        float_cols = [col for col in df.columns if col in ['strain', 'kilojoule', 'meter']]
        for col in float_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)

        df = df.rename(columns={'id':'workout_id'})
        df['workout_id'] = df['workout_id'].astype(str)

        return df


    def clean_cycle_data(self, df:pd.DataFrame) -> pd.DataFrame:
        """Cleans the cycle data DataFrame."""
        
        df.columns = df.columns.str.split('score.').str[-1] # Keeps everything after score.
        # Convert date columns to datetime
        datetime_columns = ['created_at', 'updated_at', 'start', 'end']
        for col in datetime_columns:
            df[col] = pd.to_datetime(df[col])

        df['timezone_offset'] = df['timezone_offset'].apply(self.tz_offset_to_minutes)
        
        int_cols = [col for col in df.columns if col in ['rate']]
        for col in int_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype(int)

        
        float_cols = [col for col in df.columns if col in ['strain', 'kilojoule']]
        for col in float_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)
        
        df = df.rename(columns={'id':'cycle_id'})
        df['cycle_id'] = pd.to_numeric(df['cycle_id']).astype(int)
        
        return df
    
