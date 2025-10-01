# 🏎️ Procesamiento de Datos en Tiempo Real con AWS Kinesis – Demo F1 Voting  

Este proyecto es un **demo de votaciones en tiempo real** construido con servicios serverless de AWS.  
El objetivo es mostrar cómo **Amazon Kinesis** permite procesar datos en **streaming** y entregar resultados inmediatos.  

---

## 📌 Introducción  

Los usuarios votan desde un **frontend web** (desplegado en S3).  
Los votos son enviados a través de **API Gateway**, procesados por **Lambda Producer** y transmitidos en **Kinesis Data Streams**.  
Un **Lambda Consumer** los guarda en **DynamoDB**, y un **Lambda Results** expone los resultados para el dashboard.  

---

## 🏗️ Arquitectura  

![Arquitectura](Demo%20AWS%20Community%20day%20Bolivia.drawio.png)

### Flujo

👉 **Productores**  
1. Usuario abre el frontend (HTML en S3).  
2. El voto se envía a API Gateway.  
3. API Gateway invoca a Lambda Producer.  
4. Lambda coloca el voto en el stream de Kinesis.  

👉 **Consumidores**  
1. Lambda Consumer lee los votos desde Kinesis.  
2. DynamoDB almacena y actualiza los resultados.  
3. Lambda Results expone los resultados en un endpoint `/results`.  
4. El dashboard en S3 consume este endpoint y actualiza en tiempo real.  

---

## ⚙️ Implementación paso a paso  

### 1. Crear el stream en Kinesis
```bash
# En la consola de AWS:
- Kinesis Data Streams → Create
- Nombre: f1-votes
- Shards: 1
```

### Estructura del proyecto
/demo-f1-voting-kinesis
│── frontend/
│   ├── index.html
│   ├── dashboard.html
│── lambdas/
│   ├── producer.py
│   ├── consumer.py
│   ├── results.py
│── architecture.png
│── README.md


✨ Créditos

Demo construida para AWS Community Day Bolivia 2025
Autora: Silvana Gutierrez M. 🚀


