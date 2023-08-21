from config import config
from notify import nofity
from data_sources import data_source_classes


def get_statuses() -> dict:
    statuses = {}
    for name, _class in data_source_classes.items():
        inst = _class(**config.get(name, {}), **config.get("global", {}))
        try:
            statuses[name] = inst.get_status()
        except:
            print(f"Error getting data from the {_class.__name__} data source.\n")
            raise
    return statuses


if __name__ == "__main__":
    statuses = get_statuses()

    status_msg = ""
    hashes = {}
    for source, status in statuses.items():
        status_msg += status["message"] + "\n"
        hashes[source] = status["hash"]

    # TODO: Compare hashes with stored file, send email if different, save new hashes
    # If no file, send if alert status, don't send if no alerts

    print(status_msg)
    if config.get("notify", {}).get("enable"):
        nofity("Monitor Alert", status_msg)
