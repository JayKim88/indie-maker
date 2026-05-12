# schemas/

JSON Schema definitions for indie-maker harness state files.

## Files

| File | Purpose |
|------|---------|
| `indie-sprint.schema.json` | Schema for `projects/{name}/.indie-sprint.json` — per-project sprint state |
| `example.indie-sprint.json` | Annotated example of a mid-sprint project state |

## Editor support

To get IntelliSense/validation in VS Code, each `.indie-sprint.json` file in `projects/{name}/` should reference the schema:

```json
{
  "$schema": "../../schemas/indie-sprint.schema.json",
  ...
}
```

Or configure VS Code globally via `.vscode/settings.json`:

```json
{
  "json.schemas": [
    {
      "fileMatch": ["**/.indie-sprint.json"],
      "url": "./schemas/indie-sprint.schema.json"
    }
  ]
}
```

## Validation (CLI)

```bash
npx ajv-cli validate -s schemas/indie-sprint.schema.json -d projects/{name}/.indie-sprint.json
```

## Updating the schema

When adding fields:
1. Update `indie-sprint.schema.json` (add property + description + type).
2. Update `example.indie-sprint.json` (show the field in context).
3. Mark whether the field is `[DERIVED]` (computed by hook) or stored.
4. Update any hooks in `bin/` that read/write the file.
