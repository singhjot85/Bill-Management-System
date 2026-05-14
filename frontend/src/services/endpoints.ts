/**
 * Endpoint Keys
 * Using Object.freeze for immutability and to serve as a single source of truth for endpoint identifiers.
 */
export const ENDPOINTS = Object.freeze({
  // Auth Endpoints
  LOGIN: 'LOGIN',
  LOGOUT: 'LOGOUT',
  ME: 'ME',

  // Branding & Configuration
  BRANDING: 'BRANDING',

  // Workflow & Business Logic
  VALIDATE_EMAIL: 'VALIDATE_EMAIL',
  VALIDATE_PHONE: 'VALIDATE_PHONE',
  MAKE_PAYMENT: 'MAKE_PAYMENT',
  SUBMIT_FORM: 'SUBMIT_FORM',
  INVOICE: 'INVOICE',
});

/**
 * Public Schema Endpoints (Platform-wide)
 * These are used when the tenant context is 'public'.
 */
const PUBLIC_ENDPOINTS: Record<string, string> = Object.freeze({
  [ENDPOINTS.LOGIN]: 'auth/login/',
  [ENDPOINTS.BRANDING]: 'branding/',
});


/**
 * Tenant Schema Endpoints (Private/Tenant-specific)
 * These are used when operating within a specific tenant's schema.
 */
const PRIVATE_ENDPOINTS: Record<string, string> = Object.freeze({
  [ENDPOINTS.LOGIN]: 'auth/login/',
  [ENDPOINTS.LOGOUT]: 'auth/logout/',
  [ENDPOINTS.ME]: 'auth/me/',
  [ENDPOINTS.VALIDATE_EMAIL]: 'workflow/validate_email/',
  [ENDPOINTS.VALIDATE_PHONE]: 'workflow/validate_phone/',
  [ENDPOINTS.MAKE_PAYMENT]: 'workflow/make_payment/',
  [ENDPOINTS.SUBMIT_FORM]: 'workflow/submit_form/',
  [ENDPOINTS.INVOICE]: 'workflow/invoice/',
});

/**
 * Resolves an API endpoint path based on the current tenant context.
 *
 * @param endpointKey - The unique key identifying the endpoint (from ENDPOINTS constant).
 * @param tenantName - The current tenant context. Defaults to 'public'.
 * @returns The relative path for the requested endpoint.
 *
 * @example
 * const path = getEndpoint(ENDPOINTS.LOGIN, 'public'); // returns 'auth/login/'
 */
export function getEndpoint(endpointKey: string, tenantName: string = 'public'): string {
  const endpointsMap = tenantName === 'public' ? PUBLIC_ENDPOINTS : PRIVATE_ENDPOINTS;
  const path = endpointsMap[endpointKey];

  if (!path) {
    console.error(`[Endpoints] Key "${endpointKey}" not found in context "${tenantName}"`);
    return '';
  }

  return path;
}

export default {
  ENDPOINTS,
  getEndpoint,
};
