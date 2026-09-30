import { RenderMode, ServerRoute } from '@angular/ssr';

/**
 * How each route is rendered on the server. Pages depend on live API data, so they are
 * rendered on each request (Server), not prerendered at build time (Prerender), which
 * would need the API during the build.
 */
export const serverRoutes: ServerRoute[] = [{ path: '**', renderMode: RenderMode.Server }];
