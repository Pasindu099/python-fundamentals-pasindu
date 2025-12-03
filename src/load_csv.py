import pandas as pd
from pathlibPath import Path


def load_csv(file_path: str) -> pd.DataFrame:
    """Load a CSV file into a Pandas DataFrame."""
    csv_path = Path("data/users.csv")

    if not csv_path.exists():
        raise FileNotFoundError(f"The file at {file_path} does not exist.")

    df = pd.read_csv(csv_path)
    return df


if __name__ == "__main__":
    df = load_csv("data/users.csv")
    print("\n--- Loaded DataFrame ---\n")
    print(df.head())
