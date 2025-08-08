# Defines the core conversational agent using Gemini, LangChain, and LangGraph.

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from salesforce_integration import SalesforceIntegration
from external_integrations import KnowledgeBaseIntegration

# --- Tool Definitions ---

# Initialize integrations which will be used by our tools
sf_integration = SalesforceIntegration()
kb_integration = KnowledgeBaseIntegration()

@tool
def get_salesforce_case_details(case_number: str) -> dict:
    """
    Retrieves details for a specific case from Salesforce using its case number.
    Use this tool when a user asks for the status, priority, subject, or description of a specific case.
    """
    print(f"--- Calling Salesforce Tool for case: {case_number} ---")
    return sf_integration.get_case_details(case_number)

@tool
def search_knowledge_base(search_term: str) -> str:
    """
    Searches the knowledge base for articles related to a given search term.
    Use this for general questions, how-to guides, or troubleshooting information.
    """
    print(f"--- Calling Knowledge Base Tool for term: {search_term} ---")
    return kb_integration.search_articles(search_term)

@tool
def log_and_assign_task(subject: str, related_to_id: str, description: str, assignee_id: str = None) -> dict:
    """
    Logs a customer interaction or assigns a task in Salesforce.
    Requires a subject, the ID of the related record (like a Contact or Case ID), and a description.
    Optionally, you can assign it to another user by providing their Salesforce user ID in 'assignee_id'.
    """
    print(f"--- Calling Salesforce Tool to log/assign task: {subject} ---")
    return sf_integration.log_activity_or_task(subject, related_to_id, description, assignee_id)

@tool
def update_external_inventory_db(product_sku: str, quantity_change: int) -> dict:
    """
    Updates the inventory count for a product in the external inventory database.
    Use a positive number for quantity_change to add stock, and a negative number to remove stock.
    """
    print(f"--- Calling External DB Tool to update inventory for: {product_sku} ---")
    return kb_integration.update_inventory(product_sku, quantity_change)

@tool
def commit_code_changes(commit_message: str, file_path: str) -> str:
    """
    Commits a file to the Git repository with a specific commit message.
    This is a sensitive tool. Use only when explicitly told to commit a configuration change or code fix.
    Requires a detailed commit_message and the relative file_path to be committed.
    For safety, this tool only simulates the git commands.
    """
    print(f"--- Calling Git Tool to commit file: {file_path} ---")
    git_add_command = f"git add {file_path}"
    git_commit_command = f"git commit -m '{commit_message}'"
    
    # In a real environment, you would use subprocess.run() to execute these.
    # For this example, we will print the commands to avoid making actual commits.
    simulated_output = (
        f"Simulated Execution:\n"
        f"Would run: {git_add_command}\n"
        f"Would run: {git_commit_command}\n"
        f"Successfully simulated commit for file '{file_path}'."
    )
    return simulated_output

@tool
def update_marketing_platform_subscriber(email: str, new_data: dict) -> dict:
    """
    Updates a subscriber's profile in the company's marketing automation platform (e.g., Marketo, HubSpot).
    Use this to sync changes to a customer's contact preferences, name, or email address.
    Requires the user's email and a dictionary of the data to update.
    """
    print(f"--- Calling Marketing Platform Tool to update subscriber: {email} ---")
    return kb_integration.update_marketing_subscriber(email, new_data)

@tool
def update_erp_customer_record(customer_id: str, new_financial_data: dict) -> dict:
    """
    Updates a customer's record in the ERP system (e.g., SAP, NetSuite).
    Use this to change critical financial information like billing addresses or payment terms.
    Requires the ERP customer_id and a dictionary of the financial data to update.
    """
    print(f"--- Calling ERP Tool to update customer: {customer_id} ---")
    return kb_integration.update_erp_record(customer_id, new_financial_data)

@tool
def sync_contact_to_cdp(contact_id: str, contact_data: dict) -> dict:
    """
    Pushes a full, updated contact profile to the central Customer Data Platform (CDP).
    This tool should be used after a contact record is updated to ensure the unified customer view is current.
    Requires the Salesforce contact_id and a dictionary of the complete contact data.
    """
    print(f"--- Calling CDP Tool to sync contact: {contact_id} ---")
    return kb_integration.sync_to_cdp(contact_id, contact_data)



# --- Agent Definition ---

def create_agent_executor():
    """
    Creates and compiles the LangGraph agent.
    """
    # 1. Define the LLM
    # Using Gemini 1.5 Flash, a fast and capable model that's also conviently available under the Free Tier.
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")



    # 2. Define the tools
    tools = [
        get_salesforce_case_details,
        search_knowledge_base,
        create_new_lead,
        update_customer_360_record,
        log_and_assign_task,
        update_external_inventory_db,
        commit_code_changes
        update_marketing_platform_subscriber,
        update_erp_customer_record,
        sync_contact_to_cdp
    ]

    # 3. Define the memory for conversational history
    memory = MemorySaver()

    # 4. Create the ReAct Agent
    # ReAct (Reasoning and Acting) is a powerful agent type that can decide when to use tools.
    # LangGraph's `create_react_agent` simplifies this process.
    agent_executor = create_react_agent(llm, tools, checkpointer=memory)
    
    print("LangGraph agent created successfully.")
    return agent_executor
