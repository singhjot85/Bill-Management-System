## Devlopment Setup

- Generate latest lock file: `poetry lock`
- Install dependencies in a virtualenv for reference: `poetry install`
    - If `poetry install` fails u need to install `cairo`, `pkg-config`, `cmake` additionally for `pycairo`.
    - These are system packages and poetry cannot install them directly, u can use brew to install them.
    - `brew install cairo pkg-config cmake`.
- For easier devlopment in your IDE, install `Pylance` extension and give your virtualenv's reference to pylance.
```json
{
    "python.defaultInterpreterPath": "<venv_path>/bin/python",
    "python.terminal.activateEnvironment": true,
}
```
> You can also try: `make setup`, this will do all the dev setup

Addditional System dependencies:
- dependencies for weasyprint: `brew install cairo pango gdk-pixbuf libffi`
- dependencies for xhtml2pdf: `brew install cairo pkg-config`


## UI Infra
UI is currently rendered through django templates, a brief on the infra
```
project_templating/
    static/
        css/
        js/
        images/
        vendor/
    templates/
        base/
        components/
        views/
        partials/
        include/
```
