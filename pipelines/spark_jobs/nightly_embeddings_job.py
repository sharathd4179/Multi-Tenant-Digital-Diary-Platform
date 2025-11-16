"""
PySpark job to generate embeddings for new or updated diary notes.

This script demonstrates how to integrate Spark with BigQuery and OpenAI to
compute vector embeddings at scale.  It reads new or updated notes from
BigQuery, splits them into chunks, generates embeddings using the OpenAI
Embeddings API and writes the results back to BigQuery.

Run with:

```
spark-submit --packages com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.28.0 \
    nightly_embeddings_job.py --project=<gcp-project> --dataset=<dataset> --table=notes
```
"""
import argparse
import os
from datetime import datetime
from typing import List

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, udf
from pyspark.sql.types import ArrayType, FloatType, StringType

import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter


def parse_args():
    parser = argparse.ArgumentParser(description="Generate embeddings for notes")
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--dataset", required=True, help="BigQuery dataset name")
    parser.add_argument("--table", default="notes", help="BigQuery table name for notes")
    parser.add_argument("--embedding_table", default="embeddings", help="Destination table for embeddings")
    parser.add_argument("--openai_model", default="text-embedding-ada-002", help="OpenAI embedding model")
    return parser.parse_args()


def get_embedding(text: str, model: str) -> List[float]:
    # Use OpenAI API to generate embeddings
    response = openai.Embedding.create(input=text, model=model)
    return response["data"][0]["embedding"]  # type: ignore


def main():
    args = parse_args()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    spark = SparkSession.builder \
        .appName("NightlyEmbeddingsJob") \
        .getOrCreate()

    # Read notes from BigQuery
    notes_df = spark.read.format("bigquery").option("project", args.project) \
        .option("dataset", args.dataset) \
        .option("table", args.table) \
        .load()

    # Only process notes updated in the last day
    yesterday = datetime.utcnow().timestamp() - 86400
    notes_df = notes_df.filter(col("updated_at").cast("double") > yesterday)

    # Split notes into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)

    def split_text(text: str) -> List[str]:
        if not text:
            return []
        return splitter.split_text(text)

    split_udf = udf(split_text, ArrayType(StringType()))
    exploded_df = notes_df.withColumn("chunks", split_udf(col("content"))) \
        .withColumn("chunk", explode(col("chunks")))

    # Generate embeddings
    embedding_udf = udf(lambda txt: get_embedding(txt, args.openai_model), ArrayType(FloatType()))
    embedded_df = exploded_df.withColumn("embedding", embedding_udf(col("chunk")))

    result_df = embedded_df.select(
        col("id").alias("note_id"),
        col("tenant_id"),
        col("user_id"),
        col("chunk").alias("chunk_text"),
        col("embedding"),
    )

    # Write embeddings back to BigQuery
    result_df.write.format("bigquery").option("project", args.project) \
        .option("dataset", args.dataset) \
        .option("table", args.embedding_table) \
        .mode("append") \
        .save()

    spark.stop()


if __name__ == "__main__":
    main()