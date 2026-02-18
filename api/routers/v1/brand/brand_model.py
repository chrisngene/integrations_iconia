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


def get_brand_data() -> List[Dict]:
    """

    """
    #  select the choice from the choice details table where choice_id = 258
    db


    return generate_json_output(df_latest)


# print(get_brand_data())

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
