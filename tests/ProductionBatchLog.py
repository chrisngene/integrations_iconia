import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from urllib.parse import quote
import logging

# --- Configure logging for detailed requests output (useful for debugging) ---
logging.basicConfig(level=logging.INFO)  # Set to INFO for less verbose, DEBUG for full details
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.INFO)
requests_log.propagate = True

# --- Configuration ---
# IMPORTANT: Replace with your actual username and password that work with Basic Auth.
username = 'oshochemicals\\navdev'
password = 'Kolopa@2025'

# Base URL for Business Central OData
# CORRECTED: Removed the duplicate 'Industries' from the company name
BC_BASE_URL = "https://oshobc.oshochem.net:4049/CRM/ODataV4/Company('Osho%20Chemical%20Industries%20Ltd')"

# Specific OData endpoints you want to fetch
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
# --- SSL Verification Option ---
VERIFY_SSL = True # Keep this True for secure connections. Set to False for testing if needed.

print(f"Using username: {username}")
print(f"SSL Verification: {'Enabled' if VERIFY_SSL else 'DISABLED (INSECURE)'}")

def fetch_odata_data(endpoint_name, base_url, auth_session, verify_ssl):
    """
    Fetches data from a specified Business Central OData endpoint.

    Args:
        endpoint_name (str): The name of the OData endpoint (e.g., "OshoProductionOrder").
        base_url (str): The base URL for the Business Central OData API.
        auth_session (requests.Session): A requests session pre-configured with authentication.
        verify_ssl (bool): Whether to verify SSL certificates.

    Returns:
        pandas.DataFrame or None: A DataFrame with the fetched data, or None if an error occurred.
    """
    full_url = f"{base_url}/{endpoint_name}"
    print(f"\n--- Attempting to fetch data from: {full_url} ---")

    try:
        response = auth_session.get(
            full_url,
            headers={'Accept': 'application/json'},
            verify=verify_ssl
        )
        response.raise_for_status() # Raise an exception for HTTP errors

        data = response.json()
        records = data.get('value', [])

        if not records:
            print(f"No records found in the 'value' array for {endpoint_name}.")
            return pd.DataFrame() # Return empty DataFrame if no records
        else:
            df = pd.DataFrame(records)

            # Attempt to convert common date columns, coercing errors
            for col in ['Manufacturing_Date', 'Expiration_Date', 'Date']: # Add other common date column names here
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')

            print(f"Successfully fetched {len(df)} records from {endpoint_name}.")
            return df

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error fetching data from {endpoint_name}: {e}")
        print(f"Status Code: {e.response.status_code}")
        if e.response.text and len(e.response.text) < 1000:
            print(f"Response Body: {e.response.text}")
        else:
            print(f"Response Body (truncated/large): {e.response.text[:500]}...")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error fetching data from {endpoint_name}: {e}")
        print(f"Ensure the URL is correct, server is reachable, and check firewall/SSL settings.")
        return None
    except ValueError as e:
        print(f"Error parsing JSON response from {endpoint_name}: {e}")
        print(f"Response content might not be valid JSON.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching data from {endpoint_name}: {e}")
        return None

if __name__ == "__main__":
    # Create a single session with Basic authentication
    session = requests.Session()
    session.auth = HTTPBasicAuth(username, password)

    # Dictionary to hold our DataFrames
    dataframes = {}

    for name, endpoint in ENDPOINTS.items():
        df = fetch_odata_data(endpoint, BC_BASE_URL, session, VERIFY_SSL)
        if df is not None: # Only store if fetching was successful (not None)
            dataframes[name] = df

    # --- Filtering and Merging Logic ---
    df_production_order = dataframes.get("OshoProductionOrder")
    df_production_batch_log = dataframes.get("ProductionBatchLog")

    final_output_df = pd.DataFrame() # Initialize an empty DataFrame for the final output

    if df_production_order is not None and not df_production_order.empty:
        # 1. Filter OshoProductionOrder for "AuxiliaryIndex1": "Released"
        filtered_production_order = df_production_order[
            (df_production_order['AuxiliaryIndex1'] == 'Released')
        ].copy()
        print(f"\nFiltered OshoProductionOrder (AuxiliaryIndex1 == 'Released'): {len(filtered_production_order)} records.")

        if not filtered_production_order.empty:
            # 2. Get unique AuxiliaryIndex2 values (Production Order Nos)
            #    and the Item_Description and Planned_Quantity for merging
            production_order_details_for_merge = filtered_production_order[[
                'AuxiliaryIndex2', 'Item_Description', 'Planned_Quantity'
            ]].drop_duplicates(subset=['AuxiliaryIndex2']).rename(
                columns={'AuxiliaryIndex2': 'Production_Order_No'}
            )
            print(f"Unique Production Order Nos and associated details from filtered OshoProductionOrder: {len(production_order_details_for_merge)} entries.")

            if df_production_batch_log is not None and not df_production_batch_log.empty:
                # 3. First filter ProductionBatchLog for "Type": "Local"
                filtered_batch_log = df_production_batch_log[
                    df_production_batch_log['Type'] == 'Local'
                ].copy()
                print(f"ProductionBatchLog filtered by Type == 'Local': {len(filtered_batch_log)} records.")

                # 4. Then filter by Production_Order_No values from OshoProductionOrder
                filtered_batch_log = filtered_batch_log[
                    filtered_batch_log['Production_Order_No'].isin(
                        production_order_details_for_merge['Production_Order_No']
                    )
                ].copy()

                # 5. Merge Item_Description and Planned_Quantity into the filtered ProductionBatchLog
                final_output_df = pd.merge(
                    filtered_batch_log,
                    production_order_details_for_merge,
                    on='Production_Order_No',
                    how='left'
                )

                # Select only the required columns in the specified order
                final_output_df = final_output_df[[
                    'Production_Order_No', 'Entry_No', 'Manufacturing_Date', 
                    'Bulk_Batch_No', 'Finished_Batch_No', 'Expiration_Date', 
                    'Type', 'Item_Description', 'Planned_Quantity'
                ]]

                print("\n--- Final Filtered ProductionBatchLog Data with Merged Columns: ---")
                if not final_output_df.empty:
                    print(final_output_df.head())
                    print(f"Total rows in final output: {len(final_output_df)}")
                else:
                    print("No matching records found in ProductionBatchLog for the filtered Production Orders after Type='Local' filter.")
            else:
                print("ProductionBatchLog DataFrame is empty or could not be fetched. Cannot perform merging.")
        else:
            print("No records found in OshoProductionOrder matching the specified filters ('Released').")
    else:
        print("OshoProductionOrder DataFrame is empty or could not be fetched. Cannot perform filtering or merging.")

    # export final_output_df to CSV if it exists and is not empty
    # if not final_output_df.empty:
    #     final_output_df.to_csv('filtered_production_batch_log.csv', index=False)
    #     print("Filtered ProductionBatchLog exported to 'filtered_production_batch_log.csv'.")
    # else:
    #     print("No final ProductionBatchLog to export.")

    # Then modify the export section of your code (replace the current CSV export part):
    if not final_output_df.empty:
        # 1. Export to CSV as before
        final_output_df.to_csv('filtered_production_batch_log.csv', index=False)
        print("Filtered ProductionBatchLog exported to 'filtered_production_batch_log.csv'.")
        
        # 2. Create the JSON output in both formats
        json_output = []
        numbered_json_output = []
        
        # Select only the columns we want in the output
        output_columns = [
            'Item_Description', 'Production_Order_No', 'Manufacturing_Date',
            'Bulk_Batch_No', 'Expiration_Date', 'Planned_Quantity'
        ]
        
        for _, row in final_output_df[output_columns].iterrows():
            # Create the named JSON object
            # named_entry = {
            #     "Item_Description": str(row['Item_Description']),
            #     "Production_Order_No": str(row['Production_Order_No']),
            #     "Manufacturing_Date": str(row['Manufacturing_Date']),
            #     "Bulk_Batch_No": str(row['Bulk_Batch_No']),
            #     "Expiration_Date": str(row['Expiration_Date']),
            #     "Planned_Quantity": float(row['Planned_Quantity'])
            # }
            # json_output.append(named_entry)
            
            # Create the numbered JSON object
            numbered_entry = {
                COLUMN_MAPPING["Item_Description"]: str(row['Item_Description']),
                COLUMN_MAPPING["Production_Order_No"]: str(row['Production_Order_No']),
                COLUMN_MAPPING["Manufacturing_Date"]: str(row['Manufacturing_Date']),
                COLUMN_MAPPING["Bulk_Batch_No"]: str(row['Bulk_Batch_No']),
                COLUMN_MAPPING["Expiration_Date"]: str(row['Expiration_Date']),
                COLUMN_MAPPING["Planned_Quantity"]: float(row['Planned_Quantity'])
            }
            numbered_json_output.append(numbered_entry)
        
        # Export both JSON formats
        import json
        
        # with open('production_data_named.json', 'w') as f:
        #     json.dump(json_output, f, indent=2)
        
        with open('production_data_numbered.json', 'w') as f:
            json.dump(numbered_json_output, f, indent=2)
        
        print("Data also exported to JSON formats:")
        # print("- production_data_named.json (with field names)")
        print("- production_data_numbered.json (with numbered fields)")
        
        # Print a sample of each format
        # print("\nSample named JSON output:")
        # print(json.dumps(json_output[0], indent=2) if json_output else "No data")
        
        print("\nSample numbered JSON output:")
        print(json.dumps(numbered_json_output[0], indent=2) if numbered_json_output else "No data")
    else:
        print("No final ProductionBatchLog to export.")