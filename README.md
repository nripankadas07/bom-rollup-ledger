# bom-rollup-ledger

Propagate exact demand through a multilevel CSV BOM, combine shared paths once at each part, and show leaf costs plus an edge-by-edge quantity ledger.

For: Manufacturing and procurement engineers reviewing a multilevel BOM export before a material estimate. Shared subassemblies and decimal quantities make spreadsheet multiplication easy to undercount; a missing leaf price should not silently look like a complete estimate.

## Quickstart

Python 3.10 or newer. No runtime packages or network requests. The initial wheel build needs setuptools from the normal Python package registry.

```sh
git clone https://github.com/nripankadas07/bom-rollup-ledger.git
cd bom-rollup-ledger
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/bom-rollup-ledger example-bom.csv example-costs.csv --root R --quantity 2 --currency USD
```

The synthetic diamond requires 4.6 units of leaf L at unit cost 2.5, producing exact material cost 11.5. JSON includes each propagation contribution.

Windows: use `.venv\Scripts\python.exe` and `.venv\Scripts\bom-rollup-ledger.exe` instead. Windows is documented but has not been executed in this release's Linux CI.

## Input and result contract

Two UTF-8 CSV files with exact headers parent,component,quantity and part,unit_cost. IDs are trimmed, 1..128 printable characters. Quantities are positive decimal strings; prices nonnegative. Plain decimals allow <=12 integer and <=8 fractional digits. All BOM cycles, duplicate edges/prices and assembly prices are rejected. The selected root may be an assembly or a leaf; only reachable leaves contribute. Missing prices yield a known subtotal with total=null. No intermediate rounding; all results use exact rational arithmetic with a 4096-bit budget. At most 5000 rows/file, 2000 parts and 2 MiB/file. Currency is only a three-uppercase-letter label.

Output is JSON on stdout. Exit 0 means complete/no findings; exit 1 means a valid report with missing coverage, prices, capacity, or capture findings, where applicable. SQLite extraction has no exit-1 state. Exit 2 means invalid input or an I/O failure, with an error on stderr and no partial report. `--help` describes command options. Inputs stay local; review output before sharing it.

## Limits

Material-only arithmetic. No live supplier prices, ERP/CAD importer, inventory availability, unit conversion, scrap/yield, substitutions, labor, tax, FX or jurisdiction rules. Unreachable cycles still invalidate the supplied BOM. Unused prices are listed. A complete material total is not a purchase quote or an accounting valuation.

## Verify

```sh
python3 -m unittest -v test_behavior
python3 -m compileall -q .
python3 -m pip wheel --no-deps --wheel-dir dist .
python3 -m venv /tmp/bom-rollup-ledger-check
/tmp/bom-rollup-ledger-check/bin/python -m pip install --no-deps dist/*.whl
python3 verify_installed.py /tmp/bom-rollup-ledger-check/bin/python
```

The installed-command check runs outside the checkout. See [validation](VALIDATION.md), [research and tradeoffs](RESEARCH.md), [contributing](CONTRIBUTING.md), [support](SUPPORT.md) and [security](SECURITY.md).

Original implementation and synthetic fixtures, developed with AI assistance and reviewed through executable checks. MIT license. No customer/adoption claims, copied competitor implementation, or performance-superiority claim.
