import pandas as pd


class WhoopDataCleaner():
    def clean_sleep_data(self, df:pd.DataFrame) -> pd.DataFrame:
        """Cleans the sleep data DataFrame."""
        
        # Renames all columns to replace . with _
        df.columns = df.columns.str.replace('.', '_', regex=False)
        # Convert date columns to datetime
        datetime_columns = ['created_at', 'updated_at', 'start', 'end']
        for col in datetime_columns: # Converts all date columns to datetime
            df[col] = pd.to_datetime(df[col])

        
        df['timezone_offset'] = df['timezone_offset'].apply(self.tz_offset_to_minutes)

        int_cols = [col for col in df.columns if col.endswith("milli") or col.endswith("count") or col.endswith("id")] # lists all columns ending with milli to be converted to in
        for col in int_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        float_columns = [col for col in df.columns if col.endswith("percentage") or col.endswith("rate")]
        for col in float_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float) 
            if col.endswith("percentage"): #converts all percentages to a decimal
                df[col] = df[col] / 100
        

        # Handle missing values
        df.fillna({
            'score_respiratory_rate': df['score_respiratory_rate'].mean(),
            'score_sleep_performance_percentage': df['score_sleep_performance_percentage'].mean(),
            'score_sleep_consistency_percentage': df['score_sleep_consistency_percentage'].mean(),
            'score_sleep_efficiency_percentage': df['score_sleep_efficiency_percentage'].mean()
        }, inplace=True)
                # Convert timezone_offset from "+01:00" format to minutes
        return df
        
    def tz_offset_to_minutes(self, offset_str):
        if pd.isna(offset_str):
            return 0
        elif isinstance(offset_str, str) and (offset_str.startswith('+') or offset_str.startswith('-')):
            sign = 1 if offset_str[0] == '+' else -1
            hours, minutes = map(int, offset_str[1:].split(':'))
        return sign * (hours * 60 + minutes)
