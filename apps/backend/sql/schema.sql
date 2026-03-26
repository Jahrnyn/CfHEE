CREATE TABLE IF NOT EXISTS workspaces (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS domains (
  id BIGSERIAL PRIMARY KEY,
  workspace_id BIGINT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (workspace_id, name)
);

CREATE TABLE IF NOT EXISTS projects (
  id BIGSERIAL PRIMARY KEY,
  domain_id BIGINT NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (domain_id, name)
);

CREATE TABLE IF NOT EXISTS clients (
  id BIGSERIAL PRIMARY KEY,
  project_id BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (project_id, name)
);

CREATE TABLE IF NOT EXISTS modules (
  id BIGSERIAL PRIMARY KEY,
  client_id BIGINT NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (client_id, name)
);

CREATE TABLE IF NOT EXISTS documents (
  id BIGSERIAL PRIMARY KEY,
  workspace_id BIGINT NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
  domain_id BIGINT NOT NULL REFERENCES domains(id) ON DELETE RESTRICT,
  project_id BIGINT REFERENCES projects(id) ON DELETE RESTRICT,
  client_id BIGINT REFERENCES clients(id) ON DELETE RESTRICT,
  module_id BIGINT REFERENCES modules(id) ON DELETE RESTRICT,
  title TEXT NOT NULL,
  source_type TEXT NOT NULL,
  language TEXT,
  source_ref TEXT,
  raw_text TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chunks (
  id BIGSERIAL PRIMARY KEY,
  document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  workspace_id BIGINT NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
  domain_id BIGINT NOT NULL REFERENCES domains(id) ON DELETE RESTRICT,
  project_id BIGINT REFERENCES projects(id) ON DELETE RESTRICT,
  client_id BIGINT REFERENCES clients(id) ON DELETE RESTRICT,
  module_id BIGINT REFERENCES modules(id) ON DELETE RESTRICT,
  chunk_index INTEGER NOT NULL,
  text TEXT NOT NULL,
  char_count INTEGER NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (document_id, chunk_index)
);

CREATE TABLE IF NOT EXISTS query_logs (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  query_text TEXT NOT NULL,
  workspace TEXT NOT NULL,
  domain TEXT NOT NULL,
  project TEXT,
  client TEXT,
  module TEXT,
  top_k INTEGER,
  result_count INTEGER NOT NULL,
  empty_result BOOLEAN NOT NULL,
  retrieved_chunk_ids JSONB NOT NULL,
  retrieved_document_ids JSONB NOT NULL,
  selected_context_chunk_ids JSONB,
  dropped_context_chunk_ids JSONB,
  answer_text TEXT,
  has_evidence BOOLEAN,
  context_used_count INTEGER,
  answer_length INTEGER,
  grounded_flag TEXT,
  candidate_count INTEGER,
  top_k_limit_hit BOOLEAN,
  returned_distance_values JSONB,
  returned_document_distribution JSONB,
  provider_used TEXT NOT NULL,
  fallback_used BOOLEAN NOT NULL DEFAULT FALSE
);

ALTER TABLE query_logs
ADD COLUMN IF NOT EXISTS selected_context_chunk_ids JSONB;

ALTER TABLE query_logs
ADD COLUMN IF NOT EXISTS dropped_context_chunk_ids JSONB;

ALTER TABLE query_logs
ADD COLUMN IF NOT EXISTS has_evidence BOOLEAN;

ALTER TABLE query_logs
ADD COLUMN IF NOT EXISTS context_used_count INTEGER;

ALTER TABLE query_logs
ADD COLUMN IF NOT EXISTS answer_length INTEGER;

ALTER TABLE query_logs
ADD COLUMN IF NOT EXISTS grounded_flag TEXT;

ALTER TABLE query_logs
ADD COLUMN IF NOT EXISTS candidate_count INTEGER;

ALTER TABLE query_logs
ADD COLUMN IF NOT EXISTS top_k_limit_hit BOOLEAN;

ALTER TABLE query_logs
ADD COLUMN IF NOT EXISTS returned_distance_values JSONB;

ALTER TABLE query_logs
ADD COLUMN IF NOT EXISTS returned_document_distribution JSONB;
