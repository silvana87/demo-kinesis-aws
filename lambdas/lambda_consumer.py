import json
import boto3
import base64
import os

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'f1-vote-results') 
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    for record in event['Records']:
        payload = base64.b64decode(record['kinesis']['data']).decode('utf-8')
        vote_data = json.loads(payload)
        vote_option = vote_data.get('vote')

        if vote_option:
            print(f"Processing vote for: {vote_option}")
            table.update_item(
                Key={'option_id': vote_option},   # debe coincidir con tu Partition Key
                UpdateExpression="ADD votes :inc",
                ExpressionAttributeValues={':inc': 1},
                ReturnValues="UPDATED_NEW"
            )
        else:
            print("No vote option found in record.")

    return {'statusCode': 200, 'body': 'Successfully processed records'}