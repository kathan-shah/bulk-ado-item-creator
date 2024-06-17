import requests
from requests.auth import HTTPBasicAuth
import json
import base64
import csv

# Azure DevOps details
organization = "org-name"
project = "project-name"
personal_access_token = "pat from ADO"
base_url = f"https://dev.azure.com/{organization}/{project}"

# IDs of the existing test plan and test suite
plan_id = 524014
suite_id = "524259"
area_path = "Commercial-Dental\Eaglesoft\Database\SQL Migration"
csv_file_path = "path to csv"

# Example usage
test_case_steps = [
    {"action": "Run pgMigrationValidator data matching endpoint to compare sqlAnywhere and postgres data", "expected": "The console window shows Pass percentage: 100%"},
    {"action": "Test Insert on table", "expected": "Valid insert statement inserts without any issues"},
    {"action": "Test Delete on table", "expected": "Valid delete statement deletes the inserted row without any issues"}
]

# Prepare the authorization header with the PAT
pat_token = ':{}'.format(personal_access_token).encode('utf-8')
auth_header = 'Basic {}'.format(base64.b64encode(pat_token).decode('utf-8'))

# Headers for API requests
headers = {
    "Content-Type": "application/json-patch+json",
    "Authorization": auth_header
}

# Function to create a test case
def create_test_case(title, steps, area_path):
    url = f"{base_url}/_apis/wit/workitems/$Test Case?api-version=6.0"
    # Dynamically build the steps XML based on the steps list
    steps_xml_parts = []
    for i, step in enumerate(steps, start=1):
        step_xml = f"""
        <step id="{i}" type="ActionStep">
            <parameterizedString isformatted="true">{step['action']}</parameterizedString>
            <parameterizedString isformatted="true">{step['expected']}</parameterizedString>
            <description/>
        </step>
        """
        steps_xml_parts.append(step_xml)

    # Combine all step parts into the final XML structure
    steps_formatted = f"""
    <steps id="0" last="{len(steps)}">
        {''.join(steps_xml_parts)}
    </steps>
    """
    payload = [
        {
            "op": "add",
            "path": "/fields/System.Title",
            "value": title
        },
        {
            "op": "add",
            "path": "/fields/Microsoft.VSTS.TCM.Steps",
            "value": steps_formatted
        },
        {
            "op": "add",
            "path": "/fields/System.AreaPath",
            "value": area_path  # Assigning area path to the test case
        }
    ]
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(f"Error creating test case: {response.status_code}")
        print(response.text)
        return None


def link_test_case_to_work_item(test_case_id, work_item_id):
    url = f"{base_url}/_apis/wit/workitems/{test_case_id}?api-version=6.0"

    payload = [
        {
            "op": "add",
            "path": "/relations/-",
            "value": {
                "rel": "Microsoft.VSTS.Common.TestedBy-Reverse",
                "url": f"{base_url}/_apis/wit/workItems/{work_item_id}",
                "attributes": {
                    "comment": "Linking Test Case to Work Item"
                }
            }
        }
    ]
    response = requests.patch(url, headers=headers, json=payload)
    if response.status_code in [200, 201]:
        print("Test case linked to work item successfully.")
    else:
        print(f"Failed to link test case to work item: {response.status_code}")
        print(response.text)

# Read CSV file and create test cases
def create_test_cases_from_csv(csv_file_path):
    with open(csv_file_path, mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            pbi_id = row["ID"]
            test_case_title = "QA " + row["Title"]
            test_case_response = create_test_case(test_case_title, test_case_steps, area_path)
            if test_case_response:
                test_case_id = test_case_response["id"]
                link_test_case_to_work_item(test_case_id, pbi_id)
            else:
                print(f"Failed to create test case for PBI ID: {pbi_id}")
# Create a test case
# test_case_response = create_test_case(test_case_title, test_case_steps, area_path)
# if test_case_response:
#     test_case_id = test_case_response["id"]
#     # Add the test case to the test suite
#     link_test_case_to_work_item(test_case_id, pbi_id)

create_test_cases_from_csv(csv_file_path)



