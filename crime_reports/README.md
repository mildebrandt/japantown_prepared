Install the requirements and run:
```
python generate_report.py
```

This script generates a crime report from the [San Jose open data on police calls](https://data.sanjoseca.gov/dataset/police-calls-for-service). The police data indicates location either by numerical address or by cross street. Those can be defined in the `streets.toml` file. There are A LOT of call types. To collapse them into broader categories, users can modify the `call_type_mapping.toml` file.

When the script is first run, it'll download the police data file that's defined in the `settings.toml` file and save it as `policecalls.csv` in the current directory. As long as this file exists, a new version won't be downloaded. To download an updated copy, first delete the `policecalls.csv` file and then run the script.
