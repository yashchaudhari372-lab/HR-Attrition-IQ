import os
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import snowflake.connector
except ImportError:
    snowflake = None

ROOT = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = ROOT / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_DATA_FILE = ROOT / "data" / "hr_attrition_final.csv"

def load_data():
    required = ["SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD", "SNOWFLAKE_ACCOUNT", "SNOWFLAKE_WAREHOUSE", "SNOWFLAKE_DATABASE", "SNOWFLAKE_SCHEMA"]
    has_creds = all(os.getenv(k) for k in required)
    
    if has_creds and snowflake is not None:
        try:
            print("Connecting to Snowflake for EDA data...")
            conn = snowflake.connector.connect(
                user=os.getenv("SNOWFLAKE_USER"),
                password=os.getenv("SNOWFLAKE_PASSWORD"),
                account=os.getenv("SNOWFLAKE_ACCOUNT"),
                warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
                database=os.getenv("SNOWFLAKE_DATABASE"),
                schema=os.getenv("SNOWFLAKE_SCHEMA"),
                login_timeout=15,
                network_timeout=20,
            )
            df = pd.read_sql("SELECT * FROM hr_attrition_final;", conn)
            conn.close()
            print("Loaded data from Snowflake.")
            return df
        except Exception as exc:
            print(f"⚠️ Snowflake connection failed ({type(exc).__name__}: {exc}).")
            print("Falling back to bundled local dataset...")
    
    if LOCAL_DATA_FILE.exists():
        print(f"Loaded dataset from {LOCAL_DATA_FILE}")
        return pd.read_csv(LOCAL_DATA_FILE)
    raise FileNotFoundError(f"Neither Snowflake nor local dataset at {LOCAL_DATA_FILE} could be loaded.")

df = load_data()
df.columns = [str(c).upper() for c in df.columns]

# 1. Overall attrition rate
print("\nOverall Attrition Rate:")
print(df['ATTRITION'].value_counts(normalize=True) * 100)

# 2. Attrition by department
plt.figure(figsize=(8, 5))
sns.countplot(data=df, x='DEPARTMENT', hue='ATTRITION')
plt.title("Attrition by Department")
plt.xticks(rotation=45)
plt.tight_layout()
dept_path = OUTPUTS_DIR / "attrition_by_department.png"
plt.savefig(dept_path)
plt.close()

# 3. Attrition by overtime
plt.figure(figsize=(6, 5))
sns.countplot(data=df, x='OVERTIME', hue='ATTRITION')
plt.title("Attrition by Overtime")
plt.tight_layout()
ot_path = OUTPUTS_DIR / "attrition_by_overtime.png"
plt.savefig(ot_path)
plt.close()

# 4. Salary vs Attrition
plt.figure(figsize=(6, 5))
sns.boxplot(data=df, x='ATTRITION', y='MONTHLY_INCOME')
plt.title("Monthly Income vs Attrition")
plt.tight_layout()
sal_path = OUTPUTS_DIR / "salary_vs_attrition.png"
plt.savefig(sal_path)
plt.close()

print(f"\nEDA charts saved to {OUTPUTS_DIR}:")
print(" - attrition_by_department.png")
print(" - attrition_by_overtime.png")
print(" - salary_vs_attrition.png")
