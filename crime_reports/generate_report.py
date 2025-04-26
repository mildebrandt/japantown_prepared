import os
import pandas as pd
import requests
import re

call_type_mapping = {
    "ABANDONED VEHICLE": "Service Call",
    "ALARM": "Service Call",
    "ALARM, AUDIBLE": "Service Call",
    "ALARM, SILENT": "Service Call",
    "ALARM, SVRN": "Service Call",
    "ALTERED VIN NUMBER": "Fraud",
    "ANIMAL COMPLAINT": "Other",
    "ARMED ROBBERY": "Robbery",
    "ARMED ROBBERY (COMBINED EVENT)": "Robbery",
    "ARSON (447A)": "Vandalism",
    "ASSAULT": "Assault",
    "ASSAULT AND BATTERY": "Assault",
    "ASSAULT ON AN OFFICER": "Assault",
    "ASSAULT WITH DEADLY WEAPON": "Assault",
    "ASSAULT WITH DEADLY WEAPON (COMBINED EVENT)": "Assault",
    "ASSAULT WITH DEADLY WEAPON, GANG": "Assault",
    "BAD CHECKS": "Fraud",
    "BAR CHECK": "Service Call",
    "BATTERY": "Assault",
    "BATTERY (COMBINED EVENT)": "Assault",
    "BATTERY, GANG RELATED": "Assault",
    "BATTERY ON AN OFFICER": "Assault",
    "BATTERY ON A PEACE OFFICER": "Assault",
    "BATTERY, SERIOUS INJURY": "Assault",
    "BOMB THREAT": "Other",
    "BRANDISHING A WEAPON": "Weapons",
    "BRANDISHING A WEAPON, GANG": "Weapons",
    "BREACH OF AOA": "Service Call",
    "BURGLARY (460)": "Burglary",
    "BURGLARY  REPORT  (460)": "Burglary",
    "CALL_TYPE": "Other",
    "CARJACKING (COMBINED EVENT)": "Vehicle Break-in/Theft",
    "CARRYING A CONCEALED WEAPON": "Weapons",
    "CHILD ABUSE": "Assault",
    "CHILD BEATING": "Assault",
    "CIVIL MATTER": "Other",
    "COMMUNIT POLICING BIKE": "Non-criminal",
    "COMMUNITY POLICING -CITZ ASSIST": "Non-criminal",
    "COMMUNITY POLICING MEETING": "Non-criminal",
    "COMMUNITY POLICING OFFICE": "Non-criminal",
    "COMMUNITY POLICING SCHOOL": "Non-criminal",
    "CONTROLLED SUBSTANCE AT RESIDENCE": "Drugs/Alcohol",
    "CORONERS CASE": "Other",
    "CRIMINAL THREATS": "Assault",
    "CRUELTY TO ANIMALS": "Other",
    "DEAD ANIMAL": "Service Call",
    "DEFRAUDING AN INKEEPER": "Fraud",
    "DISTURBANCE": "Disturbing Peace",
    "DISTURBANCE (COMBINED EVENT)": "Disturbing Peace",
    "DISTURBANCE, FAMILY": "Disturbing Peace",
    "DISTURBANCE, FAMILY (COMBINED EVENT)": "Disturbing Peace",
    "DISTURBANCE, FIGHT": "Disturbing Peace",
    "DISTURBANCE, FIGHT (COMBINED EVENT)": "Disturbing Peace",
    "DISTURBANCE, FIRECRACKERS": "Disturbing Peace",
    "DISTURBANCE, GANG": "Disturbing Peace",
    "DISTURBANCE, JUVENILE": "Disturbing Peace",
    "DISTURBANCE, MOTORCYCLE": "Disturbing Peace",
    "DISTURBANCE, MUSIC": "Disturbing Peace",
    "DISTURBANCE, NEIGHBOR": "Disturbing Peace",
    "DISTURBANCE, UNKNOWN": "Disturbing Peace",
    "DISTURBANCE, UNKNOWN (COMBINED EVENT)": "Disturbing Peace",
    "DISTURBANCE, WEAPON": "Disturbing Peace",
    "DISTURBANCE, WEAPON (COMBINED EVENT)": "Disturbing Peace",
    "DOMESTIC VIOLENCE  (COMBINED EVENT)": "Assault",
    "DRIVING W/SUSPENDED LICENSE": "Traffic",
    "DRUNK IN PUBLIC": "Drugs/Alcohol",
    "ELDER/DEPENDENT ADULT ABUSE": "Assault",
    "EMBEZZLEMENT": "Larceny",
    "EXPIRED REGISTRATION": "Traffic",
    "EXPLOSION": "Other",
    "EXTORTION": "Robbery",
    "FALSE IMPRISONMENT": "Other",
    "FELONY DUI": "DUI",
    "FELONY HIT AND RUN": "Traffic",
    "FELONY WANT": "Other",
    "FEMALE CALLING FOR HELP": "Other",
    "FIREARMS DISCHARGED": "Weapons",
    "FIRE DEPARTMENT REQUEST FOR PD": "Other",
    "FIRE (SPECIFY TYPE)": "Other",
    "FORGERY": "Fraud",
    "FOUND, MISSING PERSON": "Missing Person",
    "FOUND PROPERTY": "Service Call",
    "GARBAGE COMPLAINT": "Service Call",
    "GRAND THEFT": "Larceny",
    "HANDICAPPED PARKING VIOLATION": "Service Call",
    "HATE CRIMES": "Other",
    "HI-TECH CRIMES": "Other",
    "ILLEGAL WEAPONS": "Weapons",
    "ILLEGAL WEAPONS, GANG RELATED": "Weapons",
    "INDECENT EXPOSURE": "Sex Crime",
    "INJURED ANIMAL": "Other",
    "INJURED PERSON": "Other",
    "INTOXICATED PERSON": "Drugs/Alcohol",
    "KIDNAPPING": "Other",
    "MALICIOUS MISCHIEF": "Vandalism",
    "MALICIOUS MISCHIEF, GANG RELATED": "Vandalism",
    "MEET THE CITIZEN": "Non-criminal",
    "MENTALLY DISTURBED FEMALE": "Disturbing Peace",
    "MENTALLY DISTURBED PERSON": "Disturbing Peace",
    "MISDEMEANOR DUI": "DUI",
    "MISDEMEANOR HIT AND RUN": "Traffic",
    "MISDEMEANOR WANT": "Other",
    "MISSING FEMALE": "Missing Person",
    "MISSING FEMALE JUVENILE": "Missing Person",
    "MISSING JUVENILE": "Missing Person",
    "MISSING PERSON": "Missing Person",
    "MISSING PERSON, MENTAL HANDICAP": "Missing Person",
    "MOLEST/ANNOY UNDER 18YRS": "Sex Crime",
    "MURDER": "Assault",
    "NARCOTICS": "Drugs/Alcohol",
    "NARCOTICS, GANG RELATED": "Drugs/Alcohol",
    "OBSCENE OR HARASSING PH CALLS": "Assault",
    "OBSTRUCT STREETS OR SIDEWALK": "Service Call",
    "OPEN DOOR": "Service Call",
    "OPEN WINDOW": "Service Call",
    "PARKING VIOLATION": "Traffic",
    "PAROLE VIOLATION": "Other",
    "PEDESTRIAN STOP": "Other",
    "PEDESTRIAN STOP ON FEMALE": "Other",
    "PERSON CALLING FOR HELP": "Public Safety",
    "PERSON SHOT": "Assault",
    "PERSON STABBED": "Assault",
    "PETTY THEFT": "Larceny",
    "PETTY THEFT (BROADCAST ONLY)": "Larceny",
    "PETTY THEFT PRIOR CONVICTION": "Larceny",
    "POSSESSION OF CONTROLLED SUBSTANCE": "Drugs/Alcohol",
    "POSSESSION OF CONTROLLED SUBSTANCE, GANG RELATED": "Drugs/Alcohol",
    "POSSESSION OF MARIJUANA": "Drugs/Alcohol",
    "POSSESSION OF NARCOTICS": "Drugs/Alcohol",
    "POSSESSION OF NARCOTICS, GANG RELATED": "Drugs/Alcohol",
    "PROWLER": "Suspicious Person",
    "PUBLIC SAFETY ASSISTANCE": "Public Safety",
    "PURSE SNATCH ROBBERY": "Robbery",
    "RECEIVE/POSSESS STOLEN PROP": "Larceny",
    "RECKLESS DRIVING": "Traffic",
    "RECOVERED STOLEN VEHICLE": "Vehicle Break-in/Theft",
    "REFUSAL TO LEAVE PROPERTY": "Trespassing",
    "REGISTRATION OF SEX OFFENDER": "Sex Crime",
    "RESISTING ARREST": "Assault",
    "RESISTING ARREST, GANG RELATED": "Assault",
    "ROBBERY": "Robbery",
    "ROBBERY, GANG RELATED": "Robbery",
    "SHOOTING INTO OCCP VEH OR DWELLING": "Assault",
    "SICK PERSON": "Public Safety",
    "SOLICITING FOR LEWD CONDUCT": "Sex Crime",
    "SOLICITING FOR PROSTITUTION": "Sex Crime",
    "SPEED CONTEST": "Traffic",
    "SPEEDING": "Traffic",
    "STALKING": "Public Safety",
    "STOLEN VEHICLE": "Vehicle Break-in/Theft",
    "STOLEN VEHICLE, GANG RELATED": "Vehicle Break-in/Theft",
    "STRONG ARM ROBBERY": "Robbery",
    "STRONG ARM ROBBERY (COMBINED EVENT)": "Robbery",
    "SUSPICIOUS CIRCUMSTANCES": "Suspicious Person",
    "SUSPICIOUS CIRCUMSTANCES (COMBINED EVENT)": "Suspicious Person",
    "SUSPICIOUS FEMALE": "Suspicious Person",
    "SUSPICIOUS PACKAGE": "Suspicious Person",
    "SUSPICIOUS PERSON": "Suspicious Person",
    "SUSPICIOUS PERSON (GANG)": "Suspicious Person",
    "SUSPICIOUS PERSON ON RUNWAY - SJIA": "Suspicious Person",
    "SUSPICIOUS PERSON W/ WEAPON": "Suspicious Person",
    "SUSPICIOUS VEHICLE": "Suspicious Person",
    "TAKE A REPORT": "Service Call",
    "TAMPERING WITH A VEHICLE": "Vandalism",
    "THEFT": "Larceny",
    "THEFT, GANG RELATED": "Larceny",
    "THEFT OF RECYCLABLES": "Larceny",
    "THROWING SUBSTANCES AT VEHICLE": "Vandalism",
    "TRAFFIC CONTROL": "Traffic",
    "TRAFFIC HAZARD": "Traffic",
    "TRESPASSING": "Trespassing",
    "UNK TYPE 911 CALL": "Other",
    "UNLICENSED DRIVER": "Traffic",
    "USE OF CONTROLLED SUBSTANCE": "Drugs/Alcohol",
    "VAGRANT": "Suspicious Person",
    "VEHICLE ACCIDENT, AMB DISPATCHED": "Vehicle Accident",
    "VEHICLE ACCIDENT, MAJOR INJURIES": "Vehicle Accident",
    "VEHICLE ACCIDENT, MINOR INJURIES": "Vehicle Accident",
    "VEHICLE ACCIDENT, PROPERTY DAMAGE": "Vehicle Accident",
    "VEHICLE ACCIDENT, UNKNOWN INJURIES": "Vehicle Accident",
    "VEHICLE BURGLARY": "Vehicle Break-in/Theft",
    "VEHICLE STOP": "Traffic",
    "VEHICLE STOP ON FEMALE": "Traffic",
    "VEHICLE STOP, SEND FILL": "Traffic",
    "VICIOUS ANIMAL": "Other",
    "VIOLATION OF PROTECTIVE ORDER": "Other",
    "WELFARE CHECK": "Welfare Check",
    "WELFARE CHECK (COMBINED EVENT)": "Welfare Check",
    "W&I-UNDER JURIS OF JUV COURT": "Other",
}


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


def is_cross_street_match(address_str, ns_streets, ew_streets):
    if isinstance(address_str, str) and "&" in address_str:
        ns_lower_no_prefix = [
            re.sub(r"^[ns]\s+", "", s.lower().strip()) for s in ns_streets
        ]
        ew_lower_no_prefix = [
            re.sub(r"^[ew]\s+", "", s.lower().strip()) for s in ew_streets
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
    address_column,
    numeric_address_ranges,
    north_south_streets,
    east_west_streets,
    offense_date_column,
    offense_time_column,
    start_datetime_str,
    end_datetime_str,
    call_type_filter_list=None,
):
    try:
        df = pd.read_csv(csv_filepath)

        # Ensure the address column is treated as string and handle potential NaNs
        df[address_column] = df[address_column].astype(
            str).str.lower().str.strip()
        # Remove rows where the address is 'nan'
        df = df[df[address_column] != "nan"]

        df["CALL_CATEGORY"] = (
            df["CALL_TYPE"].map(call_type_mapping).fillna("Uncategorized")
        )

        # Filter by numeric address ranges (only if '&' is NOT present)
        numeric_filtered_df = df[
            df[address_column].apply(
                lambda x: "&" not in x
                and matches_numeric_range(x, numeric_address_ranges)
            )
        ].copy()

        # Filter by cross streets (only if '&' IS present)
        cross_street_filtered_df = df[
            df[address_column].apply(
                lambda x: "&" in x
                and is_cross_street_match(x, north_south_streets, east_west_streets)
            )
        ].copy()

        # Combine the two address-filtered DataFrames
        combined_address_df = pd.concat(
            [numeric_filtered_df, cross_street_filtered_df]
        ).drop_duplicates()

        # --- Datetime Conversion and Filtering ---
        if not combined_address_df.empty:
            date_format = "%m/%d/%Y %I:%M:%S %p"
            combined_address_df["OFFENSE_DATETIME"] = (
                pd.to_datetime(
                    combined_address_df[offense_date_column], format=date_format
                ).dt.date.astype(str)
                + " "
                + combined_address_df[offense_time_column]
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
        else:
            return pd.DataFrame()
            datetime_filtered_df = pd.DataFrame()

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

    except FileNotFoundError:
        print(f"Error: The file '{csv_filepath}' was not found.")
        return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()


file_url = "https://data.sanjoseca.gov/dataset/c5929f1b-7dbe-445e-83ed-35cca0d3ca8b/resource/0bc5ea69-fcc7-4998-ab6c-70c3a0df778b/download/policecalls2025.csv"
csv_file = "policecalls.csv"

if not os.path.exists(csv_file):
    download_file(file_url, csv_file)

address_column = "ADDRESS"
numeric_ranges = [
    (500, 899, "N 2ND ST"),
    (500, 899, "N 3RD ST"),
    (500, 899, "N 4TH ST"),
    (500, 899, "N 5TH ST"),
    (500, 899, "N 6TH ST"),
    (500, 899, "N 7TH ST"),
    (500, 899, "N 8TH ST"),
    (500, 899, "N 9TH ST"),
    (0, 400, "E EMPIRE ST"),
    (0, 400, "JACKSON ST"),
    (0, 400, "E TAYLOR ST"),
    (0, 400, "E MISSION ST"),
    (0, 400, "E HEDDING ST"),
]
north_south_streets_list = [
    "N 2ND ST",
    "N 3RD ST",
    "N 4TH ST",
    "N 5TH ST",
    "N 6TH ST",
    "N 7TH ST",
    "N 8TH ST",
    "N 9TH ST",
]
east_west_streets_list = [
    "EMPIRE ST",
    "JACKSON ST",
    "TAYLOR ST",
    "MISSION ST",
    "HEDDING ST",
]
offense_date_column_name = "OFFENSE_DATE"
offense_time_column_name = "OFFENSE_TIME"
start_datetime_filter = "2025-04-01 00:00:00"
end_datetime_filter = "2025-04-30 23:59:59"
call_types_to_include = []

filtered_data = filter_data_by_address_and_offense_datetime(
    csv_file,
    address_column,
    numeric_ranges,
    north_south_streets_list,
    east_west_streets_list,
    offense_date_column_name,
    offense_time_column_name,
    start_datetime_filter,
    end_datetime_filter,
    call_types_to_include,
)

if not filtered_data.empty:
    filtered_data.to_csv("crimes.csv", index=False)

    category_counts = filtered_data["CALL_CATEGORY"].value_counts(
    ).reset_index()
    category_counts.columns = ["Category", "Incidents"]

    markdown_table = category_counts.to_markdown(
        index=False, tablefmt="mixed_outline")
    print(markdown_table)

    type_counts = filtered_data["CALL_TYPE"].value_counts().reset_index()
    type_counts.columns = ["CALL_TYPE", "Number of Incidents"]

    markdown_table = type_counts.to_markdown(
        index=False, tablefmt="mixed_outline")
    print(markdown_table)
else:
    print("\nNo data matches the specified criteria.")
