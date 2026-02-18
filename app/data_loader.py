import pandas as pd
from typing import Union


def load_csv(file_path: str) -> pd.DataFrame:
    """
    Load a CSV file and return a pandas DataFrame.
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        raise ValueError(f"Error loading CSV file: {e}")


def dataframe_to_text(df: pd.DataFrame) -> str:
    """
    Convert a DataFrame into structured text format
    suitable for embedding in RAG pipeline.
    """
    try:
        # Convert each row into structured sentence
        rows_as_text = []

        for index, row in df.iterrows():
            row_text = ", ".join(
                [f"{col}: {row[col]}" for col in df.columns]
            )
            rows_as_text.append(f"Row {index + 1}: {row_text}")

        return "\n".join(rows_as_text)

    except Exception as e:
        raise ValueError(f"Error converting DataFrame to text: {e}")
