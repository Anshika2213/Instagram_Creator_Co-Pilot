# Instagram Creator Co-Pilot 🚀

Instagram Creator Co-Pilot is an AI-powered analytics application designed to help Instagram creators make data-driven content decisions. It predicts engagement before posting, analyzes post performance, and evaluates caption quality to suggest improvements.

## ✨ Features

- **Pre-Post Engagement Prediction:** Uses an XGBoost regression model to estimate potential engagement based on content and posting details.
- **Post-Performance Analysis:** Classifies published-post performance and provides metrics, insights, and recommendations.
- **Caption Quality Scorer:** Evaluates captions using NLP-based, rule-driven checks for length, emoji usage, questions, and calls to action.
- **Content Insights:** Provides suggestions to help creators improve their content strategy.

## 🛠️ Tech Stack

- **Frontend:** React, Vite
- **Backend:** Python, Flask, Flask-CORS
- **Machine Learning:** XGBoost, Scikit-learn
- **Data Processing:** PySpark, Pandas, NumPy
- **NLP:** spaCy

## ⚙️ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Anshika2213/Instagram_Creator_Co-Pilot.git
cd Instagram_Creator_Co-Pilot
```

### 2. Set Up the Backend

```bash
python -m venv ai_env
```

Activate the environment on Windows:

```bash
ai_env\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Start the Flask backend using your main application file:

```bash
python app.py
```

### 3. Set Up the Frontend

Open a new terminal and navigate to the frontend directory:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite in your terminal.

## 📁 Project Structure

```text
Instagram_Creator_Co-Pilot/
├── backend/          # Flask APIs and ML integration
├── frontend/         # React application
├── data/             # Datasets and processed data
├── ml_model/         # Model training and saved models
├── spark_pipeline/   # Data preprocessing pipeline
├── notebooks/        # Exploratory data analysis
├── app.py            # Backend application entry point
├── requirements.txt  # Python dependencies
└── README.md
```

## 🎯 Objective

The goal of Instagram Creator Co-Pilot is to help creators understand content performance, evaluate captions, and make more informed posting decisions using machine learning and data analysis.

**Note:** Engagement predictions are estimates based on the available training data and do not guarantee actual Instagram performance.
