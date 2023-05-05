import yaml
from data_sources import data_source_classes

config_file = "config.yaml"


def get_config(config_file=config_file) -> dict:
    with open(config_file, "r") as f:
        return yaml.safe_load(f)


def get_statuses() -> dict:
    config = get_config()
    statuses = {}
    for name, _class in data_source_classes.items():
        inst = _class(**config.get(name, {}))
        statuses[name] = inst.get_status()["message"]
    return statuses


if __name__ == "__main__":
    for source, status in get_statuses().items():
        print(status)
        print()
