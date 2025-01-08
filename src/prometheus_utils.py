import requests
import logging

logger = logging.getLogger(__name__)


def make_request_with_retries(url, params=None, headers=None, verify=True, retries=3, timeout=30):
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, headers=headers, verify=verify, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt == retries - 1:
                raise


def fetch_metric_names_by_prefix(prometheus_url, prefix, headers, ca_cert_path=None):
    try:
        response = make_request_with_retries(
            f"{prometheus_url}/api/v1/label/__name__/values",
            headers=headers,
            verify=ca_cert_path or False
        )
        all_metrics = response.json().get('data', [])
        return [metric for metric in all_metrics if metric.startswith(prefix)]
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching metric names with prefix '{prefix}': {e}")
        return []


def fetch_metric_metadata(prometheus_url, metric_name, headers, ca_cert_path=None):
    try:
        # Define suffix-specific descriptions
        suffix_descriptions = {
            "histogram": {
                "_sum": "Total sum of values in the histogram.",
                "_bucket": "Count of observations in each bucket.",
                "_count": "Total number of observations.",
            },
            "summary": {
                "_sum": "Total sum of observed values.",
                "_count": "Total number of observations.",
            },
        }

        # Fetch metadata
        metadata_response = make_request_with_retries(
            f"{prometheus_url}/api/v1/metadata",
            headers=headers,
            verify=ca_cert_path or False
        )
        all_metadata = metadata_response.json().get('data', {})
        metadata = all_metadata.get(metric_name, [])

        # Extract description and type
        metric_description = None
        metric_type = None
        for meta in metadata:
            if 'help' in meta:
                metric_description = meta['help']
            if 'type' in meta:
                metric_type = meta['type']
                break  # Use the first matching metadata entry

        # Adjust description based on suffix if type matches
        if metric_type in suffix_descriptions:
            for suffix, description in suffix_descriptions[metric_type].items():
                if metric_name.endswith(suffix):
                    metric_description = f"{metric_description} {description}" if metric_description else description
                    break

        # Determine the origin of the metric
        metric_origin = "recording_rule" if metric_name in all_metadata and any('rules' in meta for meta in metadata) else "metric"

        # Fetch labels
        labels_response = make_request_with_retries(
            f"{prometheus_url}/api/v1/query",
            params={'query': metric_name},
            headers=headers,
            verify=ca_cert_path or False
        )
        results = labels_response.json().get('data', {}).get('result', [])

        # Extract labels
        labels = set()
        for result in results:
            labels.update(result.get('metric', {}).keys())

        # Return structured data
        return {
            'metric_name': metric_name,
            'metric_description': metric_description,
            'type': metric_type,
            'metric_origin': metric_origin,
            'labels': [{'label_name': label, 'label_description': None} for label in labels]
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching metadata for metric '{metric_name}': {e}")
        return {
            'metric_name': metric_name,
            'metric_description': None,
            'type': None,
            'metric_origin': None,
            'labels': []
        }
