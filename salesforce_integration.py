# Handles all communication with the Salesforce API including upsert logic

from simple_salesforce import Salesforce
import os

class SalesforceIntegration:
    def __init__(self):
        try:
            self.sf = Salesforce(
                username=os.getenv("SALESFORCE_USERNAME"),
                password=os.getenv("SALESFORCE_PASSWORD"),
                security_token=os.getenv("SALESFORCE_SECURITY_TOKEN") # Rotate every 30-90 days :)
            )
            print("Successfully connected to Salesforce.")
        except Exception as e:
            print(f"Failed to connect to Salesforce: {e}")
            self.sf = None

    def get_case_details(self, case_number: str):
        """
        Retrieves details for a specific case from Salesforce.
        """
        if not self.sf:
            return {"error": "Salesforce connection not available."}
            
        try:
            soql = f"SELECT Id, CaseNumber, Subject, Status, Priority, Description FROM Case WHERE CaseNumber = '{case_number}'"
            result = self.sf.query(soql)
            if result['totalSize'] > 0:
                record = result['records'][0]
                record.pop('attributes', None)
                return record
            return {"message": f"Case {case_number} not found."}
        except Exception as e:
            print(f"Error querying Salesforce: {e}")
            return {"error": f"An error occurred while querying Salesforce: {e}"}

    def upsert_lead(self, email: str, lead_data: dict):
        """
        Creates or updates a Lead record based on email address.
        This is a simplified upsert. A production implementation would use a dedicated External ID field.
        """
        if not self.sf:
            return {"error": "Salesforce connection not available."}
        try:
            # 1. Check if a lead with this email already exists
            existing_lead = self.sf.query(f"SELECT Id FROM Lead WHERE Email = '{email}'")
            
            if existing_lead['totalSize'] > 0:
                # 2. If it exists, update it
                lead_id = existing_lead['records'][0]['Id']
                self.sf.Lead.update(lead_id, lead_data)
                return {"status": "updated", "lead_id": lead_id}
            else:
                # 3. If it does not exist, create it
                result = self.sf.Lead.create(lead_data)
                if result.get('success'):
                    return {"status": "created", "lead_id": result.get('id')}
                else:
                    return {"status": "error", "errors": result.get('errors')}
        except Exception as e:
            return {"error": f"An error occurred during lead upsert: {e}"}

    def upsert_contact(self, email: str, contact_data: dict):
        """
        Creates or updates a Contact record based on email address.
        This is a simplified upsert. A production implementation would use a dedicated External ID field.
        """
        if not self.sf:
            return {"error": "Salesforce connection not available."}
        try:
            # 1. Check if a contact with this email already exists
            existing_contact = self.sf.query(f"SELECT Id FROM Contact WHERE Email = '{email}'")

            if 'LastName' not in contact_data:
                return {"error": "LastName is required to create or update a contact."}

            if existing_contact['totalSize'] > 0:
                # 2. If it exists, update it
                contact_id = existing_contact['records'][0]['Id']
                self.sf.Contact.update(contact_id, contact_data)
                return {"status": "updated", "contact_id": contact_id}
            else:
                # 3. If it does not exist, create it
                result = self.sf.Contact.create(contact_data)
                if result.get('success'):
                    return {"status": "created", "contact_id": result.get('id')}
                else:
                    return {"status": "error", "errors": result.get('errors')}
        except Exception as e:
            return {"error": f"An error occurred during contact upsert: {e}"}


    def log_activity_or_task(self, subject: str, who_id: str, description: str, owner_id: str = None):
        """
        Creates a new Task record in Salesforce, linking it to a Contact/Lead (WhoId).
        Can be assigned to a specific user via OwnerId.
        """
        if not self.sf:
            return {"error": "Salesforce connection not available."}
        try:
            task_data = {
                'Subject': subject,
                'WhoId': who_id, # Must be a Contact or Lead ID
                'Description': description,
                'Status': 'Not Started',
                'Priority': 'Normal'
            }
            if owner_id:
                task_data['OwnerId'] = owner_id

            result = self.sf.Task.create(task_data)
            if result.get('success'):
                return {"status": "success", "task_id": result.get('id')}
            else:
                return {"status": "error", "errors": result.get('errors')}
        except Exception as e:
            return {"error": f"An error occurred while creating a task: {e}"}