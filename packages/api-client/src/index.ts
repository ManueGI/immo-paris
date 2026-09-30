/**
 * Typed client of the Immo Paris API, generated from api/openapi.json.
 *
 * - The types (Sale, SalePage...) work with any HTTP layer, e.g. Angular's HttpClient.
 * - createApiClient() is a small fetch-based client (openapi-fetch) for React Native / Expo
 *   or any runtime with fetch: paths, query parameters and responses are all type-checked.
 *
 * src/schema.ts is generated (`pnpm generate`): never edit it by hand.
 */
import createClient, { type ClientOptions } from "openapi-fetch";

import type { components, paths } from "./schema.js";

type Schemas = components["schemas"];

export type Sale = Schemas["Sale"];
export type SalePage = Schemas["SalePage"];
export type NearbySale = Schemas["NearbySale"];
export type CommuneStats = Schemas["CommuneStats"];
export type PropertyType = Schemas["PropertyType"];
export type ErrorResponse = Schemas["ErrorResponse"];
export type ValidationErrorResponse = Schemas["HTTPValidationError"];
export type { components, paths };

export type ApiClient = ReturnType<typeof createApiClient>;

export function createApiClient(options: ClientOptions & { baseUrl: string }) {
  return createClient<paths>(options);
}
