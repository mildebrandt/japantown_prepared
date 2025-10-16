import os
import re
from datetime import datetime

import pandas as pd
import requests
import tomllib as toml
from dateutil.relativedelta import relativedelta

TWO_MONTHS_AGO = (datetime.now() - relativedelta(months=2)).strftime(
    "%Y-%m-%d %H:%M:%S"
)
ONE_MONTH_AGO = (datetime.now() - relativedelta(months=1)).strftime("%Y-%m-%d %H:%M:%S")
NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def download_file(url, filename):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(filename, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    print(f"Downloaded '{filename}' successfully.")


def extract_numeric_address(address_str):
    if isinstance(address_str, str):
        match = re.search(r"(\d+)", address_str)
        if match:
            return int(match.group(1))
    return None


def get_dataframe_from_csv(csv_filepath):
    df = pd.read_csv(csv_filepath)
    # Ensure the address column is treated as string and handle potential NaNs
    df["ADDRESS"] = df["ADDRESS"].astype(str).str.lower().str.strip()
    # Remove rows where the address is 'nan'
    df = df[df["ADDRESS"] != "nan"]

    return df


def matches_numeric_range(address_str, ranges):
    try:
        numeric_part = extract_numeric_address(address_str)
        if numeric_part is not None:
            address_lower = address_str.lower()
            for start_range, end_range, street in ranges:
                street_lower = street.lower().strip()
                if (
                    start_range <= numeric_part <= end_range
                    and street_lower in address_lower
                ):
                    return True
        return False
    except (ValueError, AttributeError, IndexError):
        return False


def matches_cross_street(address_str, cross_streets):
    if isinstance(address_str, str) and "&" in address_str:
        ns_lower_no_prefix = [
            re.sub(r"^[ns]\s+", "", s.lower().strip())
            for s in cross_streets["north_south"]
        ]
        ew_lower_no_prefix = [
            re.sub(r"^[ew]\s+", "", s.lower().strip())
            for s in cross_streets["east_west"]
        ]
        parts = [part.lower().strip() for part in address_str.split("&")]
        if len(parts) == 2:
            street1_no_prefix = re.sub(r"^[ns]\s+", "", parts[0]).strip()
            street2_no_prefix = re.sub(r"^[ew]\s+", "", parts[1]).strip()
            match_ns_ew = (
                street1_no_prefix in ns_lower_no_prefix
                and street2_no_prefix in ew_lower_no_prefix
            )
            match_ew_ns = (
                street1_no_prefix in ew_lower_no_prefix
                and street2_no_prefix in ns_lower_no_prefix
            )
            return match_ns_ew or match_ew_ns
    return False


def add_datetime_column(df):
    date_format = "%m/%d/%Y %I:%M:%S %p"
    df["OFFENSE_DATETIME"] = (
        pd.to_datetime(df["OFFENSE_DATE"], format=date_format).dt.date.astype(str)
        + " "
        + df["OFFENSE_TIME"]
    )

    df["OFFENSE_DATETIME"] = pd.to_datetime(
        df["OFFENSE_DATETIME"], format="%Y-%m-%d %H:%M:%S"
    )

    return df


def filter_by_datetime(df, start_datetime_str=None, end_datetime_str=None):
    if start_datetime_str is None:
        start_datetime_str = "1900-01-01 01:00:00"

    if end_datetime_str is None:
        end_datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    start_datetime = pd.to_datetime(start_datetime_str)
    end_datetime = pd.to_datetime(end_datetime_str)
    return df[
        (df["OFFENSE_DATETIME"] >= start_datetime)
        & (df["OFFENSE_DATETIME"] <= end_datetime)
    ]


def filter_by_address(
    df,
    numeric_address_ranges=None,
    cross_streets=None,
):
    if numeric_address_ranges is not None:
        # Filter by numeric address ranges (only if '&' is NOT present)
        numeric_filtered_df = df[
            df["ADDRESS"].apply(
                lambda x: "&" not in x
                and matches_numeric_range(x, numeric_address_ranges)
            )
        ]
    else:
        numeric_filtered_df = df[[]]

    if cross_streets is not None:
        # Filter by cross streets (only if '&' IS present)
        cross_street_filtered_df = df[
            df["ADDRESS"].apply(
                lambda x: "&" in x and matches_cross_street(x, cross_streets)
            )
        ]
    else:
        cross_street_filtered_df = df[[]]

    combined_address_df = pd.concat(
        [numeric_filtered_df, cross_street_filtered_df]
    ).drop_duplicates()

    if combined_address_df.empty:
        return pd.DataFrame()

    return combined_address_df


def get_table(
    df, columns=None, tablefmt="fancy_outline", with_total=True, sort_by=None
):
    _df = df.copy()
    if columns is not None:
        _df.columns = columns

    if sort_by is not None:
        _df = _df.sort_values(by=sort_by, ascending=False)

    if with_total:
        total_col1 = _df[_df.columns[1]].sum()
        total_col2 = _df[_df.columns[2]].sum()
        _df = pd.concat(
            [
                _df,
                pd.DataFrame(
                    {
                        _df.columns[0]: ["Total"],
                        _df.columns[1]: [total_col1],
                        _df.columns[2]: [total_col2],
                    }
                ),
            ],
            ignore_index=True,
        )

    markdown_table = _df.to_markdown(index=False, tablefmt=tablefmt)
    return markdown_table


def print_data(df, call_categories=None):
    # --- Date and time filtering
    this_months_data = df[
        (df["OFFENSE_DATETIME"] >= ONE_MONTH_AGO) & (df["OFFENSE_DATETIME"] <= NOW)
    ]

    last_months_data = df[
        (df["OFFENSE_DATETIME"] >= TWO_MONTHS_AGO)
        & (df["OFFENSE_DATETIME"] <= ONE_MONTH_AGO)
    ]

    if not this_months_data.empty and not last_months_data.empty:
        if call_categories is not None:
            column_name = "CALL_CATEGORY"
        else:
            column_name = "CALL_TYPE"

        this_months_category_counts = (
            this_months_data[column_name].value_counts().reset_index()
        )
        last_months_category_counts = (
            last_months_data[column_name].value_counts().reset_index()
        )
        combined_data = pd.merge(
            this_months_category_counts,
            last_months_category_counts,
            on=column_name,
            how="outer",
        ).fillna(0)

        table = get_table(
            combined_data,
            columns=[
                "Category",
                "This Month",
                "Last Month",
            ],
            sort_by="This Month",
        )

        print(table)
    else:
        print("\nNo data matches the specified criteria.")


if __name__ == "__main__":
    csv_file = "policecalls.csv"

    try:
        with open("settings.toml", "rb") as f:
            settings = toml.load(f)
    except FileNotFoundError:
        if not os.path.exists(csv_file):
            raise Exception("Missing settings file.")
        settings = {}

    try:
        with open("call_type_mapping.toml", "rb") as f:
            call_categories = toml.load(f)
    except FileNotFoundError:
        call_categories = None

    try:
        with open("streets.toml", "rb") as f:
            streets = toml.load(f)
    except FileNotFoundError:
        streets = {}

    if settings and not os.path.exists(csv_file):
        download_file(settings["data_url"], csv_file)

    df = get_dataframe_from_csv(csv_file)
    df = add_datetime_column(df)
    df = filter_by_datetime(df, TWO_MONTHS_AGO, NOW)

    df = filter_by_address(
        df,
        streets.get("address_ranges"),
        streets.get("cross_streets"),
    )

    if call_categories is not None:
        df["CALL_CATEGORY"] = (
            df["CALL_TYPE"].map(call_categories).fillna("Uncategorized")
        )

    print_data(df, call_categories=call_categories)
