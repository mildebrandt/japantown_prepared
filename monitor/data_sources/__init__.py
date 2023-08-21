import logging
import os
import time
import yaml

from typing import Dict, Optional
from pathlib import Path
from inspect import isclass
from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module


LOG = logging.getLogger(__name__)


class DataSource:
    cache_expiry_in_minutes = 10

    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)
        self.cache_filename = f"{self.cache_directory}/{self.__class__.__name__}.yaml"

    def create_cache_dir(self):
        try:
            os.makedirs(os.path.expanduser(self.cache_directory))
        except FileExistsError:
            pass

    def get_cached_results(self) -> Optional[Dict]:
        results = None
        path = Path(os.path.expanduser(self.cache_filename))
        try:
            if time.time() - path.stat().st_mtime < self.cache_expiry_in_minutes * 60:
                with open(path) as f:
                    results = yaml.safe_load(f)
        except (FileExistsError, FileNotFoundError):
            pass

        return results

    def save_cached_results(self, data: Dict) -> None:
        self.create_cache_dir()
        path = Path(os.path.expanduser(self.cache_filename))

        try:
            with open(path, "w") as f:
                yaml.safe_dump(data, f)
        except FileNotFoundError:
            LOG.warning(f"Unable to save cache file: {path}")

    def get_status(self) -> dict:
        """Returns the current status for the requested monitor in the following format:
        {
            "message": ""  # A formatted string to show to the user.
            "alerts": []          # An array of dictionaries with attributes of interest
                                  #   from several montioring stations if applicable.
        }
        """
        raise NotImplementedError


def curl_format(req):
    command = "curl -X {method} -H {headers} -d '{data}' '{uri}'"
    method = req.method
    uri = req.url
    data = req.body
    headers = ['"{0}: {1}"'.format(k, v) for k, v in req.headers.items()]
    headers = " -H ".join(headers)
    return command.format(method=method, headers=headers, data=data, uri=uri)


# Adapted from https://julienharbulot.com/python-dynamical-import.html
data_source_classes = {}

# iterate through the modules in the current package
package_dir = Path(__file__).resolve().parent
for _, module_name, _ in iter_modules([package_dir]):
    # import the module and iterate through its attributes
    module = import_module(f"{__name__}.{module_name}")
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)

        if (
            isclass(attribute)
            and issubclass(attribute, DataSource)
            and attribute is not DataSource
        ):
            # Add the subclasses of DataSource to the list of data sources
            data_source_classes[attribute_name] = attribute
