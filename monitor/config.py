import os
import yaml

config_file = os.environ.get("MONITOR_CONFIG_FILE", "config.yaml")

with open(config_file, "r") as f:
    config = yaml.safe_load(f)


# Environment variables in the form of MONITOR__{data_class_name}__{variable_name}
# will replace existing, or add to, the config object.
for module_name, variables in config.items():
    if isinstance(variables, dict):
        for k, v in variables.items():
            env_name = f"MONITOR__{module_name}__{k}"
            config[module_name][k] = os.environ.get(env_name, v)
            e = os.environ.get(env_name)
    else:
        config[module_name] = os.environ.get(f"MONITOR__{module_name}", variables)
