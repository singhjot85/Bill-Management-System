# BMA Taste & Animation Rules — UI Polish & Craft Guidelines

This document distills design engineering principles (from `taste-skill` and `emilkowalski/skills`) to avoid typical "generic AI-generated UI" styles and add professional polish.

---

## 1. Animation Decision Framework

Before planning any transition or animation, apply this checklist:

### A. Frequency & Decision
* **100+ times/day** (keyboard shortcuts, command palette toggle, general navigation): **No animation. Ever.** 
* **Tens of times/day** (hover effects, list item clicks): Remove or drastically reduce.
* **Occasional** (modals, drawers, toast alerts): Standard animation (under 300ms).
* **Rare/First-time** (onboarding celebrations): Deliberate, smooth animations.

### B. Easing & Curves
* **Never use ease-in** for UI animations (it starts slow and feels sluggish).
* **Use ease-out** for elements entering the screen (starts fast and feels responsive).
* **Use ease-in-out** for elements moving/morphing on screen.
* **Preferred Custom Curves**:
  ```css
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);     /* Snappy UI ease-out */
  --ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);   /* iOS-like smooth slide */
  ```
* **Vuetify Defaults**: Prefer Vuetify's built-in transition curves (props or classes) over custom keyframes unless special micro-interactions are required.

### C. Duration
* Button press feedback: **100–160ms** (e.g., scale down to `0.97` on press).
* Tooltips & popovers: **125–200ms**.
* Dropdowns & selects: **150–250ms**.
* Modals & drawers: **200–350ms**.

---

## 2. Aesthetics & UI "Tells" to Avoid

To prevent generic looking AI mockups, adhere strictly to these rules:

### A. Color & Visuals
* **No Pure Black**: Avoid `#000000`. Use off-black, zinc-950, or dark charcoal.
* **No Neon Glows**: Avoid neon shadows or bright outer glows by default. Prefer subtle tinted shadows or double inner borders.
* **Desaturate Accents**: Blend primary accents with neutral backgrounds. No oversaturated colors.
* **Ration the Middle Dot (`·`)**: Do not use it as a default separator for everything. Maximum one dot per metadata line.

### B. Typography & Layout
* **No Oversized H1s**: Control typography hierarchy using font-weights and muted colors rather than raw scale.
* **Mathematical Alignment**: Paddings, margins, and border radii must match standard tokens (e.g. `--spacing-md`, `--radius-md`).
* **Asymmetric Grid over 3-Cards Row**: Avoid the default "three identical cards in a row" feature layout. Use asymmetric grids, scroll-pinned columns, or alternate structures.
* **No Rotated Text / Crosshair Hairlines**: Avoid rotating text 90 degrees or drawing random hairline lines for "decoration" unless they group real content.

### C. Content & Data
* **No Generic Names**: Avoid "John Doe" or "Jane Doe". Use realistic names.
* **No Fake-Perfect Numbers**: Avoid `100%`, `50%`, `12345`. Use organic numbers like `47.2%`.
* **No Generic Brand Names / Verbs**: Avoid "Acme", "Nexus", or filler verbs like "Elevate", "Seamless", "Unleash". Use clear, concrete nouns and verbs.
* **No Div-Based Screenshots**: Do not build mock dashboard panels out of colored `<div>` boxes to simulate a product screen. Use real placeholder SVGs or actual layout components.
