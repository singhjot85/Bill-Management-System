# Invoice Management Application (Bill Management Application)
A system that can be used to generate and manage bills/invoices. This files contains the norms and conventions followed for backend development of the project.

# Directory Structure
```
project_root/
|- ... other infra files
|- backend/             # All Backend Code
|   |- config           # Backend Project Confiurations
|   |   |- public_routers.py    # Public URL config
|   |   |- routers.py           # Tenant URL config
|   |   |- settings.py          # Django Project Settings
|   |   |- constants.py         # Settings constants to keep settings.py clean
|   |   |- variables.py         # Settings variables to keep settings.py clean
|   |   |- wsgi.py              # Dev Server Configuration
|   |
|   |- apps             # Project Applications
|   |   |- customer_management   # Customer Django App
|   |   |- payments_management   # Payments Django App
|   |   |- service               # External Service Logic
|   |   |- setup                 # Setup App (Shared App)
|   |   |- tenants               # Tenants App (Public App)
|   |   |- utils                 # App level common utility logic
|
|- frontend/            # Frontend code
|- project_templating   # Django Templates and Static Assets
```

# Coding Conventions
Follow these coding conventions when writing and contributing to the project. These are not hard and fast rules, but these are some the practices that should be followed while contributing to the project.

**Clean Code:**
- Keep all the backend project settings and configurations in `backend/config/` directory.
- Try keeping it clean, if anything is becoming messy break into files/sub-directories, Ex:
    - Only constant value's in `backend/config/settings/constants.py`, values that may vary at runtime in `backend/config/settings/variables.py`.
    - As settings could have become messy with variable resolution functions created a `backend/config/settings/resolvers.py`.
    - `backend/config/routers.py` only contain Tenant Level routes, `backend/config/public_routers.py` contain Public routes.
    - `backend/config/settings/settings.py` only does definition, everything get defined in helper files/sub-directories.
- Keep the all the application related logic in `backend/apps` directory.


**URL Patterns:**
- Define all the urls at this base level only, don't break spread out into multiple apps.
- Always use the app_name as `api` for both public and private URLConfig.
- Always try using `router` to register Viewset's, in exterme cases use raw urls.
    - When u already have url's resolved ex: `admin.urls`.
    - When u need to define function based views.
- Use DeafultRouter for deployed envs, we don't want to expose API root view in deplyements.

**Settings:**
- Serve static assets seperately.
- Keep, Tenant and Public url configurations sepereate.

**Views:**
- Always try using DRF viewsets, only in rare use Django Views.
- Always send out serialized data.
- Do not expose direct error message, implemet custom error's to be exposed.
- If using model viewsets, override methods that are not used.
- Block list endpoints if not required, if exposed always use pagination.
- Clean incoming data, if the data isn't valid throw custom errors, and stop API execution.
