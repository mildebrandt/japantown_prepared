import os
import yaml

config_file = os.environ.get("MONITOR_CONFIG_FILE", "config.yaml")

# Defaults for the config go here:
config = {
    "global": {
        "cache_directory": "~/.cache/japantown_prepared_monitor",
        "cache_expiry_in_minutes": 10,
    },
    "notify": {
        "smtp_host": "email-smtp.us-west-2.amazonaws.com",
        "smtp_port": 465,
        "ssl": True,
        "sender_email": "japantown-prepared@woodenrhino.com",
        "sender_name": "Japantown Prepared",
    },
}

with open(config_file, "r") as f:
    config.update(yaml.safe_load(f))


# Environment variables in the form of MONITOR__{section}__{attribute}
# will replace existing, or add to, the config object.
for module_name, variables in config.items():
    for k, v in variables.items():
        env_name = f"MONITOR__{module_name}__{k}"
        config[module_name][k] = os.environ.get(env_name, v)
        e = os.environ.get(env_name)
