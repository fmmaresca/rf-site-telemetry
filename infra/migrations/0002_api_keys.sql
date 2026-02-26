BEGIN;

CREATE TABLE IF NOT EXISTS api_keys (
  api_key TEXT PRIMARY KEY,
  tenant TEXT NOT NULL REFERENCES tenants(tenant) ON DELETE CASCADE,
  device_id TEXT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  revoked_at TIMESTAMPTZ NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS api_keys_by_tenant
  ON api_keys (tenant);

COMMIT;
