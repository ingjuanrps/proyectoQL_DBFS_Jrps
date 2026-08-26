# src/01_ingest_pyspark.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# 1. Sesión de Spark
spark = SparkSession.builder.appName("PaySim_Fraud_Ingestion").getOrCreate()

# 2. Ruta exacta del Volume en Unity Catalog
volume_path = "/Volumes/workspace/default/paysim_volume/paysim.csv"

# 3. Leer CSV masivo con PySpark
df_raw = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load(volume_path)

# 4. Normalizar nombres a snake_case
df_clean = df_raw.select(
    col("step"),
    col("type").alias("transaction_type"),
    col("amount"),
    col("nameOrig").alias("name_orig"),
    col("oldbalanceOrg").alias("old_balance_orig"),
    col("newbalanceOrig").alias("new_balance_orig"),
    col("nameDest").alias("name_dest"),
    col("oldbalanceDest").alias("old_balance_dest"),
    col("newbalanceDest").alias("new_balance_dest"),
    col("isFraud").alias("is_fraud"),
    col("isFlaggedFraud").alias("is_flagged_fraud")
)

# 5. Guardar como Tabla Delta en el catálogo por defecto
df_clean.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("workspace.default.paysim_raw_delta")

print("✅ Ingesta completada. Tabla Delta creada en 'workspace.default.paysim_raw_delta'.")