import os
import warnings
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from xgboost import XGBRegressor

import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

print("Loading dataset...")

# --------------------------------------------------
# Paths
# --------------------------------------------------

base_dir = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

data_path = os.path.join(
    base_dir,
    "data",
    "processed_prepost.csv"
)

# --------------------------------------------------
# Load Data
# --------------------------------------------------

df = pd.read_csv(data_path)

print(f"Original Shape: {df.shape}")

# --------------------------------------------------
# Filter to Instagram Only
# --------------------------------------------------

print(f"\nPlatform breakdown before filtering:")
print(df['Platform'].value_counts())

df = df[df['Platform'] == 'Instagram'].copy()

print(f"\nShape after filtering to Instagram only: {df.shape}")

# --------------------------------------------------
# Remove Leakage / Unnecessary Columns
# --------------------------------------------------

drop_cols = [
    'Post_ID',
    'Timestamp',
    'Likes',
    'Comments',
    'Shares',
    'Views',
    'Saves',
    'Influencer_Tier',
    'verified_flag',
    'media_flag',
    'creator_tier',
    'engagement_bucket',
    'Platform'  # constant now (all Instagram) - carries no signal
]

df.drop(
    columns=drop_cols,
    inplace=True,
    errors='ignore'
)

print(f"Shape after cleaning: {df.shape}")

# --------------------------------------------------
# Target Cleaning
# --------------------------------------------------

print("\nOriginal Engagement Rate Stats:")
print(df['Engagement_Rate'].describe())

upper_limit = df['Engagement_Rate'].quantile(0.99)

print(f"\n99th Percentile Cap: {upper_limit:.2f}")

df['Engagement_Rate'] = df['Engagement_Rate'].clip(
    upper=upper_limit
)

df['Engagement_Rate'] = np.log1p(
    df['Engagement_Rate']
)

print("\nAfter Clipping + Log Transform:")
print(df['Engagement_Rate'].describe())

# --------------------------------------------------
# Encode Categoricals
# --------------------------------------------------

categorical_cols = [
    'Content_Type',
    'Category',
    'Day_of_Week',
    'Sentiment',
    'hour_bucket',
    'hashtag_bucket',
    'content_length_bucket'
]

encoders = {}

for col in categorical_cols:

    le = LabelEncoder()

    df[col] = le.fit_transform(
        df[col].astype(str)
    )

    encoders[col] = le

# --------------------------------------------------
# Features
# --------------------------------------------------

features = [
    'Content_Type',
    'Category',
    'Follower_Count',
    'Hour_of_Day',
    'Day_of_Week',
    'Hashtag_Count',
    'Content_Length',
    'Sentiment',
    'Has_Media',
    'Is_Verified',
    'is_weekend',
    'hour_bucket',
    'hashtag_bucket',
    'content_length_bucket'
]

target = 'Engagement_Rate'

X = df[features]
y = df[target]

# --------------------------------------------------
# Train Test Split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print(f"\nTrain Shape: {X_train.shape}")
print(f"Test Shape : {X_test.shape}")

# --------------------------------------------------
# Train Model
# --------------------------------------------------

print("\nTraining XGBoost Regressor...")

model = XGBRegressor(
    n_estimators=500,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    objective='reg:squarederror'
)

model.fit(
    X_train,
    y_train
)

print("Model Trained!")

# --------------------------------------------------
# Predictions
# --------------------------------------------------

preds = model.predict(X_test)

# --------------------------------------------------
# Metrics (log scale)
# --------------------------------------------------

mae = mean_absolute_error(y_test, preds)
rmse = np.sqrt(mean_squared_error(y_test, preds))
r2 = r2_score(y_test, preds)

print("\n==============================")
print("MODEL PERFORMANCE (log scale)")
print("==============================")
print(f"MAE  : {mae:.4f}")
print(f"RMSE : {rmse:.4f}")
print(f"R²   : {r2:.4f}")

# --------------------------------------------------
# Metrics back on ORIGINAL engagement rate scale
# --------------------------------------------------
# log1p was applied to the target, so we reverse it with expm1
# to report errors in real, interpretable engagement % terms.

y_test_original = np.expm1(y_test)
preds_original = np.expm1(preds)

mae_original = mean_absolute_error(y_test_original, preds_original)
rmse_original = np.sqrt(mean_squared_error(y_test_original, preds_original))

print("\n==============================")
print("MODEL PERFORMANCE (original % scale)")
print("==============================")
print(f"MAE  : {mae_original:.4f} engagement rate points")
print(f"RMSE : {rmse_original:.4f} engagement rate points")

# --------------------------------------------------
# Feature Importance
# --------------------------------------------------

importance_df = pd.DataFrame({
    'Feature': features,
    'Importance': model.feature_importances_
}).sort_values(
    by='Importance',
    ascending=False
)

print("\nTop Features:")
print(importance_df)

# --------------------------------------------------
# Feature Importance Plot
# --------------------------------------------------

plt.figure(figsize=(10, 6))

plt.barh(
    importance_df['Feature'][::-1],
    importance_df['Importance'][::-1],
    color='#ff9248'
)

plt.title('Feature Importance - Pre-Post Model (Instagram only)')
plt.xlabel('Importance Score')
plt.tight_layout()

plt.savefig(
    os.path.join(
        base_dir,
        'ml_model',
        'feature_importance_regression.png'
    )
)

plt.show()

# --------------------------------------------------
# Save Model
# --------------------------------------------------

model_path = os.path.join(
    base_dir,
    'ml_model',
    'model_prepost_regression.pkl'
)

encoder_path = os.path.join(
    base_dir,
    'ml_model',
    'encoders_prepost_regression.pkl'
)

joblib.dump(model, model_path)
joblib.dump(encoders, encoder_path)

print("\nModel Saved Successfully!")
print(f"Model: {model_path}")
print(f"Encoders: {encoder_path}")

print("\nNOTE for README:")
print("This model is trained on Instagram-only rows from the")
print("multi-platform dataset, after discovering that 'Platform'")
print("was dominating feature importance due to scale differences")
print("between TikTok/LinkedIn/Instagram engagement rates.")