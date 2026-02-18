import json
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from urllib.parse import quote
import logging
from typing import Dict, Optional, List
from dotenv import dotenv_values

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.INFO)
requests_log.propagate = True

config = dotenv_values(".env")


# Configuration
BC_USERNAME = config.get("BC_USERNAME")
BC_PASSWORD = config.get("BC_PASSWORD")
VEHICLES_INSPECTION_URL = config.get("VEHICLES_INSPECTION_URL")
NEXTSERVICE_URL = config.get("NEXTSERVICE_URL")

VERIFY_SSL = True

print(VEHICLES_INSPECTION_URL, BC_USERNAME, BC_PASSWORD)

COLUMN_MAPPING = {
    "serialNo": "507",
    "value": "509",
    "Next_Service_Value": "510",
}

logger.info(f"Using username: {BC_USERNAME}")
logger.info(f"SSL Verification: {'Enabled' if VERIFY_SSL else 'DISABLED (INSECURE)'}")


def fetch_odata_data(
    base_url: str, auth_session: requests.Session, verify_ssl: bool
) -> Optional[pd.DataFrame]:
    """
    Fetches data from the specified Business Central OData endpoint.

    Args:
        base_url (str): The base URL for the Business Central OData API
        auth_session (requests.Session): A requests session pre-configured with authentication
        verify_ssl (bool): Whether to verify SSL certificates

    Returns:
        A DataFrame with the fetched data, or None if an error occurred
    """

    full_url = f"{base_url}"
    logger.info(f"Attempting to fetch data from: {full_url}")

    try:
        response = auth_session.get(
            full_url, headers={"Accept": "application/json"}, verify=verify_ssl
        )
        response.raise_for_status()

        data = response.json()
        records = data.get("value", [])

        if not records:
            logger.info(
                f"No records found in the 'value' array for the vehicles inspection endpoint."
            )
            return pd.DataFrame()

        df = pd.DataFrame(records)
        
        # print(df.head())
        
        # Convert common date columns
        for col in ["postingDate"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        logger.info(
            f"Successfully fetched {len(df)} records from vehicles inspection endpoint."
        )
        return df

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error fetching data from vehicles inspection endpoint: {e}")
        logger.error(f"Status Code: {e.response.status_code}")
        if e.response.text and len(e.response.text) < 1000:
            logger.error(f"Response Body: {e.response.text}")
        else:
            logger.error(f"Response Body (truncated): {e.response.text[:500]}...")
    except requests.exceptions.ConnectionError as e:
        logger.error(
            f"Connection Error fetching data from vehicles inspection endpoint: {e}"
        )
    except ValueError as e:
        logger.error(
            f"Error parsing JSON response from vehicles inspection endpoint: {e}"
        )
    except Exception as e:
        logger.error(
            f"Unexpected error fetching data from vehicles inspection endpoint: {e}"
        )

    return None


def fetch_nextservice_data(
    base_url: str, auth_session: requests.Session, verify_ssl: bool
) -> Optional[pd.DataFrame]:
    """
    Fetches data from the specified Business Central OData endpoint.

    Args:
        base_url (str): The base URL for the Business Central OData API
        auth_session (requests.Session): A requests session pre-configured with authentication
        verify_ssl (bool): Whether to verify SSL certificates

    Returns:
        A DataFrame with the fetched data, or None if an error occurred
    """

    full_url = f"{base_url}"
    logger.info(f"Attempting to fetch data from: {full_url}")

    try:
        response = auth_session.get(
            full_url, headers={"Accept": "application/json"}, verify=verify_ssl
        )
        response.raise_for_status()

        data = response.json()
        records = data.get("value", [])

        if not records:
            logger.info(
                f"No records found in the 'value' array for the vehicles inspection endpoint."
            )
            return pd.DataFrame()

        df = pd.DataFrame(records)
        
        # print(df.head())
        
        # Convert common date columns
        for col in ["postingDate"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        logger.info(
            f"Successfully fetched {len(df)} records from vehicles inspection endpoint."
        )
        return df

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error fetching data from vehicles inspection endpoint: {e}")
        logger.error(f"Status Code: {e.response.status_code}")
        if e.response.text and len(e.response.text) < 1000:
            logger.error(f"Response Body: {e.response.text}")
        else:
            logger.error(f"Response Body (truncated): {e.response.text[:500]}...")
    except requests.exceptions.ConnectionError as e:
        logger.error(
            f"Connection Error fetching data from vehicles inspection endpoint: {e}"
        )
    except ValueError as e:
        logger.error(
            f"Error parsing JSON response from vehicles inspection endpoint: {e}"
        )
    except Exception as e:
        logger.error(
            f"Unexpected error fetching data from vehicles inspection endpoint: {e}"
        )

    return None

def generate_json_output(final_output_df: pd.DataFrame) -> List[Dict]:
    """
    Generate the JSON output in the new format with item_description separated.

    Args:
        final_output_df: Processed DataFrame

    Returns:
        List of dictionaries in the new format
    """
    json_output = []

    if not final_output_df.empty:
        output_columns = ["serialNo", "value", "Next_Service_Value"]

        for _, row in final_output_df[output_columns].iterrows():
            entry = {
                "item_description": {COLUMN_MAPPING["serialNo"]: str(row["serialNo"])},
                "data": {
                    COLUMN_MAPPING["value"]: str(row["value"]),
                    COLUMN_MAPPING["Next_Service_Value"]: str(row["Next_Service_Value"]),
                },
            }
            json_output.append(entry)

    return json_output


# print(generate_json_output)


def get_vehicles_data() -> List[Dict]:
    """
    Main function to fetch, process, and return the latest
    maintenance entry for each vehicle.

    Returns:
        List of dictionaries containing the latest vehicle data in the new format.
    """
    session = requests.Session()
    session.auth = HTTPBasicAuth(BC_USERNAME, BC_PASSWORD)

    dataframes = {}
    df = fetch_odata_data(VEHICLES_INSPECTION_URL, session, VERIFY_SSL)
    df2 = fetch_nextservice_data(NEXTSERVICE_URL, session, VERIFY_SSL)

    # print(df2.head())
    # to csv for debugging
    # df2.to_csv("nextservice_data.csv", index=False)
    
    # print all columns of df
    
    # return df
    # if df is not None:
    #     dataframes = df
    if df is None or df.empty:
        logger.info("No data fetched. Returning an empty list.")
        return []

    # Process the DataFrame to get the latest entry for each serial number
    # 1. Sort by 'Entry_No' in descending order
    df_sorted = df.sort_values(by="Entry_No", ascending=False)
    
    # print(f"df_sorted shape: {df_sorted.shape}")

    # 2. Drop duplicates based on 'serialNo', keeping the first occurrence
    #    which is now the one with the highest 'Entry_No'
    df_latest = df_sorted.drop_duplicates(subset=["serialNo"], keep="first")

    # on df_latest i have a column called serialNo and i want to merge it with df2 on a column called
    # Serial_No to get a column called Next_Service_Value. i then want to add this new column to df_latest with name Next_Service_Value
    df_latest = df_latest.merge(
        df2[["Serial_No", "Next_Service_Value"]],
        left_on="serialNo",
        right_on="Serial_No",
        how="left",
    ).drop(columns=["Serial_No"])

    # print(f"df_latest data: {df_latest}")
    # # print to csv for debugging
    # df_latest.to_csv("vehicles_inspection_latest.csv", index=False)

    # 3. filter to only show where column description has value "Update from telematics" or starts with "Service:"
    # df_latest = df_latest[
    #     (df_latest["description"] == "Update from Compliance Tool") |
    #     (df_latest["description"].str.startswith("Service:"))
    # ]

    # print(df_latest)
    # return df_latest.to_dict(orient='records')

    return generate_json_output(df_latest)


# print(get_vehicles_data())

# FastAPI endpoint would look like this:
# from fastapi import FastAPI
# app = FastAPI()
#
# @app.get("/production-data")
# async def production_data():
#     return get_production_data()

# save json output to a file
# with open("production_data.json", "w") as json_file:
#     json.dump(get_production_data(), json_file, indent=4)


def push_maintenance_to_endpoint(df):
    """
    Pushes maintenance data from a pandas DataFrame to an OData endpoint.
    The data schema is 'serialNo', 'description', 'entryType', 'postingDate', and 'value'.
    """
    logger.info(f"Attempting to push {len(df)} records to {VEHICLES_INSPECTION_URL}...")
    headers = {"Content-Type": "application/json"}
    auth = HTTPBasicAuth(BC_USERNAME, BC_PASSWORD)

    for index, row in df.iterrows():
        # Sanitize and prepare the payload
        try:
            # Ensure 'postingDate' is in the correct YYYY-MM-DD format
            if pd.notna(row["postingDate"]):
                # Assuming the date is a datetime object or a string that can be parsed
                post_date = pd.to_datetime(row["postingDate"]).strftime("%Y-%m-%d")
            else:
                post_date = None

            payload = {
                "serialNo": row["serialNo"],
                "description": str(
                    row["description"]
                ),  # row.get("description", "Update from Telematics"),
                "entryType": str(row["entryType"]),  # CONVERT TO STRING HERE
                "postingDate": post_date,
                "Next_Service_Value": row["Next_Service_Value"],
                "value": float(row["value"]),
            }

        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Skipping row {index} due to data error: {e}")
            continue

        try:
            # Use the `json` parameter to automatically handle headers and serialization
            response = requests.post(
                VEHICLES_INSPECTION_URL, json=payload, headers=headers, auth=auth
            )

            if response.status_code == 201:
                logger.info(
                    f"Successfully pushed row {index} for asset: {row['serialNo']}"
                )
                return "Success"
            else:
                logger.error(
                    f"Failed to push row {index} for asset: {row['serialNo']}. "
                    f"Status code: {response.status_code}"
                )
                logger.error(f"Response body: {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred while pushing row {index}: {e}")
