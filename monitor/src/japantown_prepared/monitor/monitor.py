from . import cache
from .config import config
from .notify import nofity
from .data_sources import data_source_classes


def get_statuses() -> dict:
    statuses = {}
    for name, _class in data_source_classes.items():
        inst = _class(**config.get(name, {}), **config.get("global", {}))
        try:
            statuses[name] = inst.get_status()
        except:
            print(f"Error getting data from the {_class.__name__} data source.\n")
    return statuses


# Returns True if a new status appears or if a status has changed.
# After comparison, it stored the updated hashes in the cache.
def process_hashes(hashes: dict) -> bool:
    hashes_changed = False
    previous_hashes = cache.get("hashes")
    if previous_hashes:
        for key, _hash in hashes.items():
            if key not in previous_hashes:
                hashes_changed = True
            elif previous_hashes[key] != _hash:
                hashes_changed = True
    else:
        hashes_changed = True

    cache.set("hashes", hashes, expire_in_seconds=None)
    return hashes_changed


def main():
    statuses = get_statuses()

    status_msg = ""
    hashes = {}
    for source, status in statuses.items():
        status_msg += status["message"] + "\n"
        hashes[source] = status["hash"]

    print(status_msg)

    hashes_changed = process_hashes(hashes)

    if hashes_changed:
        if config.get("notify", {}).get("enable"):
            nofity("Monitor Alert", status_msg)


if __name__ == "__main__":
    main()
