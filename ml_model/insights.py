import pandas as pd
import json
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(base_dir, 'data', 'processed_data.csv'))

# Best hour per category — find hour with highest avg engagement rate
best_hours = (
    df.groupby(['content_category', 'post_hour'])['engagement_rate']
    .mean()
    .reset_index()
    .sort_values('engagement_rate', ascending=False)
    .groupby('content_category')
    .apply(lambda x: x.nlargest(3, 'engagement_rate')['post_hour'].tolist())
    .to_dict()
)

# Best day per category
best_days = (
    df.groupby(['content_category', 'day_of_week'])['engagement_rate']
    .mean()
    .reset_index()
    .sort_values('engagement_rate', ascending=False)
    .groupby('content_category')
    .apply(lambda x: x.nlargest(2, 'engagement_rate')['day_of_week'].tolist())
    .to_dict()
)

# Best media type per category
best_media = (
    df.groupby(['content_category', 'media_type'])['engagement_rate']
    .mean()
    .reset_index()
    .sort_values('engagement_rate', ascending=False)
    .groupby('content_category')
    .apply(lambda x: x.iloc[0]['media_type'])
    .to_dict()
)

# Best hashtag count range per category
best_hashtags = (
    df.groupby(['content_category', 'hashtag_bucket'])['engagement_rate']
    .mean()
    .reset_index()
    .sort_values('engagement_rate', ascending=False)
    .groupby('content_category')
    .apply(lambda x: x.iloc[0]['hashtag_bucket'])
    .to_dict()
)

insights = {
    'best_hours': best_hours,
    'best_days': best_days,
    'best_media': best_media,
    'best_hashtags': best_hashtags
}

# Save to a JSON file that Flask will load
output_path = os.path.join(base_dir, 'ml_model', 'insights.json')
with open(output_path, 'w') as f:
    json.dump(insights, f, indent=2)

print("✅ Insights saved!")
print(json.dumps(insights, indent=2))