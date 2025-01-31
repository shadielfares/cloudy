import requests
import json

# Terraform Cloud API details
terraform_cloud_url = "https://app.terraform.io/api/v2"
org_name = "for_hack_uoft"  # Your Terraform Cloud organization name
workspace_id = "sddc"  # The workspace ID you provided
api_token = "cddcc"  # Terraform Cloud API token

# User credentials and terraform script (received from frontend)
user_aws_access_key = "cddcc"
user_aws_secret_key = "dczc"
terraform_script = """
provider "aws" {
  region = "us-east-1"
  access_key = "${var.AWS_ACCESS_KEY}"
  secret_key = "${var.AWS_SECRET_KEY}"
}

resource "aws_instance" "example" {
  ami           = "ami-xczc"
  instance_type = "t2.micro"
  key_name      = "the_pair"
}
"""

# Prepare Terraform script as a file content for Terraform Cloud
def create_terraform_plan(workspace_id, terraform_script):
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/vnd.api+json"
    }

    # Create a new configuration version in the workspace
    data = {
        "data": {
            "type": "configuration-version",
            "attributes": {
                "terraform_version": "1.5.0",  # Specify Terraform version
            },
            "relationships": {
                "workspace": {
                    "data": {
                        "type": "workspaces",
                        "id": workspace_id  # Use the provided workspace ID
                    }
                }
            }
        }
    }

    # Upload the script to Terraform Cloud as a configuration version
    config_version_response = requests.post(
        f"{terraform_cloud_url}/configuration-versions",
        headers=headers,
        data=json.dumps(data)
    )

    print(f"Create configuration version response: {config_version_response.status_code}")
    print(f"Response data: {config_version_response.json()}")  # Debug response

    if config_version_response.status_code != 201:
        print(f"Error creating configuration version: {config_version_response.status_code}")
        return None

    config_version_data = config_version_response.json()
    config_version_id = config_version_data["data"]["id"]
    return config_version_id

# Create environment variables for AWS credentials
def set_environment_variables(workspace_id):
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/vnd.api+json"
    }

    # Set AWS Access Key
    aws_access_data = {
        "data": {
            "type": "vars",
            "attributes": {
                "key": "AWS_ACCESS_KEY",
                "value": user_aws_access_key,
                "category": "env",
                "hcl": False,
                "sensitive": True
            }
        }
    }

    # Set AWS Access Key
    access_response = requests.post(
        f"{terraform_cloud_url}/vars",
        headers=headers,
        data=json.dumps(aws_access_data)
    )
    print(f"Set AWS_ACCESS_KEY response: {access_response.status_code}")
    print(f"Response: {access_response.json()}")  # Debug response

    if access_response.status_code != 201:
        print("Error setting AWS_ACCESS_KEY:", access_response.status_code)
    
    # Set AWS Secret Key
    aws_secret_data = aws_access_data.copy()
    aws_secret_data["data"]["attributes"]["key"] = "AWS_SECRET_KEY"
    aws_secret_data["data"]["attributes"]["value"] = user_aws_secret_key
    
    secret_response = requests.post(
        f"{terraform_cloud_url}/vars",
        headers=headers,
        data=json.dumps(aws_secret_data)
    )
    print(f"Set AWS_SECRET_KEY response: {secret_response.status_code}")
    print(f"Response: {secret_response.json()}")  # Debug response

    if secret_response.status_code != 201:
        print("Error setting AWS_SECRET_KEY:", secret_response.status_code)

# Trigger the plan and apply run
def trigger_terraform_run(config_version_id, workspace_id):
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/vnd.api+json"
    }

    data = {
        "data": {
            "type": "runs",
            "attributes": {
                "message": "Provision infrastructure via Terraform Cloud",
                "is-destroy": False
            },
            "relationships": {
                "workspace": {
                    "data": {
                        "type": "workspaces",
                        "id": workspace_id  # Use the correct workspace ID
                    }
                },
                "configuration-version": {
                    "data": {
                        "type": "configuration-versions",
                        "id": config_version_id
                    }
                }
            }
        }
    }

    # Trigger run in Terraform Cloud
    run_response = requests.post(
        f"{terraform_cloud_url}/runs",
        headers=headers,
        data=json.dumps(data)
    )
    print(f"Trigger run response: {run_response.status_code}")
    print(f"Response data: {run_response.json()}")  # Debug response
    if run_response.status_code != 201:
        print(f"Error triggering run: {run_response.status_code}")
        return None

    run_data = run_response.json()
    return run_data["data"]["id"]

# Main execution flow
def run_terraform_provisioning():
    # Set the environment variables for AWS credentials
    set_environment_variables(workspace_id)

    # Create Terraform configuration version in Terraform Cloud
    config_version_id = create_terraform_plan(workspace_id, terraform_script)

    if not config_version_id:
        print("Failed to create configuration version.")
        return

    # Trigger the Terraform run to apply the changes
    run_id = trigger_terraform_run(config_version_id, workspace_id)

    if not run_id:
        print("Failed to trigger Terraform run.")
        return

    # Poll the run status (optional, but helpful to know when it's done)
    print(f"Terraform run started. Run ID: {run_id}")

# Execute the provisioning
# run_terraform_provisioning()
