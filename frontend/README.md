# Frontend – Vue 3 + Vite + Vuetify

A modern, scalable frontend built with Vue 3 (Composition API), Vite, and Vuetify 3.  
Strong emphasis on clean architecture, reusability, and maintainable styling.

---

## Tech Stack

- **Framework:** Vue 3 (Composition API + `<script setup>`)
- **Build Tool:** Vite
- **UI Library:** Vuetify 3 (Material Design 3)
- **State Management:** Pinia
- **Routing:** Vue Router 4
- **HTTP Client:** Axios (wrapped in service modules)
- **Styling:** CSS custom properties, SCSS (for Vuetify overrides), global utilities

---

## Folder Structure
```
src/
|- assets/            # Static assets (images, fonts, etc.)
|     |- css          # Project's global CSS files and Variables
|     |- img          # Images to be shipped with code ( we'll remove these soon )
|- components/        # Reusable UI components
|     |- common/      # Generic, app-agnostic components (AppButton, AppCard, AppBar, AppFooter ...)
|     |- layout/      # Structural components (HeroSection, TieredItems ...)
|     |- view/        # View specific Components (These Components should be made in rare cases
|         |- auth/    # only when layout components aren't Sufficient)
|         |- donate/
|- config/
|     |- types/       # Config type(s) for typescript
|     |- defaults/    # Default configs
|- layouts/           # UI layout that can render multiple views
|     |- TenantLayout.vue
|     |- PublicAdmin.vue
|     |- ...
|- plugins/           # Plugin setup (vuetify, etc.)
|- router/            # Vue Router configuration
|     |- index.js
|     |- public.ts    # Un-authenticated routes
|     |- private.ts   # Authenticated routes
|- services/          # API layer and external integrations
|     |- api.js       # Axios instance + interceptors
|     |- authService.ts
|     |- brandingService.ts
|     |- ...
|- stores/            # Pinia stores (global state management)
|     |- authStore.ts
|     |- brandingStore.ts
|     |- uiStore.ts
|     |- ...
|- views/             # Page‑level components (routed)
|     |- HomeView.vue
|     |- DonateView.vue
|     |- ...
|- App.vue            # Root component (layout shell)
|- main.js            # Application entry point
```

---

## Core Conventions

<!-- TODO: Update Conventions -->


### 1. Component Design
- **Presentational vs. Container**  
  Keep business logic **out** of components. Components should be as “dumb” as possible – receiving props and emitting events.  
- Extract logic into **composables** (`useAuth`, `useItems`, etc.)
- Global state lives in **Pinia stores**.
- API calls are **never** made directly inside a component; always go through a **service**.

### 2. Views (Pages)
A View is a **layout shell** only. It must contain **only**:
- Navigation components (AppBar, Sidebar, etc.)
- A `<router-view />` (or nested router) for the main content area.
- Footer

**Example (HomeView.vue):**
```vue
<template>
  <AppBar />
  <v-main>
    <router-view />
  </v-main>
  <AppFooter />
</template>
```

### 3. Styling & Dark Theme
- All styling follows a design‑token first approach to ensure dark theme support out‑of‑the‑box.
    - styles/variables.css contains all design tokens as CSS custom properties:
    - styles/main.css holds global resets, shared utility classes (e.g., .text-center, .sr-only), and typography foundations.
- Use utility classes before adding component‑scoped styles.
- Prefer Vuetify’s built‑in spacing, typography, and color helpers (class="pa-4 text-h5") over custom CSS.
- styles/vuetify-overrides.scss customizes Vuetify’s SCSS variables to align with the project’s design tokens.
- Component‑scoped styles: Use <style scoped> only when a component requires unique presentation. Always reference CSS variables (var(--color-surface)) instead of hardcoded colors.

### 4. API & Services
- All external communication is handled through dedicated service modules.
- Place Axios configuration, base URL, interceptors, and error handling in services/api.js.
- Create feature‑specific services (e.g., services/userService.js) that only import the Axios instance.
- Never use fetch or axios directly in components or stores.

### 5. State Management (Pinia)
- Stores only orchestrate data: calling services, caching, and exposing reactive state.
- Components read state via store getters/state and dispatch actions; no direct API calls.

6. Routing
- Centralized router in router/index.js.
- Lazy‑load route components for performance.
- Use nested routes where a view acts as a layout shell.

7. Reusability & Generalisation
- Favor generic, composable components (<AppButton>, <AppModal>) over ad‑hoc, one‑off implementations.
- Build utility CSS classes for common patterns (e.g., .flex-center) instead of repeating inline styles.
- Re‑export and reuse Vuetify components with consistent prop defaults when needed.