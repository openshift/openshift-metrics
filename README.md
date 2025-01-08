# OpenShift Metrics Documentation

This repository provides a centralized documentation source for OpenShift and its operators Prometheus metrics.
It includes metadata for metrics such as descriptions, labels, and types.

The repository also provides a script to automatically fetch and update the list of Prometheus metrics and their associated labels from OpenShift clusters.

## Features

- **Centralized Documentation**: Stores Prometheus metrics and their metadata (descriptions, labels, types) in organized YAML files.
- **Automated Updates**: A Python script that can be run against OpenShift clusters to fetch new metrics and update existing ones.
- **Custom Label Descriptions**: Allows updating label descriptions using an input YAML file for improved clarity and consistency.

# Getting Started

## Prerequisites

- Python 3.7 or later.
- Access to an OpenShift cluster with Prometheus monitoring enabled.
- A valid token for accessing the Prometheus endpoint.

## Installation

### Clone this repository:

```bash
git clone https://github.com/your-username/openshift-metrics.git
```
```bash
cd openshift-metrics
```

### Install the required dependencies:

```bash
pip install requests>=2.25.0 pyyaml>=5.4 urllib3>=1.26
```
## Running the Script

### Prepare the Input File:
Place the label_descriptions.yaml file in the data/ directory. It should follow this format:

```yaml
- label_name: endpoint
  label_description: The specific endpoint of the service or application being monitored.
- label_name: namespace
  label_description: The Kubernetes namespace in which the pod or service resides.
```

### Run the Script:

Execute the Python script to fetch and update metrics documentation:

```bash
python src/fetch_metrics.py --token YOUR_PROMETHEUS_TOKEN
```

## Output:

The updated metrics documentation will be saved in the docs/prometheus_metrics/ directory. Each YAML file corresponds to a group of metrics organized by their prefix, such as:

```bash
docs/prometheus_metrics/
├── controller_metrics.yaml
├── kube_metrics.yaml
└── network_metrics.yaml
```

**Note:** It is possible to manually update the metrics and labels descriptions directly in the file under `docs/prometheus_metrics`.

## Debugging
The script provides debug messages for:

- Labels that are newly added.
- Labels whose descriptions are updated based on the label_descriptions.yaml input file.

## Contributing
We welcome contributions to improve the documentation or the script. Follow these steps to contribute:

1. Fork the repository.
2. Create a new branch:

```bash
git checkout -b feature-name
```

3. Commit your changes and push the branch:

```bash
git push origin feature-name
```

4. Open a pull request.

## License
This project is licensed under the Apache License.

## Contact
For issues or questions, feel free to open an issue.
