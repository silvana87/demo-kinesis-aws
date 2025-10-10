import json
import boto3
import os

kinesis_client = boto3.client('kinesis')
STREAM_NAME = os.environ.get('KINESIS_STREAM_NAME', 'f1-vote-stream')

def lambda_handler(event, context):
    try:
        # El voto vendrá en el cuerpo de la solicitud POST
        body = json.loads(event['body'])
        vote_option = body.get('vote')

        if not vote_option:
            return {
                'statusCode': 400,
                'headers': { # Asegúrate de tener headers también en el 400
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({'message': 'Missing vote option'})
            }

        # Envía el voto a Kinesis Data Stream
        response = kinesis_client.put_record(
            StreamName=STREAM_NAME,
            Data=json.dumps({'vote': vote_option}),
            PartitionKey='partition_key_1'
        )

        print(f"Vote '{vote_option}' sent to Kinesis. Response: {response}")

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # ¡Este es el encabezado clave!
                'Access-Control-Allow-Methods': 'POST,OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({'message': 'Voto recibido exitosamente'})
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST,OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({'message': f'Error processing vote: {str(e)}'})
        }