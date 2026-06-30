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

base_dir = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

data_path = os.path.join(
    base_dir,
    "data",
    "social_media_engagement_dataset.csv"
)

output_path = os.path.join(
    base_dir,
    "data",
    "processed_prepost.csv"
)

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

spark = SparkSession.builder \
    .appName("CreatorCoPilot_PrePost") \
    .getOrCreate()

print("Spark Session Created")

# --------------------------------------------------
# Load Dataset
# --------------------------------------------------

df = spark.read.csv(
    "../data/social_media_engagement_dataset.csv",
    header=True,
    inferSchema=True
)

print("Original Shape:")
print((df.count(), len(df.columns)))

# --------------------------------------------------
# Remove Nulls
# --------------------------------------------------

df = df.dropna()

# --------------------------------------------------
# Feature Engineering
# --------------------------------------------------

# Weekend Flag

df = df.withColumn(
    "is_weekend",
    when(
        col("Day_of_Week").isin(["Saturday", "Sunday"]),
        1
    ).otherwise(0)
)

# Morning / Afternoon / Evening / Night

df = df.withColumn(
    "hour_bucket",
    when(col("Hour_of_Day") < 6, "Night")
    .when(col("Hour_of_Day") < 12, "Morning")
    .when(col("Hour_of_Day") < 18, "Afternoon")
    .otherwise("Evening")
)

# Hashtag Bucket

df = df.withColumn(
    "hashtag_bucket",
    when(col("Hashtag_Count") <= 5, "Low")
    .when(col("Hashtag_Count") <= 15, "Medium")
    .otherwise("High")
)

# Content Length Bucket

df = df.withColumn(
    "content_length_bucket",
    when(col("Content_Length") < 50, "Short")
    .when(col("Content_Length") < 150, "Medium")
    .otherwise("Long")
)

# Verification Flag

df = df.withColumn(
    "verified_flag",
    when(col("Is_Verified") == True, 1)
    .otherwise(0)
)

# Media Flag

df = df.withColumn(
    "media_flag",
    when(col("Has_Media") == True, 1)
    .otherwise(0)
)

# --------------------------------------------------
# Creator Tier from Followers
# --------------------------------------------------

df = df.withColumn(
    "creator_tier",
    when(col("Follower_Count") < 10000, "Nano")
    .when(col("Follower_Count") < 50000, "Micro")
    .when(col("Follower_Count") < 500000, "Mid")
    .otherwise("Macro")
)

# --------------------------------------------------
# Engagement Buckets
# (for dashboard analytics)
# --------------------------------------------------

df = df.withColumn(
    "engagement_bucket",
    when(col("Engagement_Rate") < 5, "Low")
    .when(col("Engagement_Rate") < 15, "Medium")
    .when(col("Engagement_Rate") < 30, "High")
    .otherwise("Excellent")
)

# --------------------------------------------------
# Save Processed Dataset
# --------------------------------------------------

# --------------------------------------------------
# Save Processed Dataset
# --------------------------------------------------

output_path = os.path.join(
    base_dir,
    "data",
    "processed_prepost.csv"
)

print("\nSaving processed dataset...")
print("\nFinal Dataset Shape:")
print((df.count(), len(df.columns)))

df.printSchema()

try:
    pdf = df.toPandas()

    pdf.to_csv(
        output_path,
        index=False
    )

    print(f"Saved successfully!")
    print(f"Location: {output_path}")

except Exception as e:
    print("Error while saving:")
    print(e)