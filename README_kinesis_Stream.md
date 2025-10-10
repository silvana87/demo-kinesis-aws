# ⚡ Implementar un Stream en Amazon Kinesis

Este tutorial describe el paso a paso para crear y configurar un **Kinesis Data Stream** en AWS, y cómo integrarlo con **AWS Lambda** para procesar datos en tiempo real.

---

## 1️⃣ ¿Qué es Amazon Kinesis Data Streams?
Amazon Kinesis Data Streams (KDS) es un servicio que permite **capturar, procesar y almacenar datos en tiempo real**.  
Ideal para casos como:
- Analítica en tiempo real (dashboards, métricas).
- Procesamiento de logs y eventos.
- Streaming de IoT, clickstreams o votaciones en línea.

---

## 2️⃣ Crear un Stream en Kinesis
1. Ve a la consola de **Amazon Kinesis** → [https://console.aws.amazon.com/kinesis](https://console.aws.amazon.com/kinesis).
2. Selecciona **Create data stream**.
3. Configura:
   - **Name**: `f1-vote-stream` (ejemplo).
   - **Capacity mode**: elige entre:
     - **On-demand** (AWS ajusta automáticamente la capacidad, recomendado para pruebas y carga variable).
     - **Provisioned** (definir manualmente número de shards).
   - **Shards**: si eliges *Provisioned*, define cuántos shards (1 shard = hasta 1 MB/s de escritura y 2 MB/s de lectura).
4. Haz clic en **Create data stream**.

✅ Con esto tienes tu stream creado y listo para recibir eventos.

---

## 3️⃣ Enviar datos al Stream desde Lambda
# Lambda Productor para enviar votos a Kinesis

Este Lambda actúa como **productor**, recibiendo los votos desde el API Gateway y enviándolos al **Kinesis Data Stream**.  
A continuación, explicamos la configuración clave, incluyendo **variables de entorno** y **CORS**.

```python
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
```

### 🔑 Consideraciones
- **PartitionKey** se usa para distribuir los datos entre shards.
- **Data** debe estar en formato JSON o string serializado.
- La Lambda necesita permisos de escritura en Kinesis (`kinesis:PutRecord`).

---

## 4️⃣ Crear un consumidor con Lambda
Configura otra Lambda que procese los datos del stream en tiempo real.

Ejemplo en Python:

```python
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
            table.update_item(
                Key={'option_id': vote_option},
                UpdateExpression='ADD votes :inc',
                ExpressionAttributeValues={':inc': 1}
            )

    return 'Processed records.'
```

### 🔑 Consideraciones
- AWS Lambda recibe los eventos de Kinesis en **batches**.
- Los datos en `record['kinesis']['data']` llegan **Base64 encoded**, por eso hay que decodificarlos.
- La Lambda necesita permisos de lectura en Kinesis (`kinesis:GetRecords`) y escritura en DynamoDB.

---

## 5️⃣ Conectar Kinesis con Lambda (Trigger)
1. Abre la consola de **AWS Lambda**.
2. Selecciona tu función `f1-vote-consumer`.
3. En la sección **Triggers**, añade **Kinesis**.
4. Configura:
   - **Kinesis stream**: selecciona `f1-vote-stream`.
   - **Batch size**: define cuántos registros procesar en cada ejecución (ej. 100).
   - **Starting position**: `LATEST` (procesar solo nuevos eventos) o `TRIM_HORIZON` (desde el inicio).
5. Guarda los cambios.

Ahora tu Lambda se invoca automáticamente cada vez que haya nuevos registros en el stream.

---

## 6️⃣ Validar con CloudWatch Logs
- Cada Lambda escribe sus logs en **CloudWatch** bajo `/aws/lambda/<function_name>`.
- Si algo no funciona, revisa errores de permisos o de decodificación.

---

## 7️⃣ Buenas prácticas
- **On-demand vs Provisioned**: usa *On-demand* para pruebas, *Provisioned* para cargas estables y de alto volumen.
- **Dead Letter Queue (DLQ)**: configura una cola SQS o SNS en la Lambda para manejar errores.
- **Retries**: Lambda reintenta automáticamente si falla al procesar un batch.
- **Shards**: escala horizontalmente agregando más shards si necesitas más throughput.

---

## ✅ Resultado
Con esta arquitectura:
- Los votos (eventos) llegan a **API Gateway** → **Lambda**.
- La Lambda los envía a **Kinesis Stream**.
- El consumidor (otra Lambda) los procesa en tiempo real y los almacena en **DynamoDB**.

Esto permite construir **dashboards en vivo** y aprender los fundamentos de **procesamiento de datos en tiempo real**.

🎉 ¡Ya tienes tu flujo con Kinesis funcionando!
