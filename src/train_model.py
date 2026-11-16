import os
import sys
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle

try:
    from imblearn.over_sampling import SMOTE
    has_smote = True
except ImportError:
    has_smote = False

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
MODELS_DIR = ROOT / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_DATA_FILE = ROOT / "data" / "hr_attrition_final.csv"

def load_data():
    required = ["SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD", "SNOWFLAKE_ACCOUNT", "SNOWFLAKE_WAREHOUSE", "SNOWFLAKE_DATABASE", "SNOWFLAKE_SCHEMA"]
    has_creds = all(os.getenv(k) for k in required)
    
    if has_creds and snowflake is not None:
        try:
            print("Connecting to Snowflake for training data...")
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

# Drop ID column if present
data = df.drop(columns=['EMP_ID']) if 'EMP_ID' in df.columns else df.copy()

# Encode categorical columns
label_encoders = {}
cat_cols = data.select_dtypes(include=['object', 'category']).columns.drop('ATTRITION')
for col in cat_cols:
    le = LabelEncoder()
    data[col] = le.fit_transform(data[col].astype(str))
    label_encoders[col] = le

# Target encoding
data['ATTRITION'] = data['ATTRITION'].astype(str).str.title().map({'Yes': 1, 'No': 0})

X = data.drop(columns=['ATTRITION'])
y = data['ATTRITION']

# Fill remaining missing values with column median
X = X.fillna(X.median(numeric_only=True))

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ---- Balance training data ----
if has_smote:
    smote = SMOTE(random_state=42)
    X_train_bal, y_train_bal = smote.fit_resample(X_train, y_train)
    print("Before SMOTE:", y_train.value_counts().to_dict())
    print("After SMOTE:", y_train_bal.value_counts().to_dict())
    rf_base = RandomForestClassifier(random_state=42)
else:
    print("imblearn not found; training with class_weight='balanced'")
    X_train_bal, y_train_bal = X_train, y_train
    rf_base = RandomForestClassifier(random_state=42, class_weight='balanced')

# ---- Hyperparameter tuning ----
param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [5, 10, None],
    'min_samples_split': [2, 5]
}

grid = GridSearchCV(
    rf_base,
    param_grid,
    cv=3,
    scoring='f1',
    n_jobs=-1
)
grid.fit(X_train_bal, y_train_bal)

model = grid.best_estimator_
print("\nBest params:", grid.best_params_)

# ---- Evaluate on original (untouched) test set ----
y_pred = model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

# Feature importance
importance = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
print("\nTop factors driving attrition:\n", importance.head(8))

# Save model + encoders for Streamlit
save_path = MODELS_DIR / "attrition_model.pkl"
with open(save_path, "wb") as f:
    pickle.dump({"model": model, "encoders": label_encoders, "columns": list(X.columns)}, f)

print(f"\nModel successfully saved to {save_path}")
