# congress-api-ETL

Pre-deploy:

 - Create S3 bucket.
 - Get (or create) secret in secrets manager with username and password to access the db.
 - Create SSM parameter and KMS key to save the apikey.

Deploy:

 - Deploy the template files for the Parent endpoints. template.yaml file.

 `sam build`

 `sam deploy --guided`

 - Deploy Lambda function rename_input_file that's common for all ETLs. Get function name and repace in templates where is needed (RenameInputFileFunctionArn and FunctionName: "vt-congress-rename_input_file-test")

 `sam build`

 `sam deploy --guided`

 - Deploy the template files for the child enpoints. template_<endpoint>_derivates.yaml

 `sam build --config-file template_<endpoint>_derivates.yaml`

 `sam deploy --guided`
