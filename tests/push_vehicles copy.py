import pandas as pd
import requests
import json
from datetime import datetime
from requests.auth import HTTPBasicAuth


def push_maintenance_to_endpoint(df, endpoint_url, username, password):
    """
    Pushes maintenance data from a pandas DataFrame to an OData endpoint.
    The data schema is 'serialNo', 'description', 'entryType', 'postingDate', and 'value'.
    """
    print(f"Attempting to push {len(df)} records to {endpoint_url}...")
    headers = {"Content-Type": "application/json"}
    auth = HTTPBasicAuth(username, password)

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
                "description": row.get("description", "Update from Telematics"),
                "entryType": str(row["entryType"]),  # CONVERT TO STRING HERE
                "postingDate": post_date,
                "assetEntryNo": row["assetEntryNo"],
                "value": float(row["value"]),
            }

        except (KeyError, ValueError, TypeError) as e:
            print(f"Skipping row {index} due to data error: {e}")
            continue

        try:
            # Use the `json` parameter to automatically handle headers and serialization
            response = requests.post(
                endpoint_url, json=payload, headers=headers, auth=auth
            )

            if response.status_code == 201:
                print(f"Successfully pushed row {index} for asset: {row['serialNo']}")
            else:
                print(
                    f"Failed to push row {index} for asset: {row['serialNo']}. "
                    f"Status code: {response.status_code}"
                )
                print(f"Response body: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while pushing row {index}: {e}")


# Usage example
if __name__ == "__main__":
    # Define a sample DataFrame with the required columns.
    sample_data = {
        "serialNo": ["KCW025W"],
        "description": ["Update from Compliance Tool"],
        "entryType": [2],  # The code will now convert this to a string
        "postingDate": ["2025-09-10"],
        "assetEntryNo": [49],
        "value": [6000.0],
    }
    df = pd.DataFrame(sample_data)

    # API endpoint and authentication details
    api_endpoint = (
        "http://bcsqluat.oshochem.net:6048/BC240P/ODataV4/MaintenanceEntriesAPI"
    )
    api_username = "oshochemicals\\navdev"
    api_password = "Kolopa@2025"
    if not df.empty:
        print(f"Extracted {len(df)} rows for {df['serialNo'].nunique()} assets")
        print("\nFirst few rows:")
        print(df.head())

        # Push the data to the API endpoint
        push_maintenance_to_endpoint(df, api_endpoint, api_username, api_password)
    else:
        print("No data found in the DataFrame.")
