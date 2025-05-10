from datetime import datetime

from . import cache, logger
from .config import config
from .data_sources import data_source_classes
from .notify import nofity


def get_statuses() -> dict:
    statuses = {}
    for name, _class in data_source_classes.items():
        if name not in config:
            continue

        inst = _class(**config.get(name, {}), **config.get("global", {}))

        if not inst.enable:
            continue

        try:
            statuses[name] = inst.get_status()
        except Exception as e:
            # TODO: send an e-mail to admin when we get errors from APIs.
            logger.error(
                f"Error getting data from the {_class.__name__} data source:\n\t{e.args[0]}\n"
            )
            # Set status to None to indicate that we expected data but got none.
            statuses[name] = None
    return statuses


# Returns True if a new status appears or if a status has changed.
# After comparison, it stored the updated hashes in the cache.
def process_hashes(hashes: dict) -> bool:
    hashes_changed = False
    previous_hashes = cache.get("hashes")
    logger.debug(
        f"Comparing hashes:\n  Previous hashes:\n{previous_hashes}\n  Current hashes:\n{hashes}"
    )
    if previous_hashes:
        for key, _hash in hashes.items():
            if key not in previous_hashes:
                hashes_changed = True
            elif _hash is None:
                # If the current hash is None, replace it with the previous value.
                # This usually happens if we're unable to contact the API.
                hashes[key] = previous_hashes[key]
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
        try:
            status_msg += status["message"] + "\n"
            hashes[source] = status["hash"]
        except TypeError:
            # If status is None, we'll fall here.
            hashes[source] = None

    hashes_changed = process_hashes(hashes)

    if hashes_changed:
        if config.get("notify", {}).get("enable"):
            logger.info("Sending notification.")
            nofity(
                f"Monitor Alert - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                status_msg,
            )


if __name__ == "__main__":
    main()
