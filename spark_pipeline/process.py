import os
import sys

print("Python executable:", sys.executable)
print("Exists:", os.path.exists(sys.executable))

# ── Java & Spark Configuration ─────────────────────────
os.environ["JAVA_HOME"] = (
    r"C:/Users/ANSHIKA PANDIT/AppData/Local/Programs/Eclipse Adoptium/jdk-17.0.19.10-hotspot"
)

os.environ["PATH"] = (
    os.environ["JAVA_HOME"] + r"/bin"
    + os.pathsep
    + os.environ["PATH"]
)

os.environ["SPARK_HOME"] = (
    r"C:/Users/ANSHIKA PANDIT/LocalDesktop/instagram-creator_co-pilot"
    r"/ai_env/Lib/site-packages/pyspark"
)

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# ── Imports ────────────────────────────────────────────
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, udf
from pyspark.sql.types import StringType, FloatType

# ── Start Spark ────────────────────────────────────────
spark = (
    SparkSession.builder
    .appName("CreatorCopilot")
    .config("spark.driver.memory", "4g")
    .config("spark.sql.shuffle.partitions", "4")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")
print("✅ Spark session started!")

# ── Load Data ──────────────────────────────────────────
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

data_path = os.path.join(
    base_dir,
    "data",
    "Instagram_Analytics.csv"
)

output_path = os.path.join(
    base_dir,
    "data",
    "processed_data.csv"
)

print(f"📂 Loading data from: {data_path}")
print(f"📂 File exists: {os.path.exists(data_path)}")

df = spark.read.csv(
    data_path,
    header=True,
    inferSchema=True
)

print(f"✅ Data loaded: {df.count()} rows, {len(df.columns)} columns")

# ── Feature Engineering ────────────────────────────────

# 1. Creator Tier
def get_tier(followers):
    if followers is None:
        return "Unknown"
    elif followers < 10000:
        return "Nano"
    elif followers < 100000:
        return "Micro"
    elif followers < 500000:
        return "Mid"
    elif followers < 1000000:
        return "Macro"
    else:
        return "Mega"

tier_udf = udf(get_tier, StringType())

df = df.withColumn(   #adding a new column called creator_tier to the dataframe df by applying the tier_udf function to the follower_count column. The tier_udf function categorizes
    "creator_tier",
    tier_udf(col("follower_count"))
)

# 2. Engagement Rate Bucket
df = df.withColumn(
    "engagement_bucket",
    when(col("engagement_rate") < 0.01, "very_low")
    .when(col("engagement_rate") < 0.03, "low")
    .when(col("engagement_rate") < 0.06, "medium")
    .when(col("engagement_rate") < 0.10, "high")
    .otherwise("very_high")
)

# 3. Is Weekend Flag
df = df.withColumn(
    "is_weekend",
    when(
        col("day_of_week").isin("Saturday", "Sunday"),
        1
    ).otherwise(0)
)

# 4. Caption Length Bucket
df = df.withColumn(
    "caption_bucket",
    when(col("caption_length") < 50, "short")
    .when(col("caption_length") < 150, "medium")
    .otherwise("long")
)

# 5. Hashtag Bucket
df = df.withColumn(
    "hashtag_bucket",
    when(col("hashtags_count") == 0, "none")
    .when(col("hashtags_count") <= 5, "few")
    .when(col("hashtags_count") <= 15, "moderate")
    .otherwise("many")
)

# 6. Save Ratio
df = df.withColumn(
    "save_ratio",
    (col("saves") / (col("reach") + 1)).cast(FloatType())
)

# 7. Share Ratio
df = df.withColumn(
    "share_ratio",
    (col("shares") / (col("reach") + 1)).cast(FloatType())
)

# 8. Post Hour Bucket
df = df.withColumn(
    "hour_bucket",
    when(col("post_hour").between(6, 9), "early_morning")
    .when(col("post_hour").between(10, 12), "morning")
    .when(col("post_hour").between(13, 16), "afternoon")
    .when(col("post_hour").between(17, 20), "evening")
    .when(col("post_hour").between(21, 23), "night")
    .otherwise("late_night")
)

print("✅ Feature engineering done!")
print("   New columns created successfully.")

# ── Sample Output ──────────────────────────────────────
print("\n📊 Sample output:")

df.select(
    "follower_count",
    "creator_tier",
    "media_type",
    "content_category",
    "engagement_rate",
    "engagement_bucket",
    "is_weekend",
    "hour_bucket",
    "performance_bucket_label"
).show(5, truncate=False)

# ── Basic Statistics ───────────────────────────────────
print("📊 Performance bucket distribution:")

df.groupBy(
    "performance_bucket_label"
).count().orderBy(
    "count"
).show()

print("📊 Engagement by media type:")

df.groupBy(
    "media_type"
).avg(
    "engagement_rate"
).orderBy(
    "avg(engagement_rate)",
    ascending=False
).show()

print("📊 Engagement by content category:")

df.groupBy(
    "content_category"
).avg(
    "engagement_rate"
).orderBy(
    "avg(engagement_rate)",
    ascending=False
).show()

print("📊 Best posting hours:")

df.groupBy(
    "hour_bucket"
).avg(
    "engagement_rate"
).orderBy(
    "avg(engagement_rate)",
    ascending=False
).show()

# ── Save Processed Data ────────────────────────────────
print("💾 Saving processed data...")

df.toPandas().to_csv(
    output_path,
    index=False
)

print(f"✅ Saved to: {output_path}")

# ── Stop Spark ─────────────────────────────────────────
spark.stop()

print("✅ Spark session stopped!")
print("\n🎉 Pipeline complete! Ready for ML model training.")