# forge-audit

Read-only multi-forge topology and sync-drift auditor.

Inventories repos from a forge (`gh` in v0.1; `tea`/`glab` planned) and compares
two inventories to report repos missing or behind in the mirror.

## Usage

```bash
python -m forge_audit list gh --org hummbl-io -o gh.json
python -m forge_audit drift gh.json gitea.json
```

## License

MIT.
