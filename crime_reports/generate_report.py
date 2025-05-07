# This was written by Gemini AI, may need some cleanup
import os
import pandas as pd
import requests
import re
import tomllib as toml

from datetime import datetime
from dateutil.relativedelta import relativedelta


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


def matches_numeric_range(address_str, ranges):
    try:
        numeric_part = extract_numeric_address(address_str)
        if numeric_part is not None:
            address_lower = address_str.lower()
            for start_range, end_range, street in ranges:
                street_lower = street.lower().strip()
                street_lower_no_prefix = re.sub(
                    r"^[ns]\s+", "", re.sub(r"^[ew]\s+", "", street_lower)
                ).strip()
                address_lower_no_prefix = re.sub(
                    r"^[ns]\s+", "", re.sub(r"^[ew]\s+", "", address_lower)
                ).strip()
                street_lower_no_prefix = street_lower.strip()
                address_lower_no_prefix = address_lower.strip()

                if (
                    start_range <= numeric_part <= end_range
                    and street_lower_no_prefix in address_lower_no_prefix
                ):
                    return True
        return False
    except (ValueError, AttributeError, IndexError):
        return False


def is_cross_street_match(address_str, cross_streets):
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


def filter_data_by_address_and_offense_datetime(
    csv_filepath,
    call_types=None,
    numeric_address_ranges=None,
    cross_streets=None,
    start_datetime_str=None,
    end_datetime_str=None,
    call_type_filter_list=None,
):
    if start_datetime_str is None:
        start_datetime_str = "1900-01-01 01:00:00"

    if end_datetime_str is None:
        end_datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    df = pd.read_csv(csv_filepath)
    # Ensure the address column is treated as string and handle potential NaNs
    df["ADDRESS"] = df["ADDRESS"].astype(str).str.lower().str.strip()
    # Remove rows where the address is 'nan'
    df = df[df["ADDRESS"] != "nan"]

    if call_types is not None:
        df["CALL_CATEGORY"] = df["CALL_TYPE"].map(call_types).fillna("Uncategorized")

    if numeric_address_ranges is not None:
        # Filter by numeric address ranges (only if '&' is NOT present)
        numeric_filtered_df = df[
            df["ADDRESS"].apply(
                lambda x: "&" not in x
                and matches_numeric_range(x, numeric_address_ranges)
            )
        ].copy()
    else:
        numeric_filtered_df = None

    if cross_streets is not None:
        # Filter by cross streets (only if '&' IS present)
        cross_street_filtered_df = df[
            df["ADDRESS"].apply(
                lambda x: "&" in x and is_cross_street_match(x, cross_streets)
            )
        ].copy()
    else:
        cross_street_filtered_df = None

    if numeric_filtered_df is not None and cross_street_filtered_df is not None:
        # Combine the two address-filtered DataFrames
        combined_address_df = pd.concat(
            [numeric_filtered_df, cross_street_filtered_df]
        ).drop_duplicates()
    elif numeric_filtered_df is not None:
        combined_address_df = numeric_filtered_df
    elif cross_street_filtered_df is not None:
        combined_address_df = cross_street_filtered_df
    else:
        combined_address_df = df

    if combined_address_df.empty:
        return pd.DataFrame()

    # Combine offense date and time into new datetime column
    date_format = "%m/%d/%Y %I:%M:%S %p"
    combined_address_df["OFFENSE_DATETIME"] = (
        pd.to_datetime(
            combined_address_df["OFFENSE_DATE"], format=date_format
        ).dt.date.astype(str)
        + " "
        + combined_address_df["OFFENSE_TIME"]
    )
    combined_address_df["OFFENSE_DATETIME"] = pd.to_datetime(
        combined_address_df["OFFENSE_DATETIME"], format="%Y-%m-%d %H:%M:%S"
    )

    start_datetime = pd.to_datetime(start_datetime_str)
    end_datetime = pd.to_datetime(end_datetime_str)
    datetime_filtered_df = combined_address_df[
        (combined_address_df["OFFENSE_DATETIME"] >= start_datetime)
        & (combined_address_df["OFFENSE_DATETIME"] <= end_datetime)
    ].copy()

    # --- Call Type Filtering ---
    if call_type_filter_list and not datetime_filtered_df.empty:
        final_filtered_df = datetime_filtered_df[
            datetime_filtered_df["CALL_TYPE"].isin(call_type_filter_list)
        ].copy()
        return final_filtered_df
    elif not datetime_filtered_df.empty:
        return datetime_filtered_df
    else:
        return pd.DataFrame()


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

    end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_date = (datetime.now() - relativedelta(months=1)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    filtered_data = filter_data_by_address_and_offense_datetime(
        csv_file,
        call_categories,
        streets.get("address_ranges"),
        streets.get("cross_streets"),
        start_date,
        end_date,
    )

    if not filtered_data.empty:
        if call_categories is not None:
            category_counts = (
                filtered_data["CALL_CATEGORY"].value_counts().reset_index()
            )
            category_counts.columns = ["Category", "Incidents"]

            markdown_table = category_counts.to_markdown(
                index=False, tablefmt="fancy_outline"
            )
            print(markdown_table)

        type_counts = filtered_data["CALL_TYPE"].value_counts().reset_index()
        type_counts.columns = ["Call Type", "Incidents"]

        markdown_table = type_counts.to_markdown(index=False, tablefmt="fancy_outline")
        print(markdown_table)
    else:
        print("\nNo data matches the specified criteria.")
