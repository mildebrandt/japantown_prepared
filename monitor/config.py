import os
import yaml

config_file = os.environ.get("MONITOR_CONFIG_FILE", "config.yaml")

with open(config_file, "r") as f:
    config = yaml.safe_load(f)
