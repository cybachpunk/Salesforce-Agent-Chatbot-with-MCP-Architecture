# Salesforce Agent Chatbot with MCP Architecture

## Overview

This project provides a sophisticated chatbot for Salesforce call center agents utilizing MCP architecture. It leverages Gemini Flash model as its core reasoning engine, with LangChain for tool creation and LangGraph for orchestrating complex, stateful conversations.

This architecture moves beyond simple intent detection to a powerful agent that can understand natural language, maintain conversational history, and decide which tools (like Salesforce or a knowledge base) to use to answer an agent's query.

MCP is a rapidly growing domain and its likely that many applications moving forward will incorporate LLM brains to handle anything from plaintext queries to massive changes across multiple organizational applications and databases, provided they are given the tools and access to do so.

## Architecture

1.  **Chatbot App (`chatbot_app.py`)**: A lightweight client that sends user queries to the MCP server. It hosts simple logic for interaction passed off to the MCP server for processing.
2.  **MCP Server (`mcp_server.py`)**: Hosts the conversational agent. Its role is to receive requests, pass them to the agent, and stream the response back to the client.
3.  **LangGraph Agent (`langgraph_agent.py`)**: The brain of the operation. It uses Gemini to understand the user, decide on actions, and call the appropriate tools.
4.  **Tools (`salesforce_integration.py`, `external_integrations.py`)**: Functions that the LangGraph agent can call, typically to other integrations external to the immediate build. More importantly, their development cycles sit independent of this architecture, allowing the organization to stay agile in their prioritization of modernization.

### Data Flow

The design for this build 
Agent UI --> Chatbot App --> MCP Server --> LangGraph Agent --> Gemini LLM --> Tool Execution
(manages state)      (decides action)  (e.g., Salesforce API Call)


## Features

The agent has access to a variety of tools that allow it to interact with Salesforce and other external systems. The Gemini model decides which tool to use based on the user's request.


| Tool                                     | Description                                                                                             |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `get_salesforce_case_details`            | Retrieves details for a specific case from Salesforce using its case number.                            |
| `search_knowledge_base`                  | Searches the internal knowledge base for articles related to a given search term.                       |
| `upsert_lead_record`                     | Creates a new lead in Salesforce or updates an existing one if a lead with that email already exists.   |
| `upsert_customer_360_record`             | Creates or updates a customer's primary contact record in Salesforce based on their email.              |
| `log_and_assign_task`                    | Logs a customer interaction or assigns a follow-up task to a user in Salesforce.                        |
| `update_external_inventory_db`           | Updates the stock count for a product in the external inventory database.                               |
| `update_marketing_platform_subscriber`   | Syncs changes to a customer's profile in the marketing automation platform (e.g., Marketo, HubSpot).    |
| `update_erp_customer_record`             | Updates a customer's financial record (e.g., billing address) in the ERP system (e.g., SAP, NetSuite). |
| `sync_contact_to_cdp`                    | Pushes the complete, updated contact profile to the central Customer Data Platform (CDP).               |
| `commit_code_changes`                    | (For Admins/Developers) Commits a file to a Git repository to manage configurations as code, useful for custom workflows            |


## Prerequisites

* Python 3.8+
* A Salesforce Developer Org or Sandbox
* A Google AI API Key for Gemini
* Some other external dependencies for you to play with. In this example, we're simulating external Marketing, ERP, and Data Platform systems

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    * Create a `.env` file in the root of the project.
    * Add your credentials to the `.env` file:
        ```
        # Google API Key for Gemini
        GOOGLE_API_KEY='your_google_ai_api_key'

        # Salesforce Credentials
        SALESFORCE_USERNAME='your_salesforce_username'
        SALESFORCE_PASSWORD='your_salesforce_password'
        SALESFORCE_SECURITY_TOKEN='your_salesforce_security_token'
        ```

## Running the Application

1.  **Start the MCP Server:**
    ```bash
    python mcp_server.py
    ```
    The server will be running at `http://1227.0.0.1:5001`.

2.  **Run the Chatbot App:**
    * Open a new terminal window and activate the virtual environment.
    * Run the chatbot client:
        ```bash
        python chatbot_app.py
        ```

3.  **Interact with the chatbot:**
    * The chatbot now understands natural language. Try queries like:
        * **Querying Information:**
            * "What's the status of case 00001027?"
            * "How do I handle a product return?"
            * "Thanks, what was the priority on that case again?" (demonstrates memory)
        * **Creating & Updating Records:**
            * "Please create a new lead for Global Tech, contact is Sarah Smith, email sarah@globaltech.com, phone 555-111-2222."
            * "Update the phone number for the contact with email 'jane.doe.new@example.com' to 555-999-8888."
        * **Multi-step & Cross-System Actions:**
            * "Log a call for contact ID 0033i000006F7G8. The notes are 'Customer called to confirm shipping address.' and assign a follow-up task to user 0053i000002B3C4."
            * "We just sold one unit of SKU-67890-B. Please log the sale and update the inventory."
            * "The customer at jane.doe.new@example.com has a new billing address: 456 Market St, San Francisco, CA 94105. Please update their record everywhere."
        * **For Admins/Developers:**
            * "Commit the file 'flows/New_User_Onboarding.flow-meta.xml' with the message 'Feat: Add welcome email step to new user flow'."
