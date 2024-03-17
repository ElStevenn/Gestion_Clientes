# API TO Customer and lead management & Microservice

### How it works
 - This API can handle leads, share them, and collect data. It's focused on serving call centers that want to manage all their leads
 

![main image](https://paumateu.com/static/pictures/api_cost_lead.png)

## POST /v2/enviar_cliente (Endpoint for Sending Client Data)
 - **Description**: This endpoint allows you to send client data to the API.
 - **Authentication**: Requires the `api-key` in the request header for authentication.
 - **Request Body**: Expects a JSON request body with client data following the `ClientSchema`.
 - **Background Tasks**:sdsd
   - Sends an email to the client.
   - Appends data to a Google spreadsheet.

## GET /responder_cliente/ (Client Response Page)
 - **Description**: This endpoint provides an HTML response page for responding to client inquiries. It's intended to be opened in a separate tab.

## GET /get_json_dataset (Retrieve JSON Dataset)
 - **Description**: This endpoint is used to retrieve the dataset in JSON format.
 - **Authentication**: Requires the `api-key` in the request header for authentication.

## GET /admin_response (Admin Response Page)
 - **Description**: This endpoint provides an HTML page for administrators to respond to client inquiries. It includes fields for various responses.

## GET /descargar_tabla/{token_beaber} (Download Dataset Table)
 - **Description**: This endpoint is used to download the dataset table in XLSX format.
 - **Authentication**: Requires the `token_beaber` parameter for authentication.

## PUT /update_schema_client (Update Schema Definition)
 - **Description**: This endpoint updates the schema definition from a column given.
 - **Authentication**: Requires the `api-key` in the request header for authentication.

## POST /make_backup (Create Backup)
 - **Description**: This endpoint creates a backup of the dataset and sends it to AWS S3.
 - **Authentication**: Requires the `api-key` in the request header for authentication.

## POST /api_set_conf/{token_beaber} (Set API Configuration)
 - **Description**: This internal endpoint is used to apply API configuration changes.
 - **Authentication**: Requires the `api-key` in the request header for authentication.

## WebSocket /ws_tabla (WebSocket for Data Table)
 - **Description**: This WebSocket allows real-time updates of data for the table.

## GET /code (OAuth Authentication - Authorization Code Flow)
 - **Description**: This endpoint handles the OAuth2 authorization code flow for API authentication. It's used to obtain an authorization code for further authentication.

## POST /token (Create User Token)
 - **Description**: This endpoint is used to create a secure user token for authentication.
 - **Request Body**: Expects the user's credentials in the request body using OAuth2 password request form.



## GET /code (OAuth Authentication - Authorization Code Flow)
 Description: This endpoint handles the OAuth2 authorization code flow for API authentication. It's used to obtain an authorization code for further authentication.

## POST /token (Create User Token)
 Description: This endpoint is used to create a secure user token for authentication.
 Request Body: Expects the user's credentials in the request body using OAuth2 password request form.

 
