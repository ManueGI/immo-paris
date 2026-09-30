import { Component } from '@angular/core';
import { RouterLink, RouterOutlet } from '@angular/router';

/** Root component: the layout shared by every page. Pages render inside <router-outlet>. */
@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {}
