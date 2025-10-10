# Lambda Productor para enviar votos a Kinesis

Este Lambda actúa como **productor**, recibiendo los votos desde el API Gateway y enviándolos al **Kinesis Data Stream**.  
A continuación, explicamos la configuración clave, incluyendo **variables de entorno** y **CORS**.

---

## Código del Lambda Productor

```python
import json
import boto3
import os

kinesis_client = boto3.client('kinesis')
STREAM_NAME = os.environ.get('KINESIS_STREAM_NAME')

def lambda_handler(event, context):
    try:
        # El voto vendrá en el cuerpo de la solicitud POST
        body = json.loads(event['body'])
        vote_option = body.get('vote')

        if not vote_option:
            return {
                'statusCode': 400,
                'headers': { # Headers CORS también en errores
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

---

## Configuración de Variables de Entorno

Para evitar hardcodear el nombre del stream dentro del código, se utiliza una **variable de entorno**:

- **KINESIS_STREAM_NAME**  
  Nombre del stream de Kinesis al cual el Lambda enviará los datos.  

### Ejemplo en la consola de AWS Lambda:
1. Ir al **Lambda** en la consola de AWS.  
2. En la pestaña **Configuration** → **Environment variables**, añadir:  
   ```
   KINESIS_STREAM_NAME=f1-vote-stream
   ```
3. Guardar cambios y volver a desplegar.

⚡ En entornos reales se recomienda:
- Usar diferentes streams según ambiente (`f1-vote-stream-dev`, `f1-vote-stream-prod`).
- Administrar secretos y configuraciones sensibles en **AWS Systems Manager Parameter Store** o **AWS Secrets Manager**.

---

## Configuración de CORS

Uno de los puntos más importantes para que el frontend pueda comunicarse con el Lambda (a través del API Gateway) es configurar correctamente **CORS**.

En este código, los encabezados se incluyen en todas las respuestas:

```json
"headers": {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST,OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type"
}
```

### Explicación:
- **Access-Control-Allow-Origin:** `"*"` → Permite el acceso desde cualquier origen.  
  ⚠️ En producción deberías restringirlo a tu dominio específico (ejemplo: `"https://midominio.com"`).
  
- **Access-Control-Allow-Methods:** `"POST,OPTIONS"` → Define qué métodos están permitidos desde el frontend.  
  - `POST`: para enviar votos.  
  - `OPTIONS`: necesario para las solicitudes **preflight** que hace el navegador antes de enviar datos reales.
  
- **Access-Control-Allow-Headers:** `"Content-Type"` → Permite que el cliente envíe datos en formato JSON.

---

## Consideraciones Importantes

✅ **CORS en API Gateway**  
Además de definir los encabezados en el Lambda, asegúrate de habilitar CORS en tu **API Gateway**:
1. En la consola de API Gateway, selecciona tu API.  
2. En cada recurso y método (`/vote`, `POST` y `OPTIONS`), activa **Enable CORS**.  
3. Despliega nuevamente la API.  

✅ **Errores comunes con CORS**  
- Si no habilitas **OPTIONS** como método en tu API Gateway, el navegador bloqueará la petición.  
- Los encabezados deben estar en **todas las respuestas** (200, 400, 500), de lo contrario algunas llamadas fallarán.

---

Con esta configuración, tu Lambda productor podrá recibir votos desde el frontend y enviarlos de forma segura a **Kinesis Data Streams**, asegurando compatibilidad con navegadores y buenas prácticas en el manejo de configuraciones.
