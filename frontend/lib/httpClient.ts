type EnvelopeResult = "success" | "failure" | "error";

interface Envelope<T> {
  result: EnvelopeResult;
  data?: T;
}

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  const envelope: Envelope<T> = await response.json();

  if (envelope.result !== "success") {
    throw new ApiError(
      `Request to ${path} failed with result "${envelope.result}"`,
      response.status,
    );
  }

  return envelope.data as T;
}

export const httpClient = {
  get: <T>(path: string): Promise<T> => request<T>(path),

  post: <T>(path: string, body?: unknown): Promise<T> =>
    request<T>(path, {
      method: "POST",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),

  patch: <T>(path: string, body?: unknown): Promise<T> =>
    request<T>(path, {
      method: "PATCH",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),

  delete: <T>(path: string): Promise<T> =>
    request<T>(path, { method: "DELETE" }),
};
