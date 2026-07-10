# BMA Frontend Conventions Reference

This document summarizes the coding conventions and architectural patterns to enforce during frontend design and implementation.

---

## 1. Directory Structure

All frontend source code resides under `frontend/src/` and conforms to these boundaries:
* `assets/css/variables.css` — Global CSS variables and tokens. Avoid custom CSS variables elsewhere.
* `components/common/` — Generic, extremely dumb, app-agnostic UI pieces (`AppButton`, `AppCard`, etc.). No business logic, no layout positioning, highly configurable.
* `components/layout/` — Structural blocks combining common components (`HeroSection`, `TieredItems`, etc.). Configures positioning and sizing.
* `components/view/` — View-specific components used only in rare circumstances (like complex forms). Grouped by parent view name.
* `config/types/` — TypeScript interfaces for configuration data.
* `config/defaults/` — Fallback configurations used before backend data loads.
* `layouts/` — Root layout shells (e.g., `TenantLayout.vue`, `PublicLayout.vue`).
* `services/` — Dedicated HTTP modules using Axios wrapper (`services/api.js`). No direct `fetch` or `axios` in components/stores.
* `stores/` — Pinia stores (orchestrate service calls and reactive state). No direct backend logic in views/components.
* `views/` — Page-level components handling route states, config binding, and business logic.

---

## 2. CSS & Styling Priorities

Never write ad-hoc CSS unless absolutely required. Check styles against this priority order:
1. **Vuetify utility classes** (spacing, flex, colors, typography: e.g. `d-flex`, `pa-4`, `text-h5`, `mb-2`).
2. **Vuetify component props** (outlined, dense, elevation, etc.).
3. **Global SCSS/CSS variables** overridden in `variables.css`.
4. **Scoped CSS** (`<style scoped>`) — strictly reserved for complex animations or brand gradients.

*Always guarantee dark theme support using CSS custom properties (design tokens).*

---

## 3. Design and Coding Rules

* **Images**: Avoid image assets. Use icons wherever possible. If an image is necessary, load it dynamically from a static URL; do not commit it to repository source code.
* **Component Design**: Make components highly configurable with properties. Avoid hardcoding text or styles inside children.
* **No Business Logic in UI Components**: UI components must only render config and emit events. The parent View handles all business logic, store updates, and service orchestration.
