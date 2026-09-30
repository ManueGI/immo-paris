import { Component, RESPONSE_INIT, inject } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-not-found-page',
  imports: [RouterLink],
  template: `
    <h1>Page introuvable</h1>
    <p>Cette page n'existe pas. <a routerLink="/">Voir les prix par arrondissement</a></p>
  `,
})
export class NotFoundPage {
  constructor() {
    // During server rendering, answer with a real 404 status so search engines do not
    // index this page; RESPONSE_INIT is null in the browser
    const response = inject(RESPONSE_INIT, { optional: true });
    if (response) response.status = 404;
  }
}
