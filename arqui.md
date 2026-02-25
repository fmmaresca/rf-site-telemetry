# RF Site Telemetry (Edge → Cloud) — Especificación

## 1. Propósito

Construir un sistema público de portfolio que demuestre patrones de ingeniería "product-grade" para telemetría desde edge hacia cloud:

- buffering offline (store & forward)
- retries con backoff y circuit breaker liviano
- idempotencia y deduplicación end-to-end
- diseño de topics MQTT y fallback HTTP
- provisioning (claim + credenciales) y configuración remota
- observabilidad (métricas/health) y dashboard
- multi-tenant básico (por `tenant` lógico)

El caso de uso simula/implementa un “RF remote site”: monitoreo de temperatura, tensiones de fuentes (12V/5V), y estado del nodo.

## 2. Alcance

### Incluye
- Agente edge en Python (Linux / Raspberry / mini-PC)
- Cloud API en Python (HTTP + adaptador MQTT opcional)
- PostgreSQL como storage principal (time-series vía esquema e índices)
- Dashboard web (MVP simple: latest + series)
- Simulador de devices para carga y demo

### No incluye (por ahora)
- Control/actuación (commands) salvo configuración remota (pull o push)
- OTA firmware real (solo placeholder)
- PKI compleja (se diseña, se implementa mínimo viable)

## 3. Componentes

### 3.1 Edge Agent
Responsabilidades:
- recolectar métricas (real o simuladas)
- empaquetar en un envelope estable (v1)
- publicar por MQTT y/o enviar por HTTP ingest
- persistir cola local (SQLite) cuando no hay conectividad
- reintentar con backoff y jitter
- exponer health local (log + opcional HTTP localhost)

### 3.2 Cloud API
Responsabilidades:
- endpoint HTTP de ingesta (single/batch)
- validación de esquema + normalización
- dedupe (idempotencia)
- persistencia en PostgreSQL
- consultas: latest + series
- autenticación (API key por device/tenant en MVP)
- endpoints de provisioning (claim) y config (fase 2)

### 3.3 Dashboard
Responsabilidades:
- mostrar lista de devices
- último estado (última medición + age)
- gráficos de series por métrica (temp, 12v, 5v)
- alertas simples (umbral) opcional

### 3.4 Simulator
Responsabilidades:
- generar eventos realistas (seno + ruido + fallas)
- enviar por HTTP y/o MQTT
- configurable: N devices, rate, latencia artificial, pérdida

## 4. Identidad y multi-tenant

- `tenant`: string corta (ej: "demo")
- `device_id`: identificador estable (ej: "rfsite-001")
- Un device pertenece a un tenant.

En MVP: tenant se deriva del API key y/o se valida que `tenant` del payload coincida.

## 5. Contrato de datos (Telemetry Envelope v1)

### 5.1 Event Envelope (JSON)
Campos:
- `v` (int): versión del envelope. **Siempre 1** en esta fase.
- `tenant` (str)
- `device_id` (str)
- `ts` (RFC3339 UTC string): timestamp de la medición (event time)
- `seq` (int64): contador monotónico por device (persistente si posible)
- `msg_id` (str): idempotency key. Recomendado: `{device_id}:{seq}`
- `metrics` (obj): mapa de métricas numéricas
- `status` (obj, opcional): metadata del device

Ejemplo:
```json
{
  "v": 1,
  "tenant": "demo",
  "device_id": "rfsite-001",
  "ts": "2026-02-25T10:12:03Z",
  "seq": 1842,
  "msg_id": "rfsite-001:1842",
  "metrics": {
    "temp_c": 31.4,
    "psu_12v": 12.08,
    "psu_5v": 5.02
  },
  "status": {
    "rssi_dbm": -67,
    "uptime_s": 92311,
    "fw": "edge-agent/0.1.0"
  }
}


rf-site-telemetry/
  README.md
  LICENSE
  docs/
    architecture.md
    protocol.md
    provisioning.md
    threat-model.md
  edge-agent/
    README.md
    pyproject.toml (o go.mod)
    src/...
    systemd/telemetry-agent.service
    config/telemetry.example.yaml
  cloud-api/
    README.md
    docker/ (si usás)
    src/...
    openapi.yaml
  dashboard/
    README.md
    src/...
  infra/
    docker-compose.dev.yml
    migrations/
  tools/
    simulator/
    scripts/
