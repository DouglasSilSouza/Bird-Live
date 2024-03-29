import boto3
import json
from botocore.exceptions import ClientError
import dotenv
import os

class GetSecret:
    @staticmethod
    def get_secret():
        secret_name = "bird-live"
        region_name = "us-east-2"

        dotenv.load_dotenv()
        # Create a Secrets Manager client
        session = boto3.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name,
            aws_access_key_id=os.getenv("aws_access_key_id"),
            aws_secret_access_key=os.getenv("aws_secret_access_key"),
        )

        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            # For a list of exceptions thrown, see
            # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
            raise e

        secret = get_secret_value_response['SecretString']
        return json.loads(secret)