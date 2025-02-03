import argparse
from collections import defaultdict
import os
import yaml
import logging
import warnings
from urllib3.exceptions import InsecureRequestWarning
from prometheus_utils import *
from helpers import *


from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Suppress SSL warnings
warnings.simplefilter('ignore', InsecureRequestWarning)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Fetch and update OpenShift Prometheus metrics documentation.")
    parser.add_argument("--token", default=os.getenv("PROMETHEUS_TOKEN"), required=not os.getenv("PROMETHEUS_TOKEN"),
                        help="Authentication token for accessing the Prometheus API.")
    parser.add_argument("--prometheus-url",
                        default="https://prometheus-k8s-openshift-monitoring.apps.cnv2.engineering.redhat.com",
                        help="Prometheus server URL.")
    parser.add_argument(
        "--ca-cert-path",
        default=None,
        help="Path to the CA certificate file for HTTPS verification. Default is None (no verification).")
    return parser.parse_args()


def process_metrics_for_letter(letter, prometheus_url, headers, label_descriptions, ca_cert_path, output_dir):
    """
    Fetch metrics for a specific alphabetical letter and merge them with existing data.
    """
    logger.info(f"Processing metrics starting with '{letter}'...")
    metric_names = fetch_metric_names_by_prefix(prometheus_url, letter, headers, ca_cert_path)

    if not metric_names:
        logger.warning(f"No metrics found for prefix '{letter}' or error fetching metrics.")
        return

    # Group metrics by their prefix (first part before the underscore)
    grouped_metrics = defaultdict(list)
    for metric_name in metric_names:
        prefix = metric_name.split('_')[0]
        grouped_metrics[prefix].append(metric_name)

    # Process each group and merge with existing data
    for prefix, metrics in grouped_metrics.items():
        metrics_metadata = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_metric = {
                executor.submit(fetch_metric_metadata, prometheus_url, metric, headers, ca_cert_path): metric
                for metric in metrics
            }
            for future in as_completed(future_to_metric):
                try:
                    metadata = future.result()
                    metrics_metadata.append(metadata)
                except Exception as e:
                    logger.error(f"Error processing metric: {e}")

        # Load existing metrics from the file, if it exists
        file_path = os.path.join(output_dir, f"{prefix}_metrics.yaml")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as yamlfile:
                    existing_data = yaml.safe_load(yamlfile)
                    existing_metrics = existing_data.get('metrics', [])
            except IOError as e:
                logger.error(f"Error reading file {file_path}: {e}")
                existing_metrics = []
        else:
            existing_metrics = []

        # Merge new and existing metrics
        merged_metrics = merge_metrics(existing_metrics, metrics_metadata, label_descriptions)

        # Save the merged metrics back to the file
        save_metrics_to_yaml(merged_metrics, file_path)


def main():
    args = parse_arguments()
    token = args.token
    prometheus_url = args.prometheus_url
    headers = {"Authorization": f"Bearer {token}"}
    ca_cert_path = args.ca_cert_path
    output_dir = "../docs/prometheus_metrics"
    os.makedirs(output_dir, exist_ok=True)

    label_descriptions = load_label_descriptions("../data/label_descriptions.yaml")

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(process_metrics_for_letter, letter, prometheus_url, headers, label_descriptions,
                    ca_cert_path, output_dir) for letter in string.ascii_lowercase]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"Error processing letter: {e}")


if __name__ == "__main__":
    main()
