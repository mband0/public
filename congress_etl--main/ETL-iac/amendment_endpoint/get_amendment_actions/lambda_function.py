import json
import requests
from botocore.exceptions import ClientError
import boto3
import os
import psycopg2
import psycopg2.extras

ssm = boto3.client('ssm', region_name='us-east-1')

API_KEY = ssm.get_parameter(Name= 'congress-apikey', WithDecryption=True)['Parameter']['Value']

BUCKET = os.environ.get('BUCKET')

def get_secret(secret_name,region_name):
    """Retrieve values from secret in secret manager.
    
    Arguments:
    secret_name: Name of the secret.
    region_name: AWS Region.
    """
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + secret_name + " was not found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("The request was invalid due to:", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("The request had invalid params:", e)
        elif e.response['Error']['Code'] == 'DecryptionFailure':
            print("The requested secret can't be decrypted using the provided KMS key:", e)
        elif e.response['Error']['Code'] == 'InternalServiceError':
            print("An error occurred on service side:", e)
    else:
        # Secrets Manager decrypts the secret value using the associated KMS CMK
        # Depending on whether the secret was a string or binary, only one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            text_secret_data = get_secret_value_response['SecretString']
            return text_secret_data

        binary_secret_data = get_secret_value_response['SecretBinary']
        return binary_secret_data

def read_file(s3,bucket_name,key):
    """Reads json file from s3 bucket.

    Arguments:
    s3: s3 client.
    bucket_name: Name of the s3 bucket.
    key: file name.
    """
    obj = s3.Object(bucket_name, key)
    data = obj.get()['Body'].read().decode('utf-8')
    json_data = json.loads(data)

    return json_data

def json_to_csv(jdata,cl):
    """Transforms json data to a csv format.
    
    Arguments:
    jdata: data in json format.
    cl: list of columns.
    """
    cdata = []
    for jrow in jdata:
        row_data = []
        for col in cl:
            if col in jrow:
                if isinstance(jrow[col], (dict,list)):
                    value = json.dumps(jrow.get(col,None))
                else:
                    value = jrow.get(col,None)
            else:
                value = None
            row_data.append(value)
        cdata.append(tuple(row_data))
    return cdata

def write_data(host,username,password,dbname,table_name,columns,data):
    """Write response data to the db.

    Arguments:
    host: db host.
    username: db user.
    password: db password.
    dbname: db name.
    table_name: table name.
    columns: list of columns (ex: (col1,col2)).
    data: data to be inserted (ex: [(val1,val2),(val3,val4)]).
    """
    conn = psycopg2.connect(host=host, user=username, password=password, dbname=dbname)
    cursor = conn.cursor()
    insert_query = f'insert into {table_name} {columns} values %s'
    psycopg2.extras.execute_values (
        cursor, insert_query, data, template=None, page_size=100
    )
    conn.commit()
    cursor.close()
    conn.close()

class TooManyRequests(Exception):
    def __init__(self, message):
        self.name = 'TooManyRequests'
        self.message = message
        super().__init__(self.message)

def get_response(request_url):
    """Get request response.

    Arguments:
    request_url: CONGRESS_URL + URL_PARAMS + URL_ENDPOINT or next page url
    """
    next_url = None
    response = requests.get(request_url)

    if response.status_code == 200:
        REMAINING_REQUESTS = response.headers['X-RateLimit-Remaining']
        print(f"REMAINING_REQUESTS: {REMAINING_REQUESTS}")
        json_data = response.json()
        if "pagination" in json_data:
            next_url = json_data.get("next", None)
        return json_data, next_url
    
    elif response.status_code == 429:
        raise TooManyRequests('Too many requests to the API!')
    
    print(f"Status: {response.status_code}, Response: {response.json()}")
    raise Exception("Error getting API data.")

def lambda_handler(event,context):
    """"Main function. Gets member data from API and writes response as json file to S3.
    
    Arguments:
    event: Offset parameter (optional)
    context: Not in use (mandatory for lambda function)
    """
    CONGRESS_URL = 'https://api.congress.gov/v3'
    URL_ENDPOINT = '/actions'
    table_name = "amendment_actions"
    columns_list = ['actionCode','actionDate','recordedVotes','sourceSystem','text','type']
    columns = "(actioncode,actiondate,recordedvotes,sourcesystem,text,type)"
    limit=250
    
    read_key = event.get("Key", "No file provided")
    if read_key=="No file provided":
        return {"status": read_key}
    
    s3 = boto3.resource('s3')
    bucket_name = BUCKET
    
    total_data = []

    input_data = read_file(s3,bucket_name,read_key)
    for data in input_data:
        congress = data["congress"]
        amendment_type = data["type"].lower()
        amendment_number = data["number"]
        
        URL_PARAMS = '/amendment' + f'/{congress}' + f'/{amendment_type}' + f'/{amendment_number}'
        params = f"?api_key={API_KEY}&format=json&limit={limit}"
        request_url = CONGRESS_URL + URL_PARAMS + URL_ENDPOINT + params
        
        while request_url:
            response_data,request_url = get_response(request_url)
            if response_data:
                actions_data = response_data["actions"]
                for item in actions_data:
                    item.update( {"congress":congress})
                    item.update( {"amendmentType":amendment_type})
                    item.update( {"amendmentNumber":amendment_number})
                    item.update( {"endpoint_url":request_url})
                total_data += actions_data
                
    if total_data:
        secret_name = os.environ['SECRET']
        region_name = "us-east-1"

        secret = get_secret(secret_name,region_name)
        secret = json.loads(secret)
        host = os.environ['HOST']
        username = secret["username"]
        password = secret["password"]
        dbname = "postgres"
        csv_data = json_to_csv(total_data,columns_list)
        write_data(host,username,password,dbname,table_name,columns,csv_data)

    return {"status": 200,
            "Key": read_key}
    