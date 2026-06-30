import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import xgboost as xgb
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

print("📦 Libraries loaded!")

# ── Load Processed Data ───────────────────────────────
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(base_dir, "data", "processed_data.csv")

df = pd.read_csv(data_path)
print(f"✅ Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")

# Add this RIGHT AFTER loading the data, before feature selection

# ── Additional Engineered Features ────────────────────
df['like_ratio'] = df['likes'] / (df['reach'] + 1)
df['comment_ratio'] = df['comments'] / (df['reach'] + 1)
df['total_engagement'] = df['likes'] + df['comments'] + df['shares'] + df['saves']
df['engagement_per_follower'] = df['total_engagement'] / (df['follower_count'] + 1)
df['ctr'] = df['reach'] / (df['impressions'] + 1)  # how much of impressions converted to reach

print("✅ Added 5 new engineered features")

# ── Select Features ───────────────────────────────────
features = [
    'follower_count',
    'media_type',
    'content_category',
    'traffic_source',
    'has_call_to_action',
    'post_hour',
    'is_weekend',
    'caption_length',
    'hashtags_count',
    'save_ratio',
    'share_ratio',
    'like_ratio',           # NEW
    'comment_ratio',        # NEW
    'engagement_per_follower',  # NEW
    'ctr',                  # NEW
    'creator_tier',
    'caption_bucket',
    'hashtag_bucket',
    'hour_bucket',
    'account_type'
]

target = 'performance_bucket_label'

print(f"\n✅ Features selected: {len(features)}")
print(f"✅ Target: {target}")

# ── Encode Categorical Columns ────────────────────────
df_model = df[features + [target]].copy()

categorical_cols = [
    'media_type', 'content_category', 'traffic_source',
    'creator_tier', 'caption_bucket', 'hashtag_bucket',
    'hour_bucket', 'account_type'
]

encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    df_model[col] = le.fit_transform(df_model[col].astype(str))
    encoders[col] = le
    print(f"   Encoded: {col} → {list(le.classes_)}")

# Encode target
target_encoder = LabelEncoder()
df_model[target] = target_encoder.fit_transform(df_model[target])
print(f"\n✅ Target classes: {list(target_encoder.classes_)}")

# ── Split Data ────────────────────────────────────────
X = df_model[features]
y = df_model[target]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\n✅ Train size: {X_train.shape[0]} rows")
print(f"✅ Test size:  {X_test.shape[0]} rows")

# ── Train XGBoost Model ───────────────────────────────
print("\n🚀 Training XGBoost model...")

model = xgb.XGBClassifier(
    n_estimators=300,
    max_depth=8,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_weight=3,
    gamma=0.1,
    random_state=42,
    eval_metric='mlogloss',
    verbosity=0
)

model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=False
)

print("✅ Model trained!")

# ── Evaluate ──────────────────────────────────────────
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f"\n🎯 Accuracy: {accuracy * 100:.2f}%")

print("\n📊 Classification Report:")
print(classification_report(
    y_test, y_pred,
    target_names=target_encoder.classes_
))

# ── Confusion Matrix ──────────────────────────────────
plt.figure(figsize=(8, 6))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap='Blues',
    xticklabels=target_encoder.classes_,
    yticklabels=target_encoder.classes_
)
plt.title('Confusion Matrix')
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.tight_layout()
plt.savefig(os.path.join(base_dir, 'ml_model', 'confusion_matrix.png'))
plt.show()
print("✅ Confusion matrix saved!")

# ── Feature Importance ────────────────────────────────
plt.figure(figsize=(10, 6))
importance_df = pd.DataFrame({
    'feature': features,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=True)

plt.barh(importance_df['feature'], importance_df['importance'], color='#4d96ff')
plt.title('Feature Importance — What affects post performance?')
plt.xlabel('Importance Score')
plt.tight_layout()
plt.savefig(os.path.join(base_dir, 'ml_model', 'feature_importance.png'))
plt.show()
print("✅ Feature importance chart saved!")

# ── Save Model ────────────────────────────────────────
model_path = os.path.join(base_dir, 'ml_model', 'model.pkl')
encoder_path = os.path.join(base_dir, 'ml_model', 'encoders.pkl')
target_encoder_path = os.path.join(base_dir, 'ml_model', 'target_encoder.pkl')

joblib.dump(model, model_path)
joblib.dump(encoders, encoder_path)
joblib.dump(target_encoder, target_encoder_path)

print(f"\n✅ Model saved to: {model_path}")
print(f"✅ Encoders saved to: {encoder_path}")
print(f"✅ Target encoder saved to: {target_encoder_path}")

print("\n🎉 ML Model training complete! Ready for backend.")