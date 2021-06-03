import sys
import requests
import os
import gspread
import pandas as pd


# Login and get a access token
def login(base_url, username, password):
    """
    Arguments:
            base_url {string} -- authrization base url(currently same with api)
            email {[type]} -- your email
            password {[type]} -- your password

    Returns:
            json -- token entity include expiration and refresh token info like:
                    {
                            "access_token": "ABCD1234",      # Access permission
                            "token_type": "bearer",		     # Token type
                            "expires_in": 86399,		     # Access Token Expiration time (in seconds)
                            "refresh_token": "refresh_token" # To refresh Access Token
                    }
    """

    content = 'username={0}&password={1}&grant_type=password'.format(
        username, password)
    token_entity = requests.post(base_url + 'token', data=content).json()

    if 'access_token' in token_entity:
        return token_entity
    else:
        os._exit(-2)


# Get data by offset
def get_data_by_offset(base_url, token, task_id, offset=0, size=10):
    """offset, size and task ID are all required in the request.
    Offset should default to 0, and size∈[1,1000] for making the initial request.
    The offset returned (could be any value greater than 0) should be used for making the next request.
    
    Arguments:
            base_url {string} -- base url of the api
            token {string} -- token string from a valid token entity
            task_id {string} -- task id of a task from our platform

    Keyword Arguments:
            offset {int} -- an offset from last data request, should remains 0 if is the first request (default: {0})
            size {int} -- data row size for the request (default: {10})

    Returns:
            json -- task dataList and relevant information:
                     {
                            "data": {
                            "offset": 4,
                            "total": 100000,
                            "restTotal": 99996,
                            "dataList": [
                            {
                                    "state": "Texas",
                                    "city": "Plano"
                            },
                            {
                                    "state": "Texas",
                                    "city": "Houston"
                            },
                            ...
                            ]
                            },
                            "error": "success",
                            "error_Description": "Action Success"
                    }
    """

    url = 'api/allData/getDataOfTaskByOffset?taskId=%s&offset=%s&size=%s' % (
        task_id, offset, size)
    task_data_result = requests.get(base_url + url,
                                    headers={
                                        'Authorization': 'bearer ' + token
                                    }).json()

    return task_data_result

# Running the countries task
def run_countries_task(base_url, token_entity):
    """

    Arguments:
            base_url {string} -- API base url
            token_entity {json} -- token entity after logged in
    """

    # Retrieving an access token after the login
    token = token_entity['access_token']

    # Input Your Task id here
    task_id = "TaskID"

    # Running the task and retrieving data
    offset = 0
    data = get_data_by_offset(base_url, token, task_id, offset, size=1000)
    
    # Retrieving the extracted data in JSON format
    json_extracted_data = data['data']['dataList']

    # Get data when it has restTotal
    while data['data']['restTotal'] != 0:
        offset = data['data']['offset']
        data = get_data_by_offset(base_url, token, task_id, offset, size=1000)
        json_extracted_data = json_extracted_data + data['data']['dataList']
    else:
    # Converting the JSON string to CSV
        df = pd.DataFrame(json_extracted_data)
        csv_extracted_data = df.to_csv(header=True, index=False)

    # Check how to get 'credentials':
    # https://gspread.readthedocs.io/en/latest/oauth2.html#for-bots-using-service-account
    # And input your credentials below
    credentials = 

    # Input your Spread sheet ID below
    gc = gspread.service_account_from_dict(credentials)
    spreadsheet_id = "spreadsheet_id"

    # Importing CSV data into your Google Sheet document identified by spreadsheet_id
    gc.import_csv(spreadsheet_id, csv_extracted_data.encode('utf-8'))


if __name__ == '__main__':  
    # The username you used to subscribe to Octoparse
    username = "username"
    # Input your password here
    password = "password"

    octoparse_base_url = 'http://advancedapi.octoparse.com/'
    '''
    For Standard Plan, please use 'http://dataapi.octoparse.com/'.
    For Professional or Enterprise Plan, please use 'http://advancedapi.octoparse.com/'.
    '''
    token_entity = login(octoparse_base_url, username, password)

    run_countries_task(octoparse_base_url, token_entity)
