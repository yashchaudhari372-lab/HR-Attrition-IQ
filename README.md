# HR Attrition IQ | HR Attrition Intelligence Dashboard

An interactive HR analytics dashboard built to explore employee attrition patterns, understand workforce risk factors, and support data-informed retention planning. The project combines Streamlit, Plotly, Snowflake data access, and an existing Random Forest model bundle.

🌐 **Live Dashboard:** [Open HR Attrition IQ](https://hr-attrition-iq-fz7cy8ubamq9xq3jff4qib.streamlit.app/)  
💻 **GitHub Repository:** [HR-Attrition-IQ](https://github.com/yashchaudhari372-lab/HR-Attrition-IQ)

---

## 📌 Project Overview

Employee attrition can create recruitment costs, loss of organizational knowledge, team disruption, and additional pressure on remaining employees. HR teams need clear ways to explore turnover patterns and identify workforce segments that may benefit from further review.

**HR Attrition IQ** presents workforce metrics and interactive visualizations in a multi-page dashboard. Users can explore attrition by department, job role, overtime, income, age group, tenure, job satisfaction, and commute distance. The risk-segmentation page brings together employee-level factors and a table of records for further review.

The dashboard is designed as an **analytics and decision-support tool**. Its outputs should be interpreted alongside employee feedback, organizational context, and human judgment—not used as the sole basis for employment decisions.

## 🎯 Project Objectives

- Analyze overall employee attrition and workforce composition.
- Compare attrition rates across departments and job roles.
- Explore potential relationships between attrition and overtime, income, satisfaction, age, tenure, and commute distance.
- Segment employee records using the project's available risk-factor logic.
- Provide interactive filters for exploring relevant workforce groups.
- Present findings in a clear, executive-friendly dashboard.
- Connect to Snowflake for data access when the required configuration is available.
- Support review of employee records through the existing Random Forest model bundle.

## ✨ Key Features

### 1. Executive Overview
The overview page summarizes workforce metrics, including:
- Total employees
- Employees who left
- Overall attrition rate
- Average monthly income
- Active high-risk employee count

It also includes visualizations for attrition by department, attrition distribution, employees leaving by job role, and tenure versus attrition rate.

### 2. Attrition Drivers
The attrition analysis page helps explore patterns across:
- Overtime status
- Monthly income bands
- Commute-distance bands
- Job satisfaction
- Performance rating
- Age groups
- Department-level attrition distribution

Interactive filters include department, job role, age group, marital status, gender, and overtime, where supported by the dashboard.

### 3. Risk Segmentation & Action List
The risk segmentation page focuses on employee records with multiple risk factors. It includes:
- Counts of high-risk employees and active high-risk employees
- Attrition rate by number of risk factors
- Department and job-role filters
- An employee table showing fields such as employee ID, department, job role, risk-factor count, monthly income, years at company, overtime, job satisfaction, and distance from home

The risk-factor count and related labels should be interpreted according to the project's implemented logic. They are indicators for further investigation, not proof that a particular employee will leave.

### 4. Interactive Visual Analytics
- Filter dashboard views by available employee attributes.
- Compare groups using charts and summary metrics.
- Explore department, job-role, income, tenure, satisfaction, and distance patterns.
- Use visual summaries to support HR questions and retention discussions.

### 5. Data Access and Exports
The existing application supports Snowflake configuration, cached data reads, refresh controls, and CSV, Excel, and aggregate executive-summary PDF downloads, as described in the application README. Exported files should be handled carefully because employee data may be sensitive.

---

## 🖥️ Dashboard Screenshots

### 1. Executive Overview
High-level workforce KPIs, department-wise attrition, employee exits by job role, and tenure-related patterns.

![HR Attrition IQ — Executive Overview](assets/dashboard/executive-overview.jpg)

### 2. Attrition Drivers
Exploration of attrition patterns by overtime, income, commute distance, job satisfaction, performance rating, age group, and department.

![HR Attrition IQ — Attrition Drivers](assets/dashboard/attrition-drivers.jpg)

### 3. Risk Segmentation & Action List
High-risk employee summaries, attrition rates by risk-factor count, and employee-level fields for further review.

![HR Attrition IQ — Risk Segmentation and Action List](assets/dashboard/risk-segmentation-action-list.jpg)

---

## 📊 Example Insights Visible in the Dashboard

The supplied dashboard screenshots illustrate the following patterns in the displayed data:

- **Department differences:** the displayed attrition rates vary by department, with HR and Marketing higher than Finance in the overview.
- **Overtime association:** the Attrition Drivers page shows a higher attrition rate for employees marked as working overtime than for those not marked as working overtime.
- **Income bands:** the displayed chart shows differences in attrition rates across monthly-income groups.
- **Commute distance:** the chart compares attrition rates across distance bands, including a higher displayed rate for the 21+ km group.
- **Job satisfaction:** the chart shows different attrition rates across satisfaction scores.
- **Risk-factor count:** the risk segmentation page shows increasing attrition rates across higher risk-factor counts in the displayed chart.

These are descriptive patterns from the dashboard screenshots, not evidence that any single factor causes attrition. Results can change with filters and data updates, and should be validated against the underlying dataset before being used in a formal report.

## 🧰 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic and data processing |
| Streamlit | Interactive dashboard and web app |
| Pandas | Tabular data manipulation |
| Plotly | Interactive charts and visualizations |
| Snowflake | Cloud data access, when configured |
| Scikit-learn / Random Forest | Existing employee attrition model bundle |
| Joblib / serialized model artifacts | Loading the saved model and associated preprocessing objects, as applicable |

> The model artifact and its saved encoders/feature order are part of the existing project. Keep them consistent with the training pipeline. Do not report model accuracy or other evaluation metrics unless you have a documented evaluation on a held-out dataset.

## 🗂️ Project Structure

The repository currently includes the main Streamlit app, supporting Python modules, requirements, and the model directory. After adding the screenshots from this README package, the relevant structure can look like this:

```text
HR-Attrition-IQ/
├── app.py
├── main.py
├── requirements.txt
├── src/
├── models/
│   └── attrition_model.pkl
├── assets/
│   └── dashboard/
│       ├── executive-overview.jpg
│       ├── attrition-drivers.jpg
│       └── risk-segmentation-action-list.jpg
├── .gitignore
└── README.md
```

Keep any additional files already present in your repository. The tree above highlights the key application and screenshot files; it is not intended to replace your actual repository structure.

## ⚙️ Installation and Local Setup

### Prerequisites
- Python version compatible with the packages in `requirements.txt`
- Git
- Access to the Snowflake data source if you want to use the live database-backed features

### 1. Clone the repository

```bash
git clone https://github.com/yashchaudhari372-lab/HR-Attrition-IQ.git
cd HR-Attrition-IQ
```

### 2. Create and activate a virtual environment

**Windows PowerShell**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Snowflake

Create a local `.env` file or configure environment variables in your deployment platform's secrets manager. Use the variable names expected by your application:

```dotenv
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
```

The application is documented to query the `hr_attrition_final` table in the configured database and schema. Confirm the table name and column availability in your environment before running the dashboard.

**Security:** Never commit `.env`, passwords, tokens, private keys, or confidential employee exports. Use a read-only Snowflake role with only the permissions required by the app, and use Streamlit secrets or your host's secret manager in deployment.

### 5. Run the Streamlit app

```bash
streamlit run app.py
```

Open the local address shown in the terminal (usually `http://localhost:8501`).

## 🚀 Deployment

The project is deployed using Streamlit Community Cloud.

**Live app:** [HR Attrition IQ](https://hr-attrition-iq-fz7cy8ubamq9xq3jff4qib.streamlit.app/)

For a deployment or redeployment:
1. Push the application code and required public assets to GitHub.
2. Configure the Snowflake credentials and other required settings through deployment secrets.
3. Ensure the model artifact is present at the path expected by the application.
4. Install packages from `requirements.txt`.
5. Test database connectivity, navigation, filters, visualizations, predictions, and exports in the deployed environment.

## 🧪 Validation Checklist

- [ ] Snowflake connection works with the intended read-only permissions.
- [ ] Missing credentials and empty query results produce helpful messages.
- [ ] Each dashboard page opens correctly.
- [ ] Filters update the relevant metrics, charts, tables, and exports.
- [ ] Charts handle empty or small filtered datasets.
- [ ] The model loads from the expected path.
- [ ] Prediction inputs use the saved encoders and exact expected feature order.
- [ ] CSV, Excel, and PDF exports open and match the selected data scope.
- [ ] No secrets or confidential employee information are exposed in the repository or logs.
- [ ] Any reported model metrics come from a documented held-out evaluation.

## ⚠️ Responsible Use and Limitations

- Dashboard associations are descriptive and do not establish causation.
- Risk segments should be used to guide supportive review, not to label employees as certain to leave.
- Do not use protected characteristics or proxy variables to make unfair employment decisions.
- Validate model performance, calibration, and potential bias before operational use.
- Keep employee data private and restrict access to authorized users.
- Human review, employee context, and appropriate HR processes should remain central to any retention action.

## 🔮 Potential Future Improvements

- Add a documented model evaluation report with precision, recall, F1-score, ROC-AUC, and confusion matrix.
- Add model calibration and subgroup fairness checks.
- Include time-based attrition trends and data-quality monitoring.
- Provide transparent explanations for individual predictions where supported by the model.
- Add configurable retention recommendations reviewed by HR stakeholders.
- Expand automated tests for filters, data access, model inputs, and downloads.

## 👨‍💻 Project Links

- **Live Dashboard:** [HR Attrition IQ](https://hr-attrition-iq-fz7cy8ubamq9xq3jff4qib.streamlit.app/)
- **GitHub Repository:** [HR-Attrition-IQ](https://github.com/yashchaudhari372-lab/HR-Attrition-IQ)

---

⭐ If you find this project useful, consider starring the repository and sharing feedback or suggestions.
