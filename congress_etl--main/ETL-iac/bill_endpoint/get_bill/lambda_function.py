"""Lambda function that calls Bill API and writes json file to S3."""
import os
import json
import requests
import boto3

ssm = boto3.client('ssm', region_name='us-east-1')

API_KEY = ssm.get_parameter(Name= 'congress-apikey', WithDecryption=True)['Parameter']['Value']

CONGRESS_URL = 'https://api.congress.gov/v3'

BUCKET = os.environ['BUCKET']

def write_data(data,offset):
    """Write response data to a json file.

    Arguments:
    data: API Response data.
    offset: Offset parameter.
    """
    s3 = boto3.resource('s3')
    obj = s3.Object(BUCKET, f'bills/bill/bill_data_{offset}.json')

    obj.put(Body=(bytes(json.dumps(data).encode('UTF-8'))))


def get_bills(offset):
    """Get request response for bill endpoint.

    Arguments:
    offset: Offset parameter.
    """
    bills_data = []
    limit = 250

    params = {
        'api_key': API_KEY,
        'format': 'json',
        'limit': limit,
        'offset': offset,
        'sort': 'updateDate'
    }
    response = requests.get(CONGRESS_URL + '/bill', params=params)

    if response.status_code == 200:
        REMAINING_REQUESTS = response.headers['X-RateLimit-Remaining']
        print(f"REMAINING_REQUESTS: {REMAINING_REQUESTS}")
        json_data = response.json()
        bills = json_data.get('bills', [])
        pagintation_info = json_data.get('pagination', None)
        if pagintation_info:
            count = pagintation_info.get('count', 0)
            start = offset + limit
            offset_list = list(range(count))[start::limit]
            offset_dict = []
            for n in offset_list:
                offset_dict.append({"offset": n})

        for bill in bills:
             bills_data.append({
                    "congress": bill.get("congress"),
                    "number": bill.get("number"),
                    "type": bill.get("type")
                })

        return bills_data, offset_dict
    if response.status_code == 429:
        print(f"Status: {response.status_code}, Response: {response.json()}")
        raise Exception("Too many requests.")

    print(f"Status: {response.status_code}, Response: {response.json()}")
    raise Exception("Error getting API data.")


def lambda_handler(event,context):
    """"Main function. Gets bill data from API and writes response as json file to S3.
    
    Arguments:
    event: Offset parameter (optional)
    context: Not in use (mandatory for lambda function)
    """
    offset = event.get("offset", 0)

    bills_data, offset_dict = get_bills(offset)

    if bills_data:
        write_data(bills_data,offset)

    return offset_dict
