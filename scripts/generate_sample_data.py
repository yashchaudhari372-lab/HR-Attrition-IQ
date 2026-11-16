from pathlib import Path
import random
import numpy as np
import pandas as pd

np.random.seed(42)
random.seed(42)

TOTAL = 4700
TARGET_LEFT = 1359

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
out_path = DATA_DIR / "hr_attrition_final.csv"

# Explicit specific rows from screenshot
specific_rows = {
    "E3831": {"DEPARTMENT": "hr", "JOB_ROLE": "HR Executive", "MONTHLY_INCOME": 43752, "YEARS_AT_COMPANY": 0, "OVERTIME": "Yes", "JOB_SATISFACTION": 1, "DISTANCE_FROM_HOME": 23, "ATTRITION": "Yes", "AGE": 26, "GENDER": "Female", "MARITAL_STATUS": "Single", "PERFORMANCE_RATING": 3},
    "E1158": {"DEPARTMENT": "sales", "JOB_ROLE": "Sales Executive", "MONTHLY_INCOME": 61428, "YEARS_AT_COMPANY": 1, "OVERTIME": "Yes", "JOB_SATISFACTION": 1, "DISTANCE_FROM_HOME": 22, "ATTRITION": "Yes", "AGE": 29, "GENDER": "Male", "MARITAL_STATUS": "Single", "PERFORMANCE_RATING": 3},
    "E1189": {"DEPARTMENT": "sales", "JOB_ROLE": "Sales Manager", "MONTHLY_INCOME": 62025, "YEARS_AT_COMPANY": 1, "OVERTIME": "Yes", "JOB_SATISFACTION": 1, "DISTANCE_FROM_HOME": 26, "ATTRITION": "Yes", "AGE": 34, "GENDER": "Male", "MARITAL_STATUS": "Married", "PERFORMANCE_RATING": 3},
    "E1997": {"DEPARTMENT": "sales", "JOB_ROLE": "Sales Manager", "MONTHLY_INCOME": 44577, "YEARS_AT_COMPANY": 0, "OVERTIME": "No", "JOB_SATISFACTION": 2, "DISTANCE_FROM_HOME": 26, "ATTRITION": "Yes", "AGE": 32, "GENDER": "Female", "MARITAL_STATUS": "Single", "PERFORMANCE_RATING": 2},
    "E2132": {"DEPARTMENT": "sales", "JOB_ROLE": "Sales Executive", "MONTHLY_INCOME": 51655, "YEARS_AT_COMPANY": 0, "OVERTIME": "Yes", "JOB_SATISFACTION": 2, "DISTANCE_FROM_HOME": 29, "ATTRITION": "Yes", "AGE": 28, "GENDER": "Male", "MARITAL_STATUS": "Single", "PERFORMANCE_RATING": 3},
    "E2749": {"DEPARTMENT": "sales", "JOB_ROLE": "Sales Executive", "MONTHLY_INCOME": 39314, "YEARS_AT_COMPANY": 0, "OVERTIME": "No", "JOB_SATISFACTION": 1, "DISTANCE_FROM_HOME": 27, "ATTRITION": "Yes", "AGE": 24, "GENDER": "Female", "MARITAL_STATUS": "Single", "PERFORMANCE_RATING": 1},
    "E2888": {"DEPARTMENT": "marketing", "JOB_ROLE": "Marketing Executive", "MONTHLY_INCOME": 44247, "YEARS_AT_COMPANY": 13, "OVERTIME": "Yes", "JOB_SATISFACTION": 2, "DISTANCE_FROM_HOME": 27, "ATTRITION": "Yes", "AGE": 41, "GENDER": "Female", "MARITAL_STATUS": "Married", "PERFORMANCE_RATING": 3},
    "E2912": {"DEPARTMENT": "finance", "JOB_ROLE": "Financial Analyst", "MONTHLY_INCOME": 44845, "YEARS_AT_COMPANY": 6, "OVERTIME": "Yes", "JOB_SATISFACTION": 1, "DISTANCE_FROM_HOME": 23, "ATTRITION": "Yes", "AGE": 35, "GENDER": "Male", "MARITAL_STATUS": "Married", "PERFORMANCE_RATING": 2},
}

roles_by_dept = {
    "engineering": ["Software Engineer", "Tech Lead", "QA Engineer"],
    "finance": ["Accountant", "Financial Analyst"],
    "hr": ["HR Executive", "HR Manager"],
    "marketing": ["Marketing Executive", "Marketing Manager"],
    "sales": ["Sales Executive", "Sales Manager"]
}

# Target department counts and attrition rates
# HR: ~33.4% -> 500 total, 167 left
# Marketing: ~31.7% -> 600 total, 190 left
# Sales: ~29.0% -> 1400 total, 406 left
# Engineering: ~27.6% -> 1500 total, 414 left
# Finance: ~24.7% -> 700 total, 173 left
# Total: 4700 total, 1350 left -> adjust slightly to 1359

dept_distribution = {
    "engineering": {"total": 1500, "target_left": 414},
    "finance": {"total": 700, "target_left": 173},
    "hr": {"total": 500, "target_left": 167},
    "marketing": {"total": 600, "target_left": 190},
    "sales": {"total": 1400, "target_left": 415},
}

rows = []
emp_id_counter = 1

for dept, info in dept_distribution.items():
    dept_total = info["total"]
    dept_target_left = info["target_left"]
    
    # generate attrition flags for this department
    attrition_flags = ["Yes"] * dept_target_left + ["No"] * (dept_total - dept_target_left)
    random.shuffle(attrition_flags)
    
    for left_flag in attrition_flags:
        emp_id = f"E{emp_id_counter:04d}"
        emp_id_counter += 1
        
        # Check if this ID has an explicit record
        if emp_id in specific_rows:
            rec = specific_rows[emp_id].copy()
            rec["EMP_ID"] = emp_id
            rows.append(rec)
            continue
            
        role = random.choice(roles_by_dept[dept])
        gender = random.choice(["Male", "Female"])
        marital = random.choices(["Married", "Single", "Divorced", "Unknown"], weights=[0.47, 0.32, 0.18, 0.03])[0]
        
        # Correlate with attrition
        is_attrition = (left_flag == "Yes")
        
        # Overtime: 41.6% attrition for Yes, 23.3% for No
        # P(OT=Yes | Attrition=Yes) ~ 0.45, P(OT=Yes | Attrition=No) ~ 0.22
        if is_attrition:
            overtime = "Yes" if random.random() < 0.46 else "No"
            job_sat = random.choices([1, 2, 3, 4], weights=[0.36, 0.35, 0.16, 0.13])[0]
            perf_rating = random.choices([1, 2, 3, 4], weights=[0.25, 0.30, 0.30, 0.15])[0]
            dist = int(random.choices(
                [random.randint(1, 10), random.randint(11, 20), random.randint(21, 35)],
                weights=[0.30, 0.30, 0.40]
            )[0])
            # Tenure bands: 10+ yrs (~28%), 5-9 yrs (~27%), 2-4 yrs (~28%), 0-1 yrs (~40%)
            tenure_band = random.choices([0, 1, 2, 3], weights=[0.18, 0.20, 0.27, 0.35])[0]
            if tenure_band == 0:
                years = random.choice([0, 1])
            elif tenure_band == 1:
                years = random.randint(2, 4)
            elif tenure_band == 2:
                years = random.randint(5, 9)
            else:
                years = random.randint(10, 25)
                
            age = max(18, min(60, int(years + random.randint(20, 38))))
            # Monthly income: Below 45k higher attrition
            income_base = random.choices([38000, 52000, 68000, 88000], weights=[0.38, 0.22, 0.24, 0.16])[0]
            income = int(np.clip(np.random.normal(income_base, 8000), 22000, 160000))
        else:
            overtime = "Yes" if random.random() < 0.22 else "No"
            job_sat = random.choices([1, 2, 3, 4], weights=[0.16, 0.20, 0.34, 0.30])[0]
            perf_rating = random.choices([1, 2, 3, 4], weights=[0.18, 0.28, 0.36, 0.18])[0]
            dist = int(random.choices(
                [random.randint(1, 10), random.randint(11, 20), random.randint(21, 35)],
                weights=[0.42, 0.36, 0.22]
            )[0])
            tenure_band = random.choices([0, 1, 2, 3], weights=[0.06, 0.15, 0.26, 0.53])[0]
            if tenure_band == 0:
                years = random.choice([0, 1])
            elif tenure_band == 1:
                years = random.randint(2, 4)
            elif tenure_band == 2:
                years = random.randint(5, 9)
            else:
                years = random.randint(10, 25)
                
            age = max(20, min(62, int(years + random.randint(22, 40))))
            income_base = random.choices([42000, 56000, 72000, 92000], weights=[0.18, 0.28, 0.32, 0.22])[0]
            income = int(np.clip(np.random.normal(income_base, 8500), 25000, 175000))
            
        rows.append({
            "EMP_ID": emp_id,
            "AGE": age,
            "DEPARTMENT": dept,
            "JOB_ROLE": role,
            "GENDER": gender,
            "MARITAL_STATUS": marital,
            "PERFORMANCE_RATING": perf_rating,
            "OVERTIME": overtime,
            "DISTANCE_FROM_HOME": dist,
            "MONTHLY_INCOME": income,
            "YEARS_AT_COMPANY": years,
            "JOB_SATISFACTION": job_sat,
            "ATTRITION": left_flag
        })

