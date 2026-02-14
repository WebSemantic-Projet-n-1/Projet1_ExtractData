"""
Benchmark script to compare processing times across Web 1.0, RDFa, and Knowledge Graph APIs.

This script sends each of the 10 predefined questions to all 3 API endpoints
(Web 1.0, RDFa, Knowledge Graph) multiple times, collects timing data, and
produces both a terminal summary table and a CSV file for further analysis.

Usage:
    1. Start the FastAPI server:  fastapi dev main.py
    2. Run the benchmark:         python benchmark.py
"""

# --- Standard library imports ---
import csv            # Writing results to CSV files
import time           # High-resolution timing with perf_counter()
import statistics     # Descriptive stats: mean, median, stdev
import json           # (available if JSON export is needed later)
from urllib.parse import quote  # URL-encode French characters (accents, spaces, ?)

# --- Third-party imports ---
import requests       # HTTP client to call the FastAPI endpoints

# Base URL of the locally running FastAPI server
BASE_URL = "http://127.0.0.1:8000"

# The 10 canonical questions used to query each API.
# Keys (R1–R10) are short identifiers; values are the full French question strings.
# These must match the keyword rules defined in each API route handler
# (api_web_1.py, api_rdfa.py, api_knowledge_graph.py).
REQUESTS_QUESTIONS = {
    "R1": "Quelle équipe est première au classement ?",
    "R2": "Combien de matchs ont été joués cette saison ?",
    "R3": "Quel est le nombre total de buts marqués cette saison ?",
    "R4": "Quelle équipe a marqué le plus de buts ?",
    "R5": "Quelles équipes ont marqué plus de 70 buts cette saison ?",
    "R6": "Quels matchs ont eu lieu en novembre 2008 ?",
    "R7": "Combien de victoires à domicile pour Manchester United ?",
    "R8": "Classement des équipes par nombre de victoires à l'extérieur",
    "R9": "Quelle est la moyenne de buts marqués à l'extérieur par les équipes du Top 6 ?",
    "R10": "Quelles sont les confrontations historiques entre le premier et le troisième du championnat (dates, scores, résultats) ?",
}

# Maps a human-readable method name to its API URL path prefix.
# The question string will be appended (URL-encoded) to each prefix.
# Example: Web 1.0 + R1 → GET /api/v1/Quelle%20%C3%A9quipe%20...
API_ENDPOINTS = {
    "Web 1.0": "/api/v1/",
    "RDFa": "/api/rdfa/",
    "Knowledge Graph": "/api/knowledge-graph/",
}


def benchmark(n_iterations: int = 30):
    """
    Core benchmarking function.

    For every combination of (API method × question), sends the HTTP request
    `n_iterations` times and records two timing measurements per call:
      - server_ms: the processing_ms value returned by the API (server-side only,
        measured inside the FastAPI route handler with time.perf_counter())
      - client_ms: the full HTTP round-trip time measured from this script
        (includes network overhead, serialization, etc.)

    Args:
        n_iterations: How many times to repeat each API call. Higher values
                      give more statistically reliable results. 30 is the
                      minimum for meaningful stats (Central Limit Theorem).

    Returns:
        A nested dict structured as:
        results[method_name][question_id] = {
            "server_ms": [float, ...],  # one value per iteration
            "client_ms": [float, ...],  # one value per iteration
        }
    """
    results = {}

    # --- Outer loop: iterate over each web semantic method ---
    for method_name, endpoint in API_ENDPOINTS.items():
        results[method_name] = {}

        # --- Middle loop: iterate over each of the 10 questions ---
        for q_id, question in REQUESTS_QUESTIONS.items():
            server_times = []  # Will hold N server-side processing_ms values
            client_times = []  # Will hold N client-side round-trip ms values

            # --- Inner loop: repeat the same call N times ---
            for i in range(n_iterations):
                # Build the full URL.
                # quote() encodes special characters: spaces → %20,
                # accents → %C3%A9, question marks → %3F, etc.
                url = f"{BASE_URL}{endpoint}{quote(question)}"

                # Measure client-side round-trip time.
                # perf_counter() is the highest-resolution timer available
                # in Python — it uses the OS monotonic clock (not wall clock),
                # so it's immune to system clock adjustments.
                t0 = time.perf_counter()
                response = requests.get(url)
                t1 = time.perf_counter()

                # Convert seconds to milliseconds for readability
                client_ms = (t1 - t0) * 1000

                if response.status_code == 200:
                    # Parse the JSON response from the API.
                    # Expected shape: { "request_question": "...",
                    #                    "datas": [...],
                    #                    "processing_ms": float }
                    data = response.json()

                    # Extract the server-side processing time.
                    # This is the time measured *inside* the API route handler,
                    # excluding HTTP/network overhead.
                    server_times.append(data.get("processing_ms", 0))
                    client_times.append(client_ms)
                else:
                    # Log failed requests but continue — don't let one failure
                    # abort the entire benchmark.
                    print(f"  [WARN] {method_name} / {q_id} iteration {i+1}: HTTP {response.status_code}")

            # Store all collected times for this (method, question) pair
            results[method_name][q_id] = {
                "server_ms": server_times,
                "client_ms": client_times,
            }

            # Progress feedback — printed after each question is fully benchmarked
            print(f"  {method_name} | {q_id}: {n_iterations} iterations done")

    return results


