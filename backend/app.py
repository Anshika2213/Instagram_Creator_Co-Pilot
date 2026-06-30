import os
import sys
import joblib
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from caption_analyzer import analyze_caption
print("✅ NLP analyzer loaded!")

app = Flask(__name__)
CORS(app)

# ── Paths ─────────────────────────────────────────────
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ml_dir = os.path.join(base_dir, 'ml_model')

# ── Load Model B (Post-Performance Classifier) ────────
print("Loading Model B (Post-Performance Classifier)...")
model_b = joblib.load(os.path.join(ml_dir, 'model.pkl'))
encoders_b = joblib.load(os.path.join(ml_dir, 'encoders.pkl'))
target_encoder_b = joblib.load(os.path.join(ml_dir, 'target_encoder.pkl'))
print("✅ Model B loaded!")

# ── Load Model A (Pre-Post Engagement Predictor) ──────
print("Loading Model A (Pre-Post Engagement Predictor)...")
model_a = joblib.load(os.path.join(ml_dir, 'model_prepost_regression.pkl'))
encoders_a = joblib.load(os.path.join(ml_dir, 'encoders_prepost_regression.pkl'))
print("✅ Model A loaded!")

#------json---
insights_path = os.path.join(ml_dir, 'insights.json')
with open(insights_path, 'r') as f:
    insights = json.load(f)
print("✅ Insights loaded!")

# ── Helper: encode a value safely ─────────────────────
def safe_encode(encoder, value):
    classes = list(encoder.classes_)
    if value in classes:
        return encoder.transform([value])[0]
    return 0  # default to first class if unseen

# ── Helper: get Model B suggestions ───────────────────
def get_model_b_suggestions(input_data, prediction, probabilities, class_names):
    suggestions = []
    warnings_list = []

    save_ratio = input_data.get('save_ratio', 0)
    share_ratio = input_data.get('share_ratio', 0)
    like_ratio = input_data.get('like_ratio', 0)
    comment_ratio = input_data.get('comment_ratio', 0)
    ctr = input_data.get('ctr', 0)
    hashtags = input_data.get('hashtags_count', 0)
    media_type = input_data.get('media_type', '')
    has_cta = input_data.get('has_call_to_action', 0)
    hour = input_data.get('post_hour', 12)
    day = input_data.get('day_of_week', 'Monday')

    # Save ratio analysis
    if save_ratio < 0.003:
        warnings_list.append("⚠️ Save ratio is very low — people aren't finding your content valuable enough to save")
        suggestions.append("💡 Add 'how-to', 'tips', or 'educational' format — these get 3x more saves")
    elif save_ratio >= 0.008:
        suggestions.append("✅ Strong save ratio — your content is being bookmarked, great sign!")

    # Share ratio analysis
    if share_ratio < 0.002:
        warnings_list.append("⚠️ Share ratio is low — nobody is DMing this to friends")
        suggestions.append("💡 Add a relatable hook in the first 2 seconds to trigger shares")
    elif share_ratio >= 0.005:
        suggestions.append("✅ Strong share ratio — your content is being sent to others!")

    # Like ratio analysis
    if like_ratio < 0.02:
        warnings_list.append("⚠️ Like ratio is below average — your content isn't getting strong initial reactions")
        suggestions.append("💡 Try a stronger thumbnail or opening line to grab attention immediately")

    # CTR analysis
    if ctr < 0.5:
        warnings_list.append("⚠️ Low CTR — your impressions aren't converting to real reach")
        suggestions.append("💡 Improve your caption hook and first frame to make people stop scrolling")

    # Hashtag suggestions
    if hashtags == 0:
        suggestions.append("💡 Add 5-10 relevant hashtags — you're missing discoverability")
    elif hashtags < 5:
        suggestions.append("💡 Try using 8-12 hashtags for better reach in your niche")
    elif hashtags > 15:
        suggestions.append("💡 Consider reducing hashtags to 8-12 — too many can look spammy")
    else:
        suggestions.append("✅ Hashtag count looks good!")

    # CTA analysis
    if has_cta == 0:
        suggestions.append("💡 Add a Call-to-Action ('Save this!', 'Share with a friend') — it measurably improves engagement")

    # Media type
    if media_type == 'image':
        suggestions.append("💡 Consider switching to Reel format — Reels get higher reach on average in this dataset")

    # Posting time
    if hour not in [21, 22, 23, 17, 18, 19, 20]:
        suggestions.append(f"💡 You posted at {hour}:00 — late night (9PM-11PM) and evening (5PM-8PM) tend to perform better")

    # If performing well
    if prediction in ['viral', 'high']:
        suggestions.insert(0, "🔥 This post is performing well! Key things to replicate in future posts:")

    return warnings_list, suggestions

# ── Helper: get Model A suggestions ───────────────────
def get_model_a_suggestions(input_data, predicted_engagement):
    suggestions = []
    hashtags = input_data.get('hashtags_count', 0)
    hour = input_data.get('post_hour', 12)
    content_type = input_data.get('content_type', '')
    sentiment = input_data.get('sentiment', '')
    category = input_data.get('category', '')

    # ── Best posting hours (data-derived) ────────────
    best_hours = insights.get('best_hours', {})
    niche_hours = best_hours.get(category, [19, 20, 21])
    if hour not in niche_hours:
        suggestions.append(
            f"⏰ Data shows best posting hours for {category}: "
            f"{niche_hours[0]}:00, {niche_hours[1]}:00, {niche_hours[2]}:00"
        )
    else:
        suggestions.append(f"✅ You're posting at a proven high-engagement hour for {category}!")

    # ── Best day (data-derived) ───────────────────────
    best_days = insights.get('best_days', {})
    niche_days = best_days.get(category, ['Saturday', 'Sunday'])
    day = input_data.get('day_of_week', '')
    if day in niche_days:
        suggestions.append(f"✅ {day} is one of the best days for {category} content!")
    else:
        suggestions.append(
            f"📅 Data shows {category} posts perform best on: {', '.join(niche_days)}"
        )

    # ── Best hashtag range (data-derived) ────────────
    best_hashtags = insights.get('best_hashtags', {})
    niche_hashtag_range = best_hashtags.get(category, 'moderate')

    hashtag_map = {
        'none': (0, 0, "Data shows {cat} posts perform better with NO hashtags — try going without"),
        'few': (1, 5, "Data shows {cat} posts perform best with 1-5 hashtags"),
        'moderate': (6, 15, "Data shows {cat} posts perform best with 6-15 hashtags"),
        'many': (16, 30, "Data shows {cat} posts perform best with 16-30 hashtags")
    }

    bucket_info = hashtag_map.get(niche_hashtag_range, hashtag_map['moderate'])
    low, high, msg = bucket_info
    msg = msg.replace('{cat}', category)

    if niche_hashtag_range == 'none' and hashtags == 0:
        suggestions.append(f"✅ {msg}")
    elif low <= hashtags <= high:
        suggestions.append(f"✅ Your hashtag count ({hashtags}) is in the optimal range for {category}!")
    else:
        suggestions.append(f"💡 {msg} (you used {hashtags})")

    # ── Best media type (data-derived) ───────────────
    best_media = insights.get('best_media', {})
    niche_media = best_media.get(category, 'reel')

    if content_type.lower() == niche_media.lower():
        suggestions.append(f"✅ {content_type.capitalize()} is the top-performing format for {category}!")
    else:
        suggestions.append(
            f"💡 Data shows {niche_media.capitalize()} performs best for {category} "
            f"(you chose {content_type.capitalize()})"
        )

    # ── Sentiment ─────────────────────────────────────
    if sentiment == 'Negative':
        suggestions.append("⚠️ Negative sentiment tends to reduce engagement — consider a more positive angle")
    elif sentiment == 'Positive':
        suggestions.append("✅ Positive sentiment — generally performs better for engagement")

    # ── Engagement interpretation ─────────────────────
    if predicted_engagement < 2.0:
        suggestions.append("📊 Predicted engagement is below average — apply the suggestions above before posting")
    elif predicted_engagement < 5.0:
        suggestions.append("📊 Predicted engagement is average — small tweaks could push it higher")
    else:
        suggestions.append("📊 Predicted engagement looks strong — your strategy is well-targeted!")

    return suggestions

#-----test route----
@app.route("/test")
def test():
    return {
        "message": "Backend Connected Successfully"
    }

# ══════════════════════════════════════════════════════
# ROUTE 1: Health check
# ══════════════════════════════════════════════════════
@app.route('/', methods=['GET'])
def health():
    return jsonify({
        "status": "✅ Instagram Creator Co-Pilot API is running!",
        "models": {
            "model_a": "Pre-Post Engagement Predictor (regression)",
            "model_b": "Post-Performance Classifier (classification)"
        },
        "endpoints": {
            "POST /predict-prepost": "Predict engagement before posting",
            "POST /predict-performance": "Analyze post performance after posting"
        }
    })

# ══════════════════════════════════════════════════════
# ROUTE 2: Model A — Pre-Post Predictor
# ══════════════════════════════════════════════════════
@app.route('/predict-prepost', methods=['POST'])
def predict_prepost():
    try:
        data = request.get_json()

        # ── NLP Auto-extraction ───────────────────────
        caption = data.get('caption', '')
        hashtags_input = data.get('hashtags_text', '')

        # Parse hashtags from text
        import re
        hashtag_list = re.findall(r'#\w+', hashtags_input.lower())

        # Auto-extract features using NLP
        if caption:
            nlp_result = analyze_caption(caption, hashtag_list, data.get('category', ''))

            # Override manual inputs with NLP-extracted values
            auto_sentiment = nlp_result['sentiment']['label']
            auto_caption_length = len(caption.split())
            auto_hashtags_count = len(hashtag_list)
            caption_quality = nlp_result['caption_quality']
            hashtag_analysis = nlp_result['hashtag_analysis']
        else:
            # Fall back to manual inputs if no caption provided
            auto_sentiment = data.get('sentiment', 'Neutral')
            auto_caption_length = int(data.get('caption_length', 120))
            auto_hashtags_count = int(data.get('hashtags_count', 5))
            caption_quality = None
            hashtag_analysis = None

        # Build feature row using auto-extracted values
        row = {
            'Content_Type': data.get('content_type', 'image'),
            'Category': data.get('category', 'Lifestyle'),
            'Follower_Count': float(data.get('follower_count', 5000)),
            'Hour_of_Day': int(data.get('post_hour', 12)),
            'Day_of_Week': data.get('day_of_week', 'Monday'),
            'Hashtag_Count': auto_hashtags_count,  # from NLP
            'Content_Length': auto_caption_length,  # from NLP
            'Sentiment': auto_sentiment,             # from NLP
            'Has_Media': int(data.get('has_media', 1)),
            'Is_Verified': int(data.get('is_verified', 0)),
            'is_weekend': 1 if data.get('day_of_week', 'Monday') in ['Saturday', 'Sunday'] else 0,
            'hour_bucket': (
                'early_morning' if 6 <= int(data.get('post_hour', 12)) <= 9 else
                'morning' if 10 <= int(data.get('post_hour', 12)) <= 12 else
                'afternoon' if 13 <= int(data.get('post_hour', 12)) <= 16 else
                'evening' if 17 <= int(data.get('post_hour', 12)) <= 20 else
                'night' if 21 <= int(data.get('post_hour', 12)) <= 23 else
                'late_night'
            ),
            'hashtag_bucket': (
                'none' if auto_hashtags_count == 0 else
                'few' if auto_hashtags_count <= 5 else
                'moderate' if auto_hashtags_count <= 15 else
                'many'
            ),
            'content_length_bucket': (
                'short' if auto_caption_length < 50 else
                'medium' if auto_caption_length < 150 else
                'long'
            )
        }

        # Encode categoricals
        categorical_cols = [
            'Content_Type', 'Category', 'Day_of_Week',
            'Sentiment', 'hour_bucket', 'hashtag_bucket',
            'content_length_bucket'
        ]
        for col in categorical_cols:
            if col in encoders_a:
                row[col] = safe_encode(encoders_a[col], row[col])

        # Predict
        features = [
            'Content_Type', 'Category', 'Follower_Count',
            'Hour_of_Day', 'Day_of_Week', 'Hashtag_Count',
            'Content_Length', 'Sentiment', 'Has_Media',
            'Is_Verified', 'is_weekend', 'hour_bucket',
            'hashtag_bucket', 'content_length_bucket'
        ]

        input_df = pd.DataFrame([row])[features]
        log_pred = model_a.predict(input_df)[0]
        predicted_engagement = float(np.expm1(log_pred))
        predicted_engagement = round(predicted_engagement, 2)

        suggestions = get_model_a_suggestions(data, predicted_engagement)

        # Build response
        response = {
            "model": "Model A — Pre-Post Predictor",
            "predicted_engagement_rate": predicted_engagement,
            "predicted_engagement_display": f"{predicted_engagement:.1f}%",
            "interpretation": (
                "Below average" if predicted_engagement < 2 else
                "Average" if predicted_engagement < 5 else
                "Above average" if predicted_engagement < 10 else
                "High"
            ),
            "disclaimer": "Engagement rate scale reflects dataset distribution — use as relative comparison",
            "auto_extracted": {
                "sentiment": auto_sentiment,
                "caption_length": auto_caption_length,
                "hashtags_count": auto_hashtags_count
            },
            "suggestions": suggestions
        }

        # Add NLP results if caption was provided
        if caption_quality:
            response["caption_quality"] = caption_quality
        if hashtag_analysis:
            response["hashtag_analysis"] = hashtag_analysis

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ══════════════════════════════════════════════════════
# ROUTE 3: Model B — Post-Performance Analyzer
# ══════════════════════════════════════════════════════
@app.route('/predict-performance', methods=['POST'])
def predict_performance():
    try:
        data = request.get_json()

        # Compute ratios from raw engagement
        likes = float(data.get('likes', 0))
        comments = float(data.get('comments', 0))
        shares = float(data.get('shares', 0))
        saves = float(data.get('saves', 0))
        reach = float(data.get('reach', 1))
        impressions = float(data.get('impressions', 1))
        follower_count = float(data.get('follower_count', 5000))
        hashtags_count = int(data.get('hashtags_count', 5))
        post_hour = int(data.get('post_hour', 12))
        caption_length = int(data.get('caption_length', 120))

        save_ratio = saves / (reach + 1)
        share_ratio = shares / (reach + 1)
        like_ratio = likes / (reach + 1)
        comment_ratio = comments / (reach + 1)
        ctr = reach / (impressions + 1)
        engagement_per_follower = (likes + comments + shares + saves) / (follower_count + 1)
        total_engagement = likes + comments + shares + saves
        engagement_rate = total_engagement / (follower_count + 1)

        # Build feature row
        row = {
            'follower_count': follower_count,
            'media_type': data.get('media_type', 'image'),
            'content_category': data.get('content_category', 'Lifestyle'),
            'traffic_source': data.get('traffic_source', 'Home Feed'),
            'has_call_to_action': int(data.get('has_call_to_action', 0)),
            'post_hour': post_hour,
            'is_weekend': 1 if data.get('day_of_week', 'Monday') in ['Saturday', 'Sunday'] else 0,
            'caption_length': caption_length,
            'hashtags_count': hashtags_count,
            'save_ratio': save_ratio,
            'share_ratio': share_ratio,
            'like_ratio': like_ratio,
            'comment_ratio': comment_ratio,
            'engagement_per_follower': engagement_per_follower,
            'ctr': ctr,
            'creator_tier': 'Nano' if follower_count < 10000 else 'Micro',
            'caption_bucket': (
                'short' if caption_length < 50 else
                'medium' if caption_length < 150 else
                'long'
            ),
            'hashtag_bucket': (
                'none' if hashtags_count == 0 else
                'few' if hashtags_count <= 5 else
                'moderate' if hashtags_count <= 15 else
                'many'
            ),
            'hour_bucket': (
                'early_morning' if 6 <= post_hour <= 9 else
                'morning' if 10 <= post_hour <= 12 else
                'afternoon' if 13 <= post_hour <= 16 else
                'evening' if 17 <= post_hour <= 20 else
                'night' if 21 <= post_hour <= 23 else
                'late_night'
            ),
            'account_type': data.get('account_type', 'creator')
        }

        # Encode categoricals
        categorical_cols_b = [
            'media_type', 'content_category', 'traffic_source',
            'creator_tier', 'caption_bucket', 'hashtag_bucket',
            'hour_bucket', 'account_type'
        ]

        for col in categorical_cols_b:
            if col in encoders_b:
                row[col] = safe_encode(encoders_b[col], row[col])

        # Features (must match train.py exactly)
        features_b = [
            'follower_count', 'media_type', 'content_category',
            'traffic_source', 'has_call_to_action', 'post_hour',
            'is_weekend', 'caption_length', 'hashtags_count',
            'save_ratio', 'share_ratio', 'like_ratio',
            'comment_ratio', 'engagement_per_follower', 'ctr',
            'creator_tier', 'caption_bucket', 'hashtag_bucket',
            'hour_bucket', 'account_type'
        ]

        input_df = pd.DataFrame([row])[features_b]

        # Predict
        pred_encoded = model_b.predict(input_df)[0]
        pred_proba = model_b.predict_proba(input_df)[0]
        prediction = target_encoder_b.inverse_transform([pred_encoded])[0]
        class_names = list(target_encoder_b.classes_)

        # Probability breakdown
        proba_dict = {
            class_names[i]: round(float(pred_proba[i]) * 100, 1)
            for i in range(len(class_names))
        }

        # Get suggestions
        input_for_suggestions = {
            **data,
            'save_ratio': save_ratio,
            'share_ratio': share_ratio,
            'like_ratio': like_ratio,
            'comment_ratio': comment_ratio,
            'ctr': ctr
        }

        warnings_list, suggestions = get_model_b_suggestions(
            input_for_suggestions, prediction, pred_proba, class_names
        )

        return jsonify({
            "model": "Model B — Post-Performance Analyzer",
            "performance_category": prediction,
            "confidence": f"{max(pred_proba) * 100:.1f}%",
            "probability_breakdown": proba_dict,
            "key_metrics": {
                "save_ratio": round(save_ratio, 4),
                "share_ratio": round(share_ratio, 4),
                "like_ratio": round(like_ratio, 4),
                "comment_ratio": round(comment_ratio, 4),
                "engagement_rate": round(engagement_rate * 100, 2),
                "ctr": round(ctr, 4)
            },
            "warnings": warnings_list,
            "suggestions": suggestions
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ══════════════════════════════════════════════════════
# ROUTE 4: CAPTION SCORING 
# ══════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════
# ROUTE 4: NLP Caption Analyzer
# ══════════════════════════════════════════════════════
# @app.route('/analyze-caption', methods=['POST'])
# def analyze_caption_route():
#     try:
#         data = request.get_json()
#         caption = data.get('caption', '')
#         hashtags = data.get('hashtags', [])
#         category = data.get('category', '')

#         if not caption:
#             return jsonify({"error": "Caption is required"}), 400

#         result = analyze_caption(caption, hashtags, category)

#         return jsonify({
#             "model": "NLP Caption Analyzer",
#             "caption_preview": caption[:100] + "..." if len(caption) > 100 else caption,
#             **result
#         })

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
# ══════════════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════════════
if __name__ == '__main__':
    print("\n🚀 Starting Instagram Creator Co-Pilot API...")
    print("📍 Running on http://localhost:5000")
    print("📍 Health check: http://localhost:5000/")
    print("📍 Pre-post predictor: POST http://localhost:5000/predict-prepost")
    print("📍 Performance analyzer: POST http://localhost:5000/predict-performance")
    app.run(debug=True, port=5000)