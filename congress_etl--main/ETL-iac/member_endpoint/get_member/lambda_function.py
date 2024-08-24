import json
import requests
import boto3
from datetime import datetime,timedelta

ssm = boto3.client('ssm', region_name='us-east-1')

API_KEY = ssm.get_parameter(Name= 'congress-apikey', WithDecryption=True)['Parameter']['Value']

CONGRESS_URL = 'https://api.congress.gov/v3'

state_code_dict = {
"Alabama": "AL",
"Alaska": "AK",
"American Samoa": "AS",
"Arkansas": "AR",
"Arizona": "AZ",
"California": "CA",
"Colorado": "CO",
"Connecticut":"CT",
"Delaware": "DE",
"District of Columbia": "DC",
"Florida": "FL",
"Georgia": "GA",
"Guam": "GU",
"Hawaii": "HI",
"Idaho": "ID",
"Illinois": "IL",
"Indiana": "IN",
"Iowa": "IA",
"Kansas": "KS",
"Kentucky": "KY",
"Louisiana": "LA",
"Maine":  "ME",
"Maryland": "MD",
"Massachusetts": "MA",
"Michigan": "MI",
"Minnesota": "MN",
"Mississippi": "MS",
"Missouri": "MO",
"Montana": "MT",
"Nebraska": "NE",
"Nevada": "NV",
"New Hampshire": "NH",
"New Jersey": "NJ",
"New Mexico": "NM",
"New York": "NY",
"North Carolina": "NC",
"North Dakota": "ND",
"Northern Mariana Islands": "MP",
"Ohio": "OH",
"Oklahoma": "OK",
"Oregon": "OR",
"Pennsylvania": "PA",
"Puerto Rico": "PR",
"Rhode Island": "RI",
"South Carolina": "SC",
"South Dakota": "SD",
"Tennessee": "TN",
"Texas": "TX",
"Utah": "UT",
"Vermont": "VT",
"Virginia": "VA",
"Washington": "WA",
"West Virginia":"WV",
"Wisconsin": "WI",
"Wyoming": "WY",
"Virgin Islands": "VI"
}

class TooManyRequests(Exception):
    def __init__(self, message):
        self.name = 'TooManyRequests'
        self.message = message
        super().__init__(self.message)

def write_data(data,offset):
    s3 = boto3.resource('s3')
    obj = s3.Object('congress-api-data', f'members/member/member_data_{offset}.json')

    obj.put(Body=(bytes(json.dumps(data).encode('UTF-8'))))


def get_members(offset):
    members_data = []
    limit = 50
    
    params = {
        'api_key': API_KEY,
        'format': 'json',
        'limit': limit,
        'offset': offset,
        'sort': 'updateDate'
    }
    response = requests.get(CONGRESS_URL + '/member', params=params)
    
    if response.status_code == 200:
        REMAINING_REQUESTS = response.headers['X-RateLimit-Remaining']
        print(f"REMAINING_REQUESTS: {REMAINING_REQUESTS}")
        json_data = response.json()
        members = json_data.get('members', [])
        pagintation_info = json_data.get('pagination', None)
        start = offset + limit
        if pagintation_info:
            count = pagintation_info.get('count', 0)
            offset_list = list(range(count))[start::limit]
            offset_dict_list = []
            for n in offset_list:
                offset_dict_list.append({"offset": n})

        for member in members:
             members_data.append({
                    "id": member.get("bioguideId"),
                    "district": member.get("district"),
                    "state_code": state_code_dict[member.get("state")]
                })

        return members_data, offset_list, offset_dict_list

    elif response.status_code == 429:
        raise TooManyRequests('Too many requests to the API!')
    
    print(f"Status: {response.status_code}, Response: {response.json()}")
    raise Exception("Error getting API data.")

def lambda_handler(event,context):
    offset = event.get("offset", 0)

    members_data, offset_list, offset_dict_list = get_members(offset)

    if members_data:
        write_data(members_data,offset)

    return offset_dict_list

