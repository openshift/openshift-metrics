import yaml
import logging
import string
logger = logging.getLogger(__name__)

def load_label_descriptions(file_path):
    try:
        with open(file_path, "r") as yamlfile:
            labels = yaml.safe_load(yamlfile)
            return {item['label_name']: item['label_description'] for item in labels}
    except IOError as e:
        logger.error(f"Error reading label descriptions file: {e}")
        return {}

def save_metrics_to_yaml(metrics, file_path):
    try:
        with open(file_path, "w") as yamlfile:
            yaml.dump({'metrics': metrics}, yamlfile, default_flow_style=False)
        logger.info(f"Metrics metadata has been saved to {file_path}")
    except IOError as e:
        logger.error(f"Error saving metrics to YAML file: {e}")

def merge_metrics(old_metrics, new_metrics, label_descriptions):
    """
    Merge old and new metrics, updating existing ones and adding new ones.
    Preserve existing labels, and only add new labels without removing old ones.
    Always update label descriptions based on the input label_descriptions file.
    """
    merged_metrics = {metric['metric_name']: metric for metric in old_metrics}

    for new_metric in new_metrics:
        metric_name = new_metric['metric_name']
        if metric_name in merged_metrics:
            # Update existing metric
            merged_metric = merged_metrics[metric_name]

            # Update metric description only if the new one is not "None"
            if new_metric['metric_description'] != None:
                merged_metric['metric_description'] = new_metric['metric_description']

            # Update type only if the new one is not None
            if new_metric['type'] != None:
                merged_metric['type'] = new_metric['type']

            # Merge labels - preserve existing labels and add new ones
            existing_labels = {label['label_name']: label for label in merged_metric['labels']}
            for new_label in new_metric['labels']:
                label_name = new_label['label_name']
                if label_name in existing_labels:
                    # Always update label description if it exists in label_descriptions
                    if label_name in label_descriptions:
                        existing_labels[label_name]['label_description'] = label_descriptions[label_name]
                        print(
                            f"Updated label description from file: Metric '{metric_name}', Label '{label_name}', New"
                            f"Description: '{label_descriptions[label_name]}'")
                else:
                    # Add new label and apply description from label_descriptions
                    if label_name in label_descriptions:
                        new_label['label_description'] = label_descriptions[label_name]
                    existing_labels[label_name] = new_label
                    print(
                        f"New label added: Metric '{metric_name}', Label '{label_name}', Description: '{new_label['label_description']}'")
            merged_metric['labels'] = list(existing_labels.values())
        else:
            # Add new metric
            merged_metrics[metric_name] = new_metric

    return list(merged_metrics.values())