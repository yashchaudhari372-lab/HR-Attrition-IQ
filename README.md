# HR Attrition Intelligence

Premium Streamlit workforce analytics dashboard using Snowflake, Plotly, and the existing Random Forest model bundle.

## Project layout

```text
project/
├── app.py
├── main.py
├── connect_snowflake.py
├── eda.py
├── train_model.py
├── requirements.txt
├── .env                 # local only; never commit
├── models/
│   └── attrition_model.pkl
└── .gitignore
```

The app searches for the model at `models/attrition_model.pkl` and then `attrition_model.pkl` in the project root. Keep the original model bundle; its expected feature order and encoders are used by the prediction form.

## Install and run

Use a Python version supported by your installed Snowflake and scikit-learn packages. From the project directory:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Snowflake configuration

Set these values in your local `.env` file or the deployment platform's secret manager:

```dotenv
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
```

The app queries `hr_attrition_final` from the configured database/schema. Use a least-privilege Snowflake role with read-only access to the required table. Do not commit `.env`; use Streamlit secrets or your host's secret manager in deployment.

## Features

- Five themes and sidebar navigation
- Overview KPIs and interactive Plotly charts
- Advanced workforce filters, applied consistently to dashboard analytics and exports
- Department, overtime, income, age, tenure, satisfaction and distance analyses when columns are available
- Employee attrition prediction using the existing model bundle and its saved encoders
- Dynamically generated descriptive insights
- CSV, Excel and aggregate executive-summary PDF downloads
- Cached Snowflake reads, refresh controls and user-facing connection errors

## Model evaluation caveat

The provided model artifact stores the fitted estimator, encoders and ordered feature names, but not a held-out evaluation report. The Model Performance page deliberately does not invent accuracy, precision, recall, F1 or ROC-AUC. Evaluate on an untouched test set from the original training process (or create a documented new evaluation protocol) before reporting those metrics. The model's `predict_proba` output should not be called calibrated real-world risk without a calibration evaluation.

## Deployment

1. Push the project to a private repository, excluding `.env`, virtual environments, caches, and employee exports.
2. Configure the six Snowflake environment variables in the deployment secret manager.
3. Ensure the model artifact is available at `models/attrition_model.pkl` or the project root.
4. Install `requirements.txt` and launch with `streamlit run app.py`.
5. Validate Snowflake access, filters, each navigation page, prediction outputs, and CSV/XLSX/PDF exports in the target environment.

## Testing checklist

- [ ] Snowflake connection succeeds with read-only access.
- [ ] Empty result sets and missing configuration show useful errors.
- [ ] Every sidebar navigation item opens its page.
- [ ] All five themes remain selected through reruns.
- [ ] Filters update KPIs, charts, insights and exports.
- [ ] Empty filter results do not crash charts.
- [ ] Predictor uses the saved encoders and exact model feature order.
- [ ] Prediction probabilities and class outputs render correctly.
- [ ] CSV, Excel and PDF files open and reflect the selected filters.
- [ ] No credentials are displayed in logs, UI, or repository history.
- [ ] Model metrics are reported only from a documented held-out evaluation.
