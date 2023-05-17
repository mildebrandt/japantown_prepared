from config import config
from notify import nofity
from data_sources import data_source_classes


def get_statuses() -> dict:
    statuses = {}
    for name, _class in data_source_classes.items():
        inst = _class(**config.get(name, {}))
        statuses[name] = inst.get_status()["message"]
    return statuses


if __name__ == "__main__":
    statuses = get_statuses()

    for source, status in statuses.items():
        print(status)

    if "notify" in config:
        nofity(status)
