import os
import yaml
from dotenv import load_dotenv

load_dotenv()


config_file = os.environ.get("MONITOR_CONFIG_FILE", "config.yaml")

# Defaults for the config go here:
config = {
    "global": {
        "cache_directory": "~/.cache/japantown_prepared_monitor",
        "cache_expiry_in_seconds": 600,
    },
    "notify": {
        "enable": False,
        "smtp_host": "email-smtp.us-west-2.amazonaws.com",
        "smtp_port": 465,
        "ssl": True,
        "sender_email": "japantown-prepared@woodenrhino.com",
        "sender_name": "Japantown Prepared",
    },
}

with open(config_file, "r") as f:
    config_from_file = yaml.safe_load(f)
    for k, v in config_from_file.items():
        if k in config:
            config[k].update(v)
        else:
            config[k] = v

# Environment variables in the form of MONITOR__{section}__{attribute}
# will replace existing, or add to, the config object.
for module_name, variables in config.items():
    for k, v in variables.items():
        env_name = f"MONITOR__{module_name}__{k}"
        config[module_name][k] = os.environ.get(env_name, v)
        e = os.environ.get(env_name)
