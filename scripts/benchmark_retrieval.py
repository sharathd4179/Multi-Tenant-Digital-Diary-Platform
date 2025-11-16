"""
Benchmark script to measure vector retrieval latency.

This script loads FAISS indexes for each tenant and runs a number of random
queries.  It reports the average time taken to perform similarity search over
the HNSW index.  Use this to tune parameters like `efSearch` and `M`.
"""
import argparse
import json
import os
import time
from typing import List

import faiss
import numpy as np


def load_index_and_metadata(tenant_id: str):
    index = faiss.read_index(f"vector_indexes/index_{tenant_id}.faiss")
    with open(f"vector_indexes/metadata_{tenant_id}.pkl", "rb") as f:
        metadata = json.load(f)
    return index, metadata


def benchmark(tenant_id: str, num_queries: int = 100, top_k: int = 5):
    index, metadata = load_index_and_metadata(tenant_id)
    # Generate random query vectors by sampling existing vectors from the index
    all_vectors = index.reconstruct_n(0, index.ntotal)
    total_time = 0.0
    for _ in range(num_queries):
        q = all_vectors[np.random.randint(0, index.ntotal)]
        start = time.time()
        index.search(np.array([q]), top_k)
        total_time += time.time() - start
    avg_time_ms = (total_time / num_queries) * 1000
    print(f"Tenant {tenant_id}: Avg search time for top{top_k} over {num_queries} queries: {avg_time_ms:.2f} ms")


def main():
    parser = argparse.ArgumentParser(description="Benchmark FAISS retrieval")
    parser.add_argument("--tenant-id", required=True, help="Tenant ID to benchmark")
    parser.add_argument("--queries", type=int, default=100, help="Number of queries to run")
    parser.add_argument("--top-k", type=int, default=5, help="Number of nearest neighbours to retrieve")
    args = parser.parse_args()

    benchmark(args.tenant_id, args.queries, args.top_k)


if __name__ == "__main__":
    main()