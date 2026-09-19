# Pixoria Agent Guide

## Mission

Migrate the Django website from the current raw HTML/CSS templates to the matching Tailwind templates in `Pixoria-tailwind-version/`.

The two template sets represent the same website and should remain behaviorally equivalent. The Tailwind version is the visual base, while working Django behavior from the current templates is the source of truth for data, URLs, forms, conditionals, loops, authentication, and reusable context.

## Project Context

- Framework: Django.
- Active Django templates: `templates/`.
- Tailwind reference templates: `Pixoria-tailwind-version/`.
- Source CSS/JS: `static/`.
- Deployment static output: `public/static/`.
- Deployment media output: `public/media/`.
- SQLite database: `database/db.sqlite3`.
- Django settings: `config/settings.py`.
- 404 handler: `config.views.custom_404`.
- Local Python environment: `venv/`.

Current deployment paths:

```python
STATIC_URL = "/public/static/"
STATIC_ROOT = BASE_DIR / "public" / "static"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/public/media/"
MEDIA_ROOT = BASE_DIR / "public" / "media"
DATABASES["default"]["NAME"] = BASE_DIR / "database" / "db.sqlite3"
```

## Migration Status

- `templates/404.html` has already been migrated to the Tailwind layout.
- `static/css/tailwind.css` and `static/js/tailwind-main.js` were added for the migrated 404 page.
- The 404 page preserves Django URL reversing and uses Django static references.
- `apps/home/migrations/0003_latestarticlessection.py` was added to create the missing `home_latestarticlessection` table.
- The database and media files were moved to their deployment paths.
- The Tailwind source copy of a template must be deleted only after its Django replacement is complete, tested, and committed.

Before starting a new page, inspect the current working tree and recent commits. Do not undo user changes or unrelated work.

## Required Migration Workflow

Perform one page or one coherent feature at a time.

1. Identify the matching raw template in `templates/` and Tailwind reference in `Pixoria-tailwind-version/`.
2. Read both files completely before editing.
3. Inspect the related Django view, URL configuration, models, context processors, partials, forms, and JavaScript dependencies.
4. Write down the behavior inventory from the raw template:
   - Django `{% extends %}`, `{% block %}`, `{% include %}`, `{% load %}`.
   - `{% url %}`, `{% static %}`, `{% csrf_token %}`, conditionals, loops, filters, and variables.
   - Forms, validation states, pagination, empty states, authentication states, and HTMX behavior.
5. Port that behavior into the matching Tailwind markup. Never replace dynamic Django values with hardcoded text or static HTML links.
6. Preserve all working sections. A visual match is not complete if a section, link, form, loop, or state disappears.
7. Keep the Tailwind design and classes from `Pixoria-tailwind-version/` where possible. Add Django tags around them rather than rebuilding the page in the raw CSS style.
8. Use `{% load static %}` and `{% static %}` for assets. Use `{% url %}` for internal links.
9. Preserve responsive behavior and verify desktop and mobile layouts.
10. Add or adapt JavaScript behavior using plain JavaScript only.
11. Run focused checks for the page, then run the broader Django checks.
12. Delete the corresponding source template from `Pixoria-tailwind-version/` only after validation succeeds.
13. Make a short English commit immediately for that completed page or coherent feature.

## UI Rules

### Mobile navigation

The raw HTML/CSS mobile menu is the preferred behavior and interaction model. Recreate its behavior in the Tailwind version, including:

- Open and close controls.
- `aria-expanded` state.
- Close button behavior.
- Closing after selecting a link.
- Body scroll locking while open.
- Accessible labels and keyboard-friendly buttons.
- Responsive visibility at the same breakpoint as the Tailwind layout.

Use plain JavaScript. Do not introduce Alpine.js.

### Manifesto section

The manifesto section from the raw HTML/CSS version is the visual and structural source of truth. Reproduce it exactly in the Tailwind page:

- Keep all content and Django variables.
- Keep the same hierarchy, highlighted word, paragraphs, signature, statistics, and decorative elements.
- Preserve responsive behavior and spacing.
- Use Tailwind classes for styling, but do not omit or simplify working content.

### AOS animations

The project has local AOS assets. Use them consistently for every migrated section, including small supporting blocks where appropriate:

- Keep the local AOS CSS and JavaScript.
- Add `data-aos`, `data-aos-delay`, `data-aos-duration`, `data-aos-offset`, or related attributes intentionally.
- Initialize AOS through plain JavaScript.
- Do not replace AOS with Alpine.js or add a second animation framework.
- Respect reduced-motion preferences where supported.
- Avoid animation attributes that hide content permanently if JavaScript fails.

### Alpine.js removal

Remove Alpine.js from migrated project code:

- Remove Alpine script references from templates and base layouts.
- Remove Alpine directives such as `x-data`, `x-show`, `x-bind`, `x-on`, `@click`, and `:class`.
- Replace each behavior with plain JavaScript and semantic HTML.
- Search the whole project after each related change to confirm no active Alpine usage remains.

Do not remove Alpine-related files blindly until all references are gone and the site has been tested.

## Django Preservation Rules

The Tailwind migration is not an HTML-only replacement. Preserve the complete Django contract:

- All template inheritance and blocks.
- All context variables from views and context processors.
- All model-driven content and loops.
- All URL names and parameters.
- All forms, CSRF protection, errors, success messages, and redirects.
- All authentication and permission branches.
- All media URLs and uploaded files.
- All SEO metadata, canonical URLs, Open Graph data, and structured data.
- All pagination, filters, search, empty states, and 404 behavior.
- All shared header, mobile navigation, footer, CTA, and reusable partial behavior.

If the Tailwind reference omits functionality that exists in the raw template, restore the functionality in the Tailwind version.

## Asset Rules

- Prefer existing local assets and local fonts.
- Do not use relative references such as `src/output.css` or `index.html` in Django templates.
- Use `{% static '...' %}` for CSS, JavaScript, fonts, and images.
- Use `{% url 'namespace:name' %}` for internal navigation.
- Keep source assets in `static/`; run `collectstatic` when deployment output must be refreshed.
- Do not commit generated `__pycache__` files.
- Do not commit unrelated generated output unless the task explicitly requires it.

## Validation Commands

Run commands from the repository root with the project virtual environment:

```powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check
.\venv\Scripts\python.exe manage.py migrate --plan
.\venv\Scripts\python.exe manage.py test
.\venv\Scripts\python.exe manage.py collectstatic --noinput
```

For a page migration, also test the relevant route with Django's test client using an allowed host, for example:

```powershell
.\venv\Scripts\python.exe manage.py shell -c "from django.test import Client; response = Client(HTTP_HOST='127.0.0.1').get('/'); print(response.status_code)"
```

Check both desktop and mobile rendering when a browser or screenshot tool is available. Verify that CSS and JavaScript load from `/public/static/` and media loads from `/public/media/`.

## Commit Contract

Every completed step must have a short English commit. Examples:

```text
Migrate home template to Tailwind
Port mobile navigation behavior
Restore manifesto section
Remove Alpine.js dependencies
Add AOS animations to services
Migrate blog detail template
Remove migrated Tailwind source template
```

Do not combine unrelated pages into one commit. Before committing:

1. Run focused validation.
2. Inspect `git diff` and `git status`.
3. Exclude caches, secrets, local environment files, and unrelated user changes.
4. Commit only the completed step.
5. Report the commit hash and validation result.

## Suggested Migration Order

Use this order unless the current task requires another dependency order:

1. Shared base layout, header, mobile navigation, footer, AOS initialization, and Alpine removal.
2. Home page, including the raw-template manifesto section.
3. Services list and service detail pages.
4. Portfolio/work list and project detail pages.
5. About page.
6. Blog list, blog detail, and blog partials.
7. Contact page and forms.
8. Login and any remaining registration/auth templates.
9. 404 page final review and cleanup of the migrated Tailwind source.
10. Full regression checks, `collectstatic`, responsive review, and deployment checklist.

## Definition of Done

A migration is complete only when all of the following are true:

- The Django template uses the Tailwind design without losing existing behavior.
- No raw-template section or dynamic Django feature is missing.
- Internal links resolve through Django URL names.
- Static and media assets resolve through configured deployment paths.
- Mobile navigation works and matches the preferred raw implementation.
- The manifesto section matches the raw implementation where applicable.
- Alpine.js is not used by the migrated code.
- AOS is applied to the page sections and initialized locally.
- `manage.py check` and focused route tests pass.
- The matching Tailwind source template is deleted only after success.
- The completed work has its own short English commit.
- No generated cache files or unrelated changes are included.

## Instructions For The Next AI

Start by reading this file, checking `git status`, and identifying the next unmigrated template pair. Continue from the current repository state; do not ask the user to repeat the migration requirements. Before editing, inspect the raw and Tailwind versions plus the owning Django view and related partials. Work in small validated steps and commit each completed step using the contract above.