df = pd.DataFrame(rows)

# Ensure any specific IDs that fell outside are present
for emp_id, spec in specific_rows.items():
    idx_matches = df.index[df["EMP_ID"] == emp_id]
    if len(idx_matches) > 0:
        for k, v in spec.items():
            df.at[idx_matches[0], k] = v
    else:
        # replace a random row with this ID
        replace_idx = random.randint(0, len(df) - 1)
        for k, v in spec.items():
            df.at[replace_idx, k] = v
        df.at[replace_idx, "EMP_ID"] = emp_id

# Adjust total left to exactly 1359
current_left = (df["ATTRITION"] == "Yes").sum()
diff = TARGET_LEFT - current_left
if diff > 0:
    no_indices = df[df["ATTRITION"] == "No"].index.tolist()
    to_flip = random.sample(no_indices, diff)
    df.loc[to_flip, "ATTRITION"] = "Yes"
elif diff < 0:
    yes_indices = [i for i in df[df["ATTRITION"] == "Yes"].index.tolist() if df.at[i, "EMP_ID"] not in specific_rows]
    to_flip = random.sample(yes_indices, abs(diff))
    df.loc[to_flip, "ATTRITION"] = "No"

# Scale income slightly to have mean close to 61,279
current_mean = df["MONTHLY_INCOME"].mean()
df["MONTHLY_INCOME"] = (df["MONTHLY_INCOME"] * (61279 / current_mean)).round().astype(int)

# Specific rows fixup for monthly income
for emp_id, spec in specific_rows.items():
    idx_matches = df.index[df["EMP_ID"] == emp_id]
    if len(idx_matches) > 0:
        df.at[idx_matches[0], "MONTHLY_INCOME"] = spec["MONTHLY_INCOME"]

df.to_csv(out_path, index=False)

print(f"Generated {len(df)} rows to {out_path}")
print(f"Attrition: {(df['ATTRITION'] == 'Yes').sum()} Yes ({((df['ATTRITION'] == 'Yes').mean()*100):.1f}%), {(df['ATTRITION'] == 'No').sum()} No")
print(f"Mean Monthly Income: ₹{df['MONTHLY_INCOME'].mean():,.0f}")
print("Departments:")
print(df.groupby("DEPARTMENT")["ATTRITION"].value_counts(normalize=True).unstack().mul(100).round(1))
