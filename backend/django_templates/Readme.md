# Project Templating (Legacy)

This directory contains the original UI infrastructure using Django Templates.

## Overview
Earlier in the project's development, the UI was rendered using Django's built-in templating system. However, as requirements grew more complex, we shifted to a decoupled frontend using **Vue 3 + Vite + Vuetify**.

## Directory Structure
```
project_templating/
    static/             # Static assets (CSS, JS, Images)
        css/
        js/
        images/
        vendor/
    templates/          # Django HTML Templates
        base/
        components/
        views/
        partials/
        include/
```

## Status
This approach is currently **deprecated** in favor of the Vue-based SPA found in the `frontend/` directory. These files are kept for reference or for parts of the system that might still utilize server-side rendering.
