"""forge-audit CLI.

    python -m forge_audit list gh --org hummbl-io -o gh.json
    python -m forge_audit drift gh.json gitea.json
"""

import argparse
import json
import subprocess
import sys


def _gh_inventory(org: str) -> dict[str, str]:
    """Read-only repo inventory via `gh`. Requires gh auth."""
    proc = subprocess.run(
        ["gh", "api", f"orgs/{org}/repos?per_page=100", "--paginate",
         "--jq", '.[] | "\(.name)\t\(.pushed_at)"'],
        capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        return {}
    inv: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        name, _, pushed = line.partition("\t")
        if name and pushed:
            inv[name] = pushed
    return inv


def cmd_list(args) -> int:
    if args.forge != "gh":
        print(f"forge '{args.forge}' not yet supported (gh only in v0.1)", file=sys.stderr)
        return 2
    inv = _gh_inventory(args.org)
    text = json.dumps(inv, indent=2, sort_keys=True)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"wrote {len(inv)} repos -> {args.out}")
    else:
        print(text)
    return 0


def cmd_drift(args) -> int:
    from .inventory import drift, load_inventory, summarize
    print(summarize(drift(load_inventory(args.primary), load_inventory(args.mirror))))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="forge-audit", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    l = sub.add_parser("list", help="inventory a forge's repos")
    l.add_argument("forge", choices=["gh"])
    l.add_argument("--org", required=True)
    l.add_argument("-o", "--out")
    l.set_defaults(fn=cmd_list)

    d = sub.add_parser("drift", help="compare two saved inventories")
    d.add_argument("primary")
    d.add_argument("mirror")
    d.set_defaults(fn=cmd_drift)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
