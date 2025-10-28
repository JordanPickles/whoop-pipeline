from whoop_pipeline.data_cleaning import WhoopDataCleaner
import pandas as pd


def test_rename_id_column():
    df = pd.DataFrame(
    {'id': ['a', 'b', 'c'],
        'value': [1,2,3]}
    )
    df_test = WhoopDataCleaner().rename_id_column(df, endpoint='test')

    assert 'test_id' in df_test.columns

def test_split_column_names():
    df = pd.DataFrame(
    {'sleep.start': ['2023-01-01T00:00:00Z', '2023-01-02T00:00:00Z'],
        'sleep.end': ['2023-01-01T08:00:00Z', '2023-01-02T08:00:00Z']}
    )
    df_test = WhoopDataCleaner().split_column_names(df, endpoint='sleep')

    assert 'start' in df_test.columns
    assert 'end' in df_test.columns

def test_coerce_datetime():
    df = pd.DataFrame(
    {'start': ['2023-01-01T00:00:00Z', 'invalid_date'],
        'end': ['2023-01-01T08:00:00Z', '2023-01-02T08:00:00Z']}
    )
    df_test = WhoopDataCleaner().coerce_datetime(df, columns=['start', 'end'])
    assert df_test['start'].dtypes == 'datetime64[ns, UTC]'
    assert df_test['end'].dtypes == 'datetime64[ns, UTC]'

def test_coerce_integer():
    df = pd.DataFrame(
    {'int_col': ['1', '2', 'invalid'],
        'float_col': ['1.5', '2.5', '3.5']}
    )
    df_test = WhoopDataCleaner().coerce_integer(df, columns=['int_col'])
    assert df_test['int_col'].dtypes == 'Int64'

def test_coerce_float():
    df = pd.DataFrame(
    {'int_col': ['1', '2', 'invalid'],
        'float_col': ['1.5', '2.5', '3.5']}
    )
    df_test = WhoopDataCleaner().coerce_float(df, columns=['float_col'])
    assert df_test['float_col'].dtypes == float

def test_coerce_string():
    df = pd.DataFrame(
    {'int_col': [1, 2, 3],
        'str_col': [True, False, None]}
    )
    df_test = WhoopDataCleaner().coerce_string(df, columns=['str_col'])
    assert df_test['str_col'].dtypes == object

def test_coerce_boolean():
    df = pd.DataFrame(
    {'bool_col': [1, 0, None],
        'str_col': ['True', 'False', 'True']}
    )
    df_test = WhoopDataCleaner().coerce_boolean(df, columns=['bool_col'])
    assert df_test['bool_col'].dtypes == bool

def test_tz_offset_to_minutes():
    cleaner = WhoopDataCleaner()
    assert cleaner.tz_offset_to_minutes('+02:30') == 150
    assert cleaner.tz_offset_to_minutes('-01:15') == -75
    assert cleaner.tz_offset_to_minutes('invalid') == 0
    assert cleaner.tz_offset_to_minutes(None) == 0

if __name__ == '__main__':
    # test_rename_id_column()
    # test_split_column_names()
    test_coerce_datetime()