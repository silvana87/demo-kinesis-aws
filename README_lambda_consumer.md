# Lambda Consumidor - Procesamiento de Votos en Tiempo Real

Este componente forma parte de la demo de **procesamiento de datos en tiempo real con AWS Kinesis**.  
El **Lambda consumidor** se encarga de leer los datos desde el stream de Kinesis y registrarlos en **DynamoDB** para su posterior consulta desde un dashboard.

---

## 🚀 Flujo de Trabajo

1. El **Lambda productor** envía los votos al **Kinesis Data Stream**.
2. El **Lambda consumidor** se activa automáticamente cada vez que Kinesis recibe datos.
3. Los registros se procesan y se actualizan los conteos en **DynamoDB**.
4. El frontend (dashboard) consulta los resultados desde la base de datos vía API Gateway.

---

## ⚙️ Configuración de DynamoDB

1. Crear una tabla DynamoDB con:
   - **Nombre**: `f1-vote-results` (o el nombre que definas).
   - **Partition Key**: `option_id` (tipo `String`).

2. La tabla guardará registros con el siguiente esquema:
   ```json
   {
     "option_id": "Ferrari",
     "votes": 5
   }
   ```

3. Cada voto incrementará el campo `votes`.

---

## 🔧 Variables de Entorno

En la Lambda configuramos la siguiente variable de entorno:

- `DYNAMODB_TABLE_NAME`: nombre de la tabla DynamoDB (ej. `f1-vote-results`).

---

## 🔗 Configuración del Trigger en Lambda

Para que la función se ejecute cuando lleguen datos a Kinesis:

1. Abrir la consola de Lambda.
2. Seleccionar la función **consumidor**.
3. Ir a la pestaña **Desencadenadores (Triggers)**.
4. Añadir un nuevo trigger de tipo **Kinesis**:
   - Seleccionar el stream creado (ej. `f1-vote-stream`).
   - Configurar el batch size (ej. `100`).
   - Guardar.

Con esto, la Lambda se invoca automáticamente cada vez que llegan nuevos votos al stream.

---

## 📝 Código del Consumidor

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
            print(f"Processing vote for: {vote_option}")
            table.update_item(
                Key={'option_id': vote_option},   # Debe coincidir con tu Partition Key
                UpdateExpression="ADD votes :inc",
                ExpressionAttributeValues={':inc': 1},
                ReturnValues="UPDATED_NEW"
            )
        else:
            print("No vote option found in record.")

    return {'statusCode': 200, 'body': 'Successfully processed records'}
```

---

## ✅ Consideraciones

- La **Partition Key** en DynamoDB (`option_id`) debe coincidir con el campo que se envía desde el productor (`vote`).
- El campo `votes` se maneja como un contador que se incrementa automáticamente.
- Revisar **CloudWatch Logs** en caso de errores.
- Verificar permisos en la **IAM Role** de la Lambda:
  - `dynamodb:UpdateItem`
  - `dynamodb:PutItem`
  - `dynamodb:GetItem`

---

## 📊 Resultado Esperado

Cada vez que se registre un voto en el frontend:
- Se envía al Kinesis Stream.
- El consumidor lo procesa.
- DynamoDB actualiza el contador.
- El dashboard mostrará los resultados en tiempo real.
