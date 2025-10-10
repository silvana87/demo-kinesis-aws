# 📌 Publicar tu frontend `vote.html` en Amazon S3

En esta guía aprenderás cómo desplegar una aplicación frontend simple (en este caso `vote.html`) en un **bucket de Amazon S3** para que esté disponible como una página web estática.

---

## 1️⃣ Crear un bucket en S3
1. Ve a la consola de **Amazon S3** → [https://s3.console.aws.amazon.com/s3](https://s3.console.aws.amazon.com/s3).
2. Haz clic en **Create bucket**.
3. Configura:
   - **Bucket name**: debe ser único (ejemplo: `vote-demo-frontend`).
   - **Region**: selecciona la misma región de tus recursos (ej. `us-east-1`).
4. En la sección **Block Public Access**:
   - Desmarca **Block all public access**.
   - Confirma que el bucket será público (necesario para servir un sitio estático).
5. Haz clic en **Create bucket**.

---

## 2️⃣ Subir tus archivos
1. Abre tu bucket → pestaña **Objects**.
2. Haz clic en **Upload**.
3. Sube:
   - `vote.html`
   - `config.json`
   - (y cualquier archivo adicional: CSS, JS, imágenes).
4. Finaliza con **Upload**.

---

## 3️⃣ Habilitar hospedaje de sitio estático
1. Dentro de tu bucket, ve a **Properties**.
2. Busca la sección **Static website hosting** → Haz clic en **Edit**.
3. Selecciona:
   - **Enable**.
   - **Index document**: `vote.html`.
4. Guarda los cambios.
5. Obtendrás una **URL pública del sitio web** (ejemplo:  
   ```
   http://vote-demo-frontend.s3-website-us-east-1.amazonaws.com
   ```

---

## 4️⃣ Configurar permisos públicos
Para que tus archivos sean accesibles públicamente, necesitas:
1. Ir a la pestaña **Permissions** del bucket.
2. En **Bucket policy**, agrega algo como lo siguiente (reemplaza `vote-demo-frontend` con el nombre de tu bucket):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::vote-demo-frontend/*"
    }
  ]
}
```

3. Guarda los cambios.  
   Ahora tus archivos (`vote.html`, `config.json`, etc.) son accesibles vía URL pública.

---

## 5️⃣ Configuración de CORS

El **CORS (Cross-Origin Resource Sharing)** es clave para que tu frontend pueda conectarse con tu **API Gateway** y leer `config.json` desde S3. Sin esto, el navegador bloquea las peticiones.

### 🔹 Configuración en el bucket S3
En la pestaña **Permissions** → **Cross-origin resource sharing (CORS)**, añade algo como lo siguiente:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": []
  }
]
```

👉 Esto permite que tu `vote.html` cargue archivos como `config.json` desde cualquier origen.  
En entornos productivos, lo ideal es restringir `"AllowedOrigins"` al dominio de tu frontend.

---

### 🔹 Configuración en API Gateway
En **API Gateway**, debes habilitar CORS en los endpoints de tu API (`/vote`, `/results`).

1. Selecciona tu API en la consola de API Gateway.
2. Abre el recurso (ejemplo `/vote`).
3. En la acción → selecciona **Enable CORS**.
4. Configura:
   - **Allowed Origins**: `*` (para demo) o tu dominio específico en producción.
   - **Allowed Methods**: `GET, POST, OPTIONS`.
   - **Allowed Headers**: `Content-Type`.
5. Guarda y **Deploy API**.

Tu Lambda debe también devolver estos headers en la respuesta. Ejemplo en Python:

```python
return {
    'statusCode': 200,
    'headers': {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    },
    'body': json.dumps({'message': 'Voto recibido exitosamente'})
}
```

---

## 6️⃣ Parametrizar variables con `config.json`
En lugar de hardcodear tu URL de API en el HTML, puedes usar un archivo externo `config.json`.  

### Ejemplo de `config.json`:
```json
{
  "API_GATEWAY_URL": "https://xxxx.execute-api.us-east-1.amazonaws.com/prod/vote"
}
```

### Ejemplo en `vote.html`:
```html
<script>
    let API_GATEWAY_URL = '';

    async function loadConfig() {
        const response = await fetch('config.json');
        const config = await response.json();
        API_GATEWAY_URL = config.API_GATEWAY_URL;
    }

    async function submitVote(voteOption) {
        if (!API_GATEWAY_URL) {
            await loadConfig();
        }
        // ... resto de tu código
    }
</script>
```

### ¿Por qué esta configuración?
- **Separación de configuración y código**: el endpoint de tu API ya no queda fijo en el HTML, sino que se puede cambiar fácilmente desde `config.json` sin redeployar la página.  
- **Flexibilidad para diferentes entornos**: en proyectos reales, normalmente tendrías distintos endpoints (ejemplo: *desarrollo, staging, producción*). Una buena práctica es que estos valores se manejen con **Variables de entorno** o un servicio de configuración centralizado (ej. AWS Systems Manager Parameter Store, Secrets Manager o CloudFront con Lambda@Edge).  
- **Para este ejemplo**: usamos un simple `config.json` porque es fácil de implementar y suficiente para un demo. En escenarios empresariales, deberías evitar exponer configuraciones sensibles en un archivo público.

---

## 7️⃣ Consideraciones importantes
- **Cache**: si usas CloudFront o tu navegador cachea el `config.json`, usa `?v=1` en la URL para forzar refresco.  
- **HTTPS**: la URL de S3 es HTTP en la mayoría de regiones. Para HTTPS, utiliza **CloudFront** con un certificado SSL.  
- **Seguridad**: evita exponer información sensible en el frontend. El API Gateway debe tener validaciones y seguridad (por ejemplo, un API Key o autorización con IAM si no quieres exponerlo libremente).  
- **Costo**: el hosting en S3 cuesta centavos. Solo pagas por almacenamiento + requests + ancho de banda.  

---

## ✅ Resultado
Ahora tienes tu página `vote.html` disponible como un sitio web en Amazon S3, conectado con tu backend en API Gateway + Lambda + Kinesis.  

🎉 Con esto, cualquier persona puede entrar al link de tu bucket y votar en tiempo real en tu demo.
