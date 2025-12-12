import pandas as pd
import sqlite3
from pathlib import Path

# RAW CSV file ka naam
RAW_CSV = "contacts_raw.csv"
DB_NAME = "pythontut.db"   # wahi DB jo tumhara Tkinter app use kar raha hai

def extract(csv_path: str) -> pd.DataFrame:
    """CSV se data read karo."""
    print(f"[EXTRACT] Reading data from {csv_path} ...")
    df = pd.read_csv(csv_path)
    return df

def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Data clean + transform karo."""
    print("[TRANSFORM] Cleaning and transforming data ...")

    # Column names normalize
    df.columns = [c.strip().lower() for c in df.columns]

    # Expected columns ensure karo
    rename_map = {
        "firstname": "firstname",
        "lastname": "lastname",
        "gender": "gender",
        "age": "age",
        "address": "address",
        "contact": "contact",
    }
    df = df[[*rename_map.keys()]]
    df = df.rename(columns=rename_map)

    # String columns trim karna
    for col in ["firstname", "lastname", "gender", "address", "contact"]:
        df[col] = df[col].astype(str).str.strip()

    # Age numeric me convert karo
    df["age"] = pd.to_numeric(df["age"], errors="coerce")

    # Invalid age remove (NaN ya <=0)
    df = df.dropna(subset=["age"])
    df = df[df["age"] > 0]

    # Age ko int bana do
    df["age"] = df["age"].astype(int)

    # Duplicate contacts remove karo (same contact number)
    df = df.drop_duplicates(subset=["contact"])

    # Optional: full_name add kar sakte ho (future use ke liye)
    df["full_name"] = df["firstname"] + " " + df["lastname"]

    print("[TRANSFORM] Rows after cleaning:", len(df))
    return df

def load_to_sqlite(df: pd.DataFrame, db_path: str):
    """Clean data ko SQLite DB ke member table me load karo."""
    print(f"[LOAD] Loading data into SQLite DB: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Table schema same rakha hai jo tumhare Tkinter code me hai
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS member (
            mem_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            firstname TEXT,
            lastname TEXT,
            gender TEXT,
            age TEXT,
            address TEXT,
            contact TEXT
        )
    """)

    # Pehle purana data delete karna ho toh uncomment karo:
    # cursor.execute("DELETE FROM member")

    # Data insert karo
    records = df[["firstname", "lastname", "gender", "age", "address", "contact"]].values.tolist()
    cursor.executemany("""
        INSERT INTO member (firstname, lastname, gender, age, address, contact)
        VALUES (?, ?, ?, ?, ?, ?)
    """, records)

    conn.commit()
    conn.close()
    print(f"[LOAD] Inserted {len(records)} rows into 'member' table.")

def save_clean_csv(df: pd.DataFrame, out_path: str = "contacts_clean.csv"):
    """Cleaned data ko CSV me bhi save karo (optional)."""
    df.to_csv(out_path, index=False)
    print(f"[SAVE] Cleaned data saved to {out_path}")

def main():
    # Check karo raw CSV hai ya nahi
    if not Path(RAW_CSV).exists():
        print(f"[ERROR] {RAW_CSV} file nahi mili. Pehle CSV bana lo.")
        return

    # ETL pipeline
    df_raw = extract(RAW_CSV)
    df_clean = transform(df_raw)
    save_clean_csv(df_clean)
    load_to_sqlite(df_clean, DB_NAME)
    print("[DONE] ETL pipeline successfully completed ✅")

if __name__ == "__main__":
    main()
