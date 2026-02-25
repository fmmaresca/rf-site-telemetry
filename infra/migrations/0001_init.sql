BEGIN;

CREATE TABLE IF NOT EXISTS tenants (
  tenant TEXT PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS devices (
  tenant TEXT NOT NULL REFERENCES tenants(tenant) ON DELETE CASCADE,
  device_id TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_seen_at TIMESTAMPTZ,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  PRIMARY KEY (tenant, device_id)
);

CREATE TABLE IF NOT EXISTS telemetry (
  tenant TEXT NOT NULL,
  device_id TEXT NOT NULL,
  ts TIMESTAMPTZ NOT NULL,
  seq BIGINT NOT NULL,
  msg_id TEXT NOT NULL,
  metrics JSONB NOT NULL,
  status JSONB NOT NULL DEFAULT '{}'::jsonb,
  ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (tenant, device_id, seq),
  CONSTRAINT fk_device FOREIGN KEY (tenant, device_id)
    REFERENCES devices(tenant, device_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS telemetry_by_device_ts
  ON telemetry (tenant, device_id, ts DESC);

COMMIT;
