import json
import requests
import boto3
import os

ssm = boto3.client('ssm', region_name='us-east-1')

API_KEY = ssm.get_parameter(Name= 'congress-apikey', WithDecryption=True)['Parameter']['Value']

CONGRESS_URL = 'https://api.congress.gov/v3'

BUCKET = os.environ.get('BUCKET')

def write_data(data,offset):
    s3 = boto3.resource('s3')
    bucket = BUCKET
    key = f'amendments/amendment/amendment_data_{offset}.json'
    obj = s3.Object(bucket, key)

    obj.put(Body=(bytes(json.dumps(data).encode('UTF-8'))))

class TooManyRequests(Exception):
    def __init__(self, message):
        self.name = 'TooManyRequests'
        self.message = message
        super().__init__(self.message)

def get_amendments(offset):
    amendments_data = []
    limit = 250

    params = {
        'api_key': API_KEY,
        'format': 'json',
        'limit': limit,
        'offset': offset,
        'sort': 'updateDate'
    }
    response = requests.get(CONGRESS_URL + '/amendment', params=params)

    if response.status_code == 200:
        REMAINING_REQUESTS = response.headers['X-RateLimit-Remaining']
        print(f"REMAINING_REQUESTS: {REMAINING_REQUESTS}")
        json_data = response.json()
        amendments = json_data.get('amendments', [])
        pagintation_info = json_data.get('pagination', None)
        start = offset + limit
        if pagintation_info:
            count = pagintation_info.get('count', 0)
            offset_list = list(range(count))[start::limit]
            offset_dict_list = []
            for n in offset_list:
                offset_dict_list.append({"offset": n})

        for amendment in amendments:
             amendments_data.append({
                    "congress": amendment.get("congress"),
                    "number": amendment.get("number"),
                    "type": amendment.get("type")
                })

        return amendments_data, offset_list, offset_dict_list
    
    elif response.status_code == 429:
        raise TooManyRequests('Too many requests to the API!')

    print(f"Status: {response.status_code}, Response: {response.json()}")
    raise Exception("Error getting API data.")

def lambda_handler(event,context):
    offset = event.get("offset", 0)

    amendments_data, offset_list, offset_dict_list = get_amendments(offset)

    if amendments_data:
        write_data(amendments_data,offset)

    return offset_dict_list