def compute_stats(times: list[float]) -> dict:
    """
    Compute descriptive statistics for a list of timing values (in ms).

    Args:
        times: A list of float values (milliseconds) from repeated measurements.

    Returns:
        A dict with 5 keys:
        - mean:   arithmetic average — primary comparison metric
        - median: middle value — robust against outliers (e.g. cold-start spikes)
        - stdev:  standard deviation — measures consistency/variance across runs.
                  Low stdev = stable performance; high stdev = inconsistent.
        - min:    best-case time observed
        - max:    worst-case time observed

    If the list is empty, returns all zeros to avoid division-by-zero errors.
    """
    if not times:
        return {"mean": 0, "median": 0, "stdev": 0, "min": 0, "max": 0}
    return {
        "mean": round(statistics.mean(times), 3),
        "median": round(statistics.median(times), 3),
        # stdev requires at least 2 data points (it divides by N-1)
        "stdev": round(statistics.stdev(times), 3) if len(times) > 1 else 0,
        "min": round(min(times), 3),
        "max": round(max(times), 3),
    }


def print_comparison_table(results: dict):
    """
    Print a human-readable comparison table to the terminal.

    Shows server-side processing_ms as "mean ± stdev" for each
    (question × method) combination, plus an overall average row.

    This is meant for quick visual inspection; for detailed analysis,
    use export_results_csv().
    """
    print("\n" + "=" * 100)
    print("BENCHMARK RESULTS — Server-side processing_ms (mean ± stdev)")
    print("=" * 100)

    # --- Build the header row ---
    # f-string alignment: '<6' = left-align in 6 chars, '>25' = right-align in 25 chars
    header = f"{'Question':<6}"
    for method in API_ENDPOINTS:
        header += f" | {method:>25}"
    print(header)
    print("-" * 100)

    # --- One row per question (R1 through R10) ---
    for q_id in REQUESTS_QUESTIONS:
        row = f"{q_id:<6}"
        for method in API_ENDPOINTS:
            # Compute stats from the list of server_ms values for this cell
            stats = compute_stats(results[method][q_id]["server_ms"])
            # Format: "  3.45 ±   0.32 ms"
            row += f" | {stats['mean']:>8.2f} ± {stats['stdev']:>6.2f} ms"
        print(row)

    # --- Summary row: global average per method ---
    # Computes the mean of all per-question means for each method.
    # This gives a single number to compare overall method performance.
    print("-" * 100)
    row = f"{'AVG':<6}"
    for method in API_ENDPOINTS:
        all_means = [
            statistics.mean(results[method][q_id]["server_ms"])
            for q_id in REQUESTS_QUESTIONS
            if results[method][q_id]["server_ms"]  # skip if empty (all requests failed)
        ]
        avg = statistics.mean(all_means) if all_means else 0
        row += f" | {avg:>18.2f} ms avg"
    print(row)
    print("=" * 100)


def export_results_csv(results: dict, filename: str = "benchmark_results.csv"):
    """
    Export benchmark results to a CSV file in "long format".

    Long format means one row per (question, method, metric) combination.
    This produces 10 questions × 3 methods × 2 metrics = 60 rows.

    Long format is preferred because it's directly usable by:
      - Spreadsheet pivot tables (Excel, LibreOffice Calc, Google Sheets)
      - Pandas: pd.read_csv("benchmark_results.csv", sep=";")
      - Charting tools and LaTeX table packages

    Columns:
      question   — R1, R2, ..., R10
      method     — Web 1.0, RDFa, Knowledge Graph
      metric     — "server_ms" (API-side only) or "client_ms" (full round-trip)
      mean_ms    — arithmetic mean across all iterations
      median_ms  — median (robust to outliers)
      stdev_ms   — standard deviation (consistency measure)
      min_ms     — fastest iteration
      max_ms     — slowest iteration

    Args:
        results:  The nested dict returned by benchmark().
        filename: Output file path. Defaults to "benchmark_results.csv".
    """
    # newline="" is required by the csv module to prevent double line breaks
    # on Windows. Harmless on Linux but ensures cross-platform correctness.
    with open(filename, "w", newline="", encoding="utf-8") as f:
        # Semicolon delimiter because:
        # 1. French question text may contain commas
        # 2. French-locale spreadsheet apps (LibreOffice) auto-detect ";" correctly
        writer = csv.writer(f, delimiter=";")

        # Write the header row
        writer.writerow([
            "question", "method", "metric",
            "mean_ms", "median_ms", "stdev_ms", "min_ms", "max_ms"
        ])

        # Write one row per (method, question, metric) combination
        for method in results:
            for q_id in results[method]:
                # Export both timing perspectives for each combination
                for metric in ("server_ms", "client_ms"):
                    stats = compute_stats(results[method][q_id][metric])
                    writer.writerow([
                        q_id,           # e.g. "R1"
                        method,         # e.g. "Web 1.0"
                        metric,         # e.g. "server_ms"
                        stats["mean"],
                        stats["median"],
                        stats["stdev"],
                        stats["min"],
                        stats["max"],
                    ])

    print(f"Results exported to {filename}")


# ============================================================================
# Entry point — only runs when the script is executed directly
# (not when imported as a module)
# ============================================================================
if __name__ == "__main__":
    # Number of times each (method, question) pair is called.
    # 30 is the statistical minimum for meaningful comparison (CLT).
    # Increase to 50–100 for more precise results if time allows.
    N = 100

    # Total API calls = N × 10 questions × 3 methods
    total_calls = N * len(REQUESTS_QUESTIONS) * len(API_ENDPOINTS)
    print(f"Starting benchmark: {N} iterations × {len(REQUESTS_QUESTIONS)} questions × {len(API_ENDPOINTS)} methods")
    print(f"Total API calls: {total_calls}\n")

    # --- Run the benchmark ---
    results = benchmark(n_iterations=N)

    # --- Output results ---
    print_comparison_table(results)  # Quick visual summary in the terminal
    export_results_csv(results)      # Detailed data for spreadsheets/analysis