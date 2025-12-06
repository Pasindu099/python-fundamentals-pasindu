import pandas as pd
import numpy as np
import os
from functools import partial
from typing import Optional


# setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

CSV_FILE_PATH = os.path.join(DATA_DIR, "users_assignment4.csv")

if not os.path.exists(CSV_FILE_PATH):
    sample_data = """user_id,name,age,email,birthdate
1,Pasindu,26,pasindu@example.com,1999-11-04
2,Divya,27,divya@example.com,1998-07-28
3,Lakshmi,58,lakshmi@example.com,1967-04-08
4,Amitha,58,amitha@example.com,1967-12-20
5,Devi,80,devi@example.com,1945-03-15
6,Sunil,35,sunil@example.com,1988-09-12
7,Divya,27,divya@example.com,1998-07-28
"""
    with open(CSV_FILE_PATH, "w") as f:
        f.write(sample_data)

print(f"Sample CSV file created at: {CSV_FILE_PATH}")

# main dataframe
df = pd.read_csv(CSV_FILE_PATH)


# define a pandas series with custom index
user_donations = pd.Series(
    [100000, 50000, 75000, 200000, 150000, 30000],
    index=["Pasindu", "Divya", "Lakshmi", "Amitha", "Devi", "Sunil"],
    name="donations",
)

print("User Donations Series:")
print(user_donations)
print(user_donations.index)

##inspeact data
print("\n---Data type inspection---")
print(user_donations.dtypes)

print("\n---Header inspection---")
print(user_donations.head())

print("\n---Tail inspection---")
print(user_donations.tail())

print("\n---Describe inspection---")
print(user_donations.describe())


# data slicing and filtering
# data slicing by row position and by column name
print("\nData Slicing")

# slicing by column name
columns_subset = df[["name", "age", "email"]]
print("\nSlicing by Column Name (Name, Age, Email):\n", columns_subset.head(3))

# slicing by row position using .iloc
rows_subset = df.iloc[1:4]
print("\nSlicing by Row Position (df.iloc[1:4]):\n", rows_subset)


# data Filtering (Slicing)
print("\nData Filtering (Slicing)")

# slicing using a boolean flags array (Age > 40)
age_filter_flag = df["age"] > 40
df_elder = df[age_filter_flag]
print("\nFiltered by Boolean Flag (Age > 40):\n", df_elder)

# slicing by a data range (Age between 25 and 40, inclusive)
df_middle = df[df["age"].between(25, 40)]
print("\nFiltered by Data Range (Age between 25 and 40):\n", df_middle)


print("Data Cleaning and Validation")


# demonstrate the usage of duplicated, nunique, and drop_duplicates
print("\nDuplicates Management")
# check for duplicates
print("Boolean Series for Duplicated Rows:\n", df.duplicated())
print(f"\nTotal Unique Names: {df['name'].nunique()}")
print(f"Total Unique User IDs: {df['user_id'].nunique()}")

# drop duplicate records
df_clean = df.drop_duplicates(keep="first")
print(f"\nDataFrame size after drop_duplicates: {len(df_clean)} rows")
print("Cleaned DataFrame Head:\n", df_clean.head(8))


# apply pd.to_numeric and pd.to_datetime for safe type conversion
print("\nSafe Type Conversion")

# ensure 'user_id' is numeric
df_clean["user_id"] = pd.to_numeric(df_clean["user_id"], errors="coerce")

# convert 'birthdate' to datetime
df_clean["birthdate"] = pd.to_datetime(df_clean["birthdate"], errors="coerce")

print("\nFinal dtypes after conversion:\n", df_clean[["user_id", "birthdate"]].dtypes)


# set default values for missing data in a column using .apply()
print("\nHandling Missing Data with .apply()")

# introduce missing data for demonstration
df_clean.loc[df_clean["name"] == "Lakshmi", "email"] = np.nan
print("\nNull counts before fill:\n", df_clean["email"].isnull().sum())


# define a function to fill email NaN
def fill_missing_email(email: Optional[str]) -> str:
    """Sets a default placeholder if the email is missing."""
    if pd.isna(email):
        return "default_placeholder@company.com"
    return str(email)


# use .apply() on the 'email' column to set a default value
df_clean["email"] = df_clean["email"].apply(fill_missing_email)

print("\nNull counts after fill:\n", df_clean["email"].isnull().sum())
print(
    "Lakshmi's email after fill:\n",
    df_clean[df_clean["name"] == "Lakshmi"]["email"].iloc[0],
)


print("Data Processing Pipelines")


# implement a data cleaning step in a pipeline using .pipe() for type conversion.
print("\n.pipe() for Pipeline Cleaning (Type Conversion)")


def convert_age_to_float(data_frame: pd.DataFrame) -> pd.DataFrame:
    """Cleaning function to convert the 'age' column to float type."""
    df_copy = data_frame.copy()
    df_copy["age"] = df_copy["age"].astype(float)
    return df_copy


# implement a pipeline
df_piped_1 = df_clean.copy().pipe(convert_age_to_float)

print("\nData Types after .pipe() conversion:\n", df_piped_1.dtypes)
print("Null counts after pipeline step:\n", df_piped_1.isnull().sum())


# utilize .pipe() with partial arguments to apply a function requiring a threshold parameter.
print("\n.pipe() with Partial Arguments (Threshold)")


def flag_records_by_threshold(
    data_frame: pd.DataFrame, column: str, threshold: int
) -> pd.DataFrame:
    """Flags records where a column value is above the given threshold."""
    df_copy = data_frame.copy()
    df_copy[f"{column}_IS_HIGH_RISK"] = df_copy[column] >= threshold
    return df_copy


# use partial to fix column name and threshold
flag_high_age = partial(flag_records_by_threshold, column="age", threshold=60)

# apply the partial function in the pipeline
df_piped_2 = df_clean.copy().pipe(flag_high_age)

print("\nDataFrame after .pipe() with partial arguments (Flagging Age >= 60):\n")
print(df_piped_2[["name", "age", "age_IS_HIGH_RISK"]])
