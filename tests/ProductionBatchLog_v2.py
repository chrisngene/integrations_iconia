import json
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from urllib.parse import quote
import logging
from typing import Dict, Optional, List

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.INFO)
requests_log.propagate = True

# Configuration
username = 'oshochemicals\\navdev'
password = 'Kolopa@2025'
BC_BASE_URL = "https://oshobc.oshochem.net:4049/CRM/ODataV4/Company('Osho%20Chemical%20Industries%20Ltd')"
VERIFY_SSL = True

ENDPOINTS = {
    "OshoProductionOrder": "OshoProductionOrder",
    "ProductionBatchLog": "ProductionBatchLog"
}

COLUMN_MAPPING = {
    "Item_Description": "3",
    "Production_Order_No": "14",
    "Manufacturing_Date": "6",
    "Bulk_Batch_No": "5",
    "Expiration_Date": "7",
    "Planned_Quantity": "4"
}

logger.info(f"Using username: {username}")
logger.info(f"SSL Verification: {'Enabled' if VERIFY_SSL else 'DISABLED (INSECURE)'}")


def fetch_odata_data(endpoint_name: str, base_url: str, auth_session: requests.Session, verify_ssl: bool) -> Optional[pd.DataFrame]:
    """
    Fetches data from a specified Business Central OData endpoint.

    Args:
        endpoint_name: The name of the OData endpoint (e.g., "OshoProductionOrder")
        base_url: The base URL for the Business Central OData API
        auth_session: A requests session pre-configured with authentication
        verify_ssl: Whether to verify SSL certificates

    Returns:
        A DataFrame with the fetched data, or None if an error occurred
    """
    full_url = f"{base_url}/{endpoint_name}"
    logger.info(f"Attempting to fetch data from: {full_url}")

    try:
        response = auth_session.get(
            full_url,
            headers={'Accept': 'application/json'},
            verify=verify_ssl
        )
        response.raise_for_status()

        data = response.json()
        records = data.get('value', [])

        if not records:
            logger.info(f"No records found in the 'value' array for {endpoint_name}.")
            return pd.DataFrame()
        
        df = pd.DataFrame(records)

        # Convert common date columns
        for col in ['Manufacturing_Date', 'Expiration_Date', 'Date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        logger.info(f"Successfully fetched {len(df)} records from {endpoint_name}.")
        return df

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error fetching data from {endpoint_name}: {e}")
        logger.error(f"Status Code: {e.response.status_code}")
        if e.response.text and len(e.response.text) < 1000:
            logger.error(f"Response Body: {e.response.text}")
        else:
            logger.error(f"Response Body (truncated): {e.response.text[:500]}...")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection Error fetching data from {endpoint_name}: {e}")
    except ValueError as e:
        logger.error(f"Error parsing JSON response from {endpoint_name}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error fetching data from {endpoint_name}: {e}")
    
    return None


def process_data(dataframes: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Process and merge the data from different endpoints.
    
    Args:
        dataframes: Dictionary containing the fetched DataFrames
        
    Returns:
        Processed DataFrame with merged data
    """
    df_production_order = dataframes.get("OshoProductionOrder")
    df_production_batch_log = dataframes.get("ProductionBatchLog")
    final_output_df = pd.DataFrame()

    if df_production_order is not None and not df_production_order.empty:
        filtered_production_order = df_production_order[
            (df_production_order['AuxiliaryIndex1'] == 'Released')
        ].copy()
        logger.info(f"Filtered OshoProductionOrder (Released): {len(filtered_production_order)} records.")

        if not filtered_production_order.empty:
            production_order_details_for_merge = filtered_production_order[[
                'AuxiliaryIndex2', 'Item_Description', 'Planned_Quantity'
            ]].drop_duplicates(subset=['AuxiliaryIndex2']).rename(
                columns={'AuxiliaryIndex2': 'Production_Order_No'}
            )
            logger.info(f"Unique Production Order Nos: {len(production_order_details_for_merge)}")

            if df_production_batch_log is not None and not df_production_batch_log.empty:
                filtered_batch_log = df_production_batch_log[
                    df_production_batch_log['Type'] == 'Local'
                ].copy()
                logger.info(f"ProductionBatchLog filtered (Local): {len(filtered_batch_log)} records.")

                filtered_batch_log = filtered_batch_log[
                    filtered_batch_log['Production_Order_No'].isin(
                        production_order_details_for_merge['Production_Order_No']
                    )
                ].copy()

                final_output_df = pd.merge(
                    filtered_batch_log,
                    production_order_details_for_merge,
                    on='Production_Order_No',
                    how='left'
                )

                final_output_df = final_output_df[[
                    'Production_Order_No', 'Entry_No', 'Manufacturing_Date', 
                    'Bulk_Batch_No', 'Finished_Batch_No', 'Expiration_Date', 
                    'Type', 'Item_Description', 'Planned_Quantity'
                ]]

                if not final_output_df.empty:
                    logger.info(f"Final output contains {len(final_output_df)} records.")
                else:
                    logger.warning("No matching records found after all filters.")
            else:
                logger.warning("ProductionBatchLog DataFrame is empty or missing.")
        else:
            logger.warning("No records found in OshoProductionOrder matching 'Released' filter.")
    else:
        logger.warning("OshoProductionOrder DataFrame is empty or missing.")

    return final_output_df


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
        output_columns = [
            'Item_Description', 'Production_Order_No', 'Manufacturing_Date',
            'Bulk_Batch_No', 'Expiration_Date', 'Planned_Quantity'
        ]
        
        for _, row in final_output_df[output_columns].iterrows():
            entry = {
                "item_description": {
                    COLUMN_MAPPING["Item_Description"]: str(row['Item_Description'])
                },
                "data": {
                    COLUMN_MAPPING["Production_Order_No"]: str(row['Production_Order_No']),
                    COLUMN_MAPPING["Manufacturing_Date"]: str(row['Manufacturing_Date']),
                    COLUMN_MAPPING["Bulk_Batch_No"]: str(row['Bulk_Batch_No']),
                    COLUMN_MAPPING["Expiration_Date"]: str(row['Expiration_Date']),
                    COLUMN_MAPPING["Planned_Quantity"]: float(row['Planned_Quantity'])
                }
            }
            json_output.append(entry)
    
    return json_output


def get_production_data() -> List[Dict]:
    """
    Main function to fetch and process production data.
    
    Returns:
        List of dictionaries containing the production data in new format
    """
    session = requests.Session()
    session.auth = HTTPBasicAuth(username, password)

    dataframes = {}
    for name, endpoint in ENDPOINTS.items():
        df = fetch_odata_data(endpoint, BC_BASE_URL, session, VERIFY_SSL)
        if df is not None:
            dataframes[name] = df

    final_output_df = process_data(dataframes)
    return generate_json_output(final_output_df)

# FastAPI endpoint would look like this:
# from fastapi import FastAPI
# app = FastAPI()
# 
# @app.get("/production-data")
# async def production_data():
#     return get_production_data()

# save json output to a file
with open("production_data.json", "w") as json_file:
    json.dump(get_production_data(), json_file, indent=4)