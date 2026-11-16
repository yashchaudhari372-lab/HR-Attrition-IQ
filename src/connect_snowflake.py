import os
import sys
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
import pandas as pd

try:
    import snowflake.connector
except ImportError:
    snowflake = None

ROOT = Path(__file__).resolve().parent.parent
LOCAL_DATA_FILE = ROOT / "data" / "hr_attrition_final.csv"

def get_config(key, default=None):
    return os.getenv(key, default)

def test_connection():
    required = ["SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD", "SNOWFLAKE_ACCOUNT", "SNOWFLAKE_WAREHOUSE", "SNOWFLAKE_DATABASE", "SNOWFLAKE_SCHEMA"]
    missing = [k for k in required if not get_config(k)]
    
    if missing:
        print(f"⚠️ Snowflake configuration missing keys: {', '.join(missing)}")
        print("Falling back to verifying bundled local dataset...")
        return verify_local_data()

    if snowflake is None:
        print("⚠️ snowflake-connector-python is not installed.")
        print("Falling back to verifying bundled local dataset...")
        return verify_local_data()

    print("Attempting connection to Snowflake...")
    try:
        conn = snowflake.connector.connect(
            user=get_config("SNOWFLAKE_USER"),
            password=get_config("SNOWFLAKE_PASSWORD"),
            account=get_config("SNOWFLAKE_ACCOUNT"),
            warehouse=get_config("SNOWFLAKE_WAREHOUSE"),
            database=get_config("SNOWFLAKE_DATABASE"),
            schema=get_config("SNOWFLAKE_SCHEMA"),
            login_timeout=15,
            network_timeout=20,
        )
        print("✅ Snowflake connection established!")
        query = "SELECT * FROM hr_attrition_final;"
        df = pd.read_sql(query, conn)
        conn.close()
        print(f"✅ Successfully fetched data from Snowflake. Shape: {df.shape}")
        print(df.head(2))
        return df
    except Exception as exc:
        print("\n⚠️ Snowflake connection failed:")
        print(f"   {type(exc).__name__}: {exc}")
        if "390913" in str(exc) or "free trial has ended" in str(exc).lower():
            print("\n💡 Reason: Snowflake free trial has ended and virtual warehouses are suspended.")
            print("   To use Snowflake live: Add billing or a new trial account in Snowflake UI and update .env.")
        print("\nSwitching to bundled local dataset fallback...")
        return verify_local_data()

def verify_local_data():
    if not LOCAL_DATA_FILE.exists():
        print(f"❌ Local dataset not found at {LOCAL_DATA_FILE}")
        sys.exit(1)
    df = pd.read_csv(LOCAL_DATA_FILE)
    print(f"✅ Local dataset verified at {LOCAL_DATA_FILE}. Shape: {df.shape}")
    print(df.head(2))
    return df

if __name__ == "__main__":
    test_connection()
