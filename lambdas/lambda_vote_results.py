import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        # Escanea toda la tabla para obtener todos los conteos de votos
        response = table.scan()
        items = response['Items']

        # Convierte los números decimales de DynamoDB a enteros para JSON
        for item in items:
            item['votes'] = int(item['votes'])

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(items)
        }
    except Exception as e:
        print(f"Error al obtener los resultados: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({'message': f"Error: {str(e)}"})
        }