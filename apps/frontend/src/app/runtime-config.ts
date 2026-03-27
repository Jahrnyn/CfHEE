const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000';

type CfheeRuntimeConfig = {
  apiBaseUrl?: string;
};

function getRuntimeConfig(): CfheeRuntimeConfig {
  const candidate = (globalThis as { __CFHEE_RUNTIME_CONFIG__?: CfheeRuntimeConfig }).__CFHEE_RUNTIME_CONFIG__;
  if (!candidate || typeof candidate !== 'object') {
    return {};
  }

  return candidate;
}

export function getApiBaseUrl(): string {
  const configuredBaseUrl = getRuntimeConfig().apiBaseUrl?.trim();
  if (!configuredBaseUrl) {
    return DEFAULT_API_BASE_URL;
  }

  return configuredBaseUrl.replace(/\/+$/, '');
}
