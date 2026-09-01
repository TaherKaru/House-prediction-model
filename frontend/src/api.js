const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export async function api(path, options = {}) {
  const { headers: customHeaders = {}, ...requestOptions } = options;
  const mergedHeaders = {
    ...(requestOptions.body ? { 'Content-Type': 'application/json' } : {}),
    ...customHeaders,
  };

  const response = await fetch(`${API_URL}${path}`, {
    ...requestOptions,
    headers: mergedHeaders,
  });

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const validationMessage = Array.isArray(body.detail)
      ? body.detail.map((issue) => `${issue.loc?.at(-1) || 'field'}: ${issue.msg}`).join(', ')
      : body.detail;
    throw new Error(body.error || validationMessage || 'Something went wrong. Please try again.');
  }
  return body;
}

export { API_URL };
