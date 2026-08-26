# src/02_data_quality_benford.py
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# 1. Crear / Obtener Sesión de Spark
spark = SparkSession.builder.appName(
    "PaySim_DataQuality_Benford").getOrCreate()

# ==============================================================================
# PARTE 1: Filtrado GIGO y Feature Engineering (PySpark)
# ==============================================================================
# Cargar la tabla Delta inicial
df = spark.table("workspace.default.paysim_raw_delta")

# Regla GIGO: Filtrar transacciones con monto mayor a cero
df_clean = df.filter(F.col("amount") > 0)

# Feature Engineering: Inconsistencias de balance
df_features = df_clean \
    .withColumn("error_balance_orig", F.col("new_balance_orig") + F.col("amount") - F.col("old_balance_orig")) \
    .withColumn("error_balance_dest", F.col("old_balance_dest") + F.col("amount") - F.col("new_balance_dest"))

# Guardar como segunda Tabla Delta optimizada
df_features.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("workspace.default.paysim_features_delta")

print("✅ Filtrado GIGO y Feature Engineering completados exitosamente.")

# ==============================================================================
# PARTE 2: Análisis Ley de Benford (Spark SQL)
# ==============================================================================
benford_query = """
WITH first_digits AS (
    SELECT 
        CAST(SUBSTRING(CAST(amount AS STRING), 1, 1) AS INT) AS first_digit
    FROM workspace.default.paysim_features_delta
    WHERE amount >= 10
)
SELECT 
    first_digit,
    COUNT(*) AS total_count,
    ROUND((COUNT(*) * 100.0 / SUM(COUNT(*)) OVER()), 2) AS observed_percentage,
    ROUND((LOG10(1 + 1.0 / first_digit) * 100), 2) AS benford_expected_percentage
FROM first_digits
WHERE first_digit BETWEEN 1 AND 9
GROUP BY first_digit
ORDER BY first_digit;
"""

df_benford = spark.sql(benford_query)
df_benford.show()

print("✅ Análisis de la Ley de Benford ejecutado correctamente.")
