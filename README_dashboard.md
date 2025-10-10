# 📊 Dashboard de Resultados en Vivo con AWS S3 y API Gateway

Este proyecto muestra un **dashboard en tiempo real** que visualiza los resultados de una votación almacenada en AWS (por ejemplo, un flujo de datos en **Kinesis** o **DynamoDB**, expuesto a través de **API Gateway**).

El frontend es un sitio estático hospedado en **Amazon S3**, que consulta una API mediante **fetch** y actualiza los resultados cada 2 segundos.

---

## 🧱 Estructura del Proyecto

```
📁 aws-vote-dashboard/
│
├── dashboard.html          # Archivo principal del frontend
├── config.json             # Configuración de la API Gateway
├── styles.css              # Estilos opcionales
└── README.md               # Documentación
```

---

## ⚙️ 1. Configurar el archivo `config.json`

Este archivo contiene la URL de la API Gateway que provee los resultados de votación.  
De esta manera, el código puede adaptarse fácilmente a distintos entornos (por ejemplo: desarrollo, staging, producción) sin modificar el HTML.

```json
{
  "API_GET_RESULTS_URL": "https://XXXXXXXXXXX.execute-api.us-east-1.amazonaws.com/prod/results"
}
```

💡 **Por qué se usa esta configuración:**

En entornos reales, la URL de la API suele variar entre entornos (por ejemplo, un dominio distinto o un stage diferente).  
Por eso, **parametrizar la configuración** en un archivo externo (`config.json`) permite desacoplar el código del entorno de ejecución.  
Para este ejemplo, basta con mantener el `config.json` en el mismo bucket junto al HTML.

---

## 💻 2. Código del `dashboard.html`

El archivo `dashboard.html` carga dinámicamente la configuración desde `config.json`, obtiene los datos desde la API y los renderiza visualmente.

- Lee la URL de la API desde `config.json`.
- Llama al endpoint `/results` cada 2 segundos.
- Calcula el porcentaje de votos y genera una barra de progreso por opción.

📄 Código completo: [dashboard.html](./dashboard.html)

---

## ☁️ 3. Publicar el frontend en un bucket S3

### 🔹 Paso 1: Crear el bucket

1. Ingresa a la consola de **Amazon S3**.  
2. Crea un nuevo bucket (por ejemplo: `aws-vote-dashboard-demo`).  
3. **Desactiva el bloqueo de acceso público** (ya que el sitio será accesible públicamente).  
4. Sube los archivos:  
   - `dashboard.html`
   - `config.json`
   - `styles.css` (si existe)

---

### 🔹 Paso 2: Habilitar hospedaje estático

1. En las propiedades del bucket, activa **Static website hosting**.  
2. Define:
   - **Index document:** `dashboard.html`
3. Copia la URL del sitio que te proporciona S3 (por ejemplo:  
   `http://aws-vote-dashboard-demo.s3-website-us-east-1.amazonaws.com`)

---

## 🌐 4. Configurar CORS en el bucket S3

Para que el navegador pueda leer el `config.json` y mostrar los datos de la API, el bucket debe permitir solicitudes desde otros orígenes (por ejemplo, desde el dominio de tu API Gateway o desde cualquier origen para pruebas).

Configura el **CORS** del bucket con el siguiente contenido:

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

💡 *En un entorno productivo*, conviene reemplazar `"*"` por los dominios específicos que usarán el frontend (por ejemplo, `"https://dashboard.midominio.com"`).

---

## 🔐 5. Políticas de permisos del bucket

Asegúrate de que los archivos sean **públicamente legibles**.  
Puedes aplicar la siguiente política de bucket (reemplazando `YOUR_BUCKET_NAME` por el nombre real):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
    }
  ]
}
```

---

## 🚀 6. Probar la aplicación

Una vez subidos los archivos y configurado el bucket:

1. Abre la URL pública del sitio estático (por ejemplo:  
   `http://aws-vote-dashboard-demo.s3-website-us-east-1.amazonaws.com`).
2. El dashboard debería cargar la configuración desde `config.json`.
3. Verás los resultados de votación actualizándose cada 2 segundos.

Si aparece un error en consola, revisa:
- Que el archivo `config.json` esté accesible públicamente.
- Que la API Gateway tenga configurado correctamente **CORS** (aceptando el origen del frontend).

---

## 🧩 7. Configuración de CORS en API Gateway (recomendado)

Para permitir que el frontend acceda a la API, asegúrate de habilitar CORS en el método `/results` de tu API Gateway:

### En la consola de API Gateway:
1. Selecciona tu API.
2. En el método `/results`, elige **Enable CORS**.
3. Define:
   - **Access-Control-Allow-Origin:** `*` (o tu dominio específico)
   - **Access-Control-Allow-Methods:** `GET`
4. Guarda y **reimplementa la API**.

---

## 🧭 Resultado Final

Una vez implementado, tendrás un dashboard como este:

![Demo de Dashboard](https://user-images.githubusercontent.com/placeholder/aws-dashboard-demo.png)

- Los resultados se actualizan automáticamente.
- Los estilos son personalizables.
- Se puede integrar fácilmente con flujos de datos reales en AWS.

---

## 🧰 Tecnologías Utilizadas

- **Amazon S3** — Hosting estático del frontend  
- **API Gateway** — Exposición de datos desde backend o Lambda  
- **JavaScript** — Actualización dinámica del DOM  
- **CORS & IAM Policies** — Control de acceso seguro  

---

## 👩‍💻 Autor

**Silvana Gutiérrez**  
Expert Backend Developer | Cloud & Data Enthusiast  
💡 Promoviendo el aprendizaje de tecnologías cloud y automatización inteligente de datos.
