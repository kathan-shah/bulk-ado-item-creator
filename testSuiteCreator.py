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
parent_suite_id = "524259"
csv_file_path = "path to csv"

# Prepare the authorization header with the PAT
pat_token = ':{}'.format(personal_access_token).encode('utf-8')
auth_header = 'Basic {}'.format(base64.b64encode(pat_token).decode('utf-8'))

# Headers for API requests
headers = {
    "Content-Type": "application/json",
    "Authorization": auth_header
}

def create_requirement_based_suite_under_parent(plan_id, suite_id, suite_name, work_item_id):
    url = f"{base_url}/_apis/testplan/Plans/{plan_id}/suites?api-version=7.1-preview.1"
    payload = {
        "name": suite_name,
        "suiteType": "requirementTestSuite",
        "requirementId": work_item_id,
        "parentSuite": {
            "id": suite_id
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code in [200, 201]:
        print("Requirement-based suite created successfully under parent suite.")
        return response.json()
    else:
        print(f"Failed to create requirement-based suite under parent suite: {response.status_code}")
        print(response.text)
        return None
    
# Function to read from CSV and create test suites
def create_test_suites_from_csv(csv_file_path, plan_id, parent_suite_id):
    with open(csv_file_path, mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            work_item_id = row["ID"]
            suite_name = row["Title"]
            suite_creation_response = create_requirement_based_suite_under_parent(plan_id, parent_suite_id, suite_name, work_item_id)
            # if suite_creation_response:
            #     print(suite_creation_response)
    

create_test_suites_from_csv(csv_file_path, plan_id, parent_suite_id)