# Equilibrio Estudiantil

Sistema distribuido basado en microservicios desarrollado con Flask, Docker y MySQL.

El proyecto implementa una arquitectura distribuida funcional utilizando múltiples microservicios desacoplados, comunicación HTTP REST, API Gateway, persistencia independiente, monitoreo básico y tolerancia a fallos mediante Circuit Breaker.

---

# Descripción del sistema

Equilibrio Estudiantil es un sistema distribuido orientado al bienestar estudiantil. El objetivo principal es demostrar la implementación práctica de arquitecturas distribuidas utilizando microservicios contenerizados.

El sistema permite administrar:

- usuarios
- estados emocionales
- sesiones
- recomendaciones
- notificaciones

Cada módulo funciona como un microservicio independiente conectado mediante HTTP REST a través de un API Gateway centralizado.

---

# Objetivos del proyecto

- Implementar una arquitectura basada en microservicios.
- Aplicar conceptos de sistemas distribuidos.
- Implementar comunicación HTTP entre servicios.
- Utilizar Docker y Docker Compose.
- Implementar persistencia desacoplada.
- Aplicar tolerancia a fallos mediante Circuit Breaker.
- Implementar monitoreo básico y métricas.
- Gestionar servicios independientes y escalables.

---

# Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Python | Lenguaje principal |
| Flask | Framework backend |
| Flask-CORS | Manejo de políticas CORS |
| MySQL | Base de datos |
| Docker | Contenerización |
| Docker Compose | Orquestación de contenedores |
| REST API | Comunicación entre servicios |
| JSON | Intercambio de datos |

---

# Arquitectura del sistema

## Arquitectura general

El sistema utiliza una arquitectura distribuida basada en microservicios.

Cada microservicio cuenta con:

- lógica independiente
- contenedor Docker propio
- base de datos desacoplada
- endpoints REST independientes

Todos los servicios se comunican mediante un API Gateway centralizado.

---

# Microservicios implementados

| Servicio | Puerto | Función |
|---|---|---|
| Gateway | 5000 | Punto central de acceso |
| Usuarios | 5001 | Gestión de usuarios |
| Moods | 5002 | Estados emocionales |
| Sesiones | 5003 | Gestión de sesiones |
| Recomendaciones | 5004 | Motor de recomendaciones |
| Notificaciones | 5005 | Gestión de notificaciones |

---

# Docker Compose

## Levantar sistema

```bash
docker-compose up --build
```

## Ver contenedores

```bash
docker ps
```

## Detener sistema

```bash
docker-compose down
```

---

# Endpoints principales

## Usuarios

| Método | Endpoint |
|---|---|
| GET | /usuarios |
| POST | /usuarios |

## Notificaciones

| Método | Endpoint |
|---|---|
| POST | /notificaciones |

## Gateway

| Endpoint | Función |
|---|---|
| /health | Estado del sistema |
| /metrics/latency | Métricas |
| /circuits | Circuit Breaker |

---

# Tolerancia a fallos

El sistema implementa tolerancia a fallos mediante Circuit Breaker.

Estados implementados:

- CLOSED
- OPEN
- HALF-OPEN

---

# Monitoreo

El sistema implementa:

- Health checks
- Métricas de latencia
- Logs
- Validación de disponibilidad

---

# Seguridad básica

- Variables de entorno
- Redes Docker
- Flask-CORS
- Bases de datos desacopladas

---

# Variables de entorno

```env
DB_ROOT_PASSWORD=123456
DB_HOST=db-usuarios
DB_USER=root
DB_PASSWORD=123456
DB_NAME=db_usuarios
```

---

# Escalabilidad

La arquitectura permite:

- Escalamiento independiente
- Replicación de servicios
- Balanceo de carga futuro
- Integración con Kubernetes

---

# Autores

- Cristian Javier
- Integrantes del grupo

---

# Licencia

Proyecto académico desarrollado para la asignatura de Sistemas Distribuidos.
