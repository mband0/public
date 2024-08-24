"""Lambda function that renames a file."""
import os
import json
import boto3

BUCKET = os.environ['BUCKET']

def lambda_handler(event,context):
    """"Main function. Makes a copy of the input file and deletes the original.
    
    Arguments:
    event: file name with input data.
    context: Not in use (mandatory for lambda function)
    """
    client = boto3.client('s3')
    bucket_name = 'congress-api-data'
    read_key = event.get("Key", "No file provided")
    if read_key=="No file provided":
        return {"status": 404,
            "file": read_key}

    output_file = 'processed/' + read_key

    copy_response = client.copy_object(
                                Bucket=bucket_name,
                                CopySource=f"{bucket_name}/{read_key}",
                                Key=output_file,
                            )

    print(copy_response)

    if "ETag" in copy_response["CopyObjectResult"]:

        delete_response = client.delete_object(
                                  Bucket=bucket_name,
                                  Key=read_key,
                              )

        print(delete_response)

        return json.dumps({"status": 200,
              "copy result":json.dumps(copy_response, default=str),
              "delete result":json.dumps(delete_response)})
   
    return json.dumps({"status": 400,
            "copy result":copy_response}, default=str)
