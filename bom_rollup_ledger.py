"""Exact leaf-material rollups for a bounded, explicit CSV BOM."""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from collections import defaultdict, deque
from fractions import Fraction
from pathlib import Path

MAX_BYTES = 2 * 1024 * 1024


def amount(value: str, *, positive: bool = False) -> Fraction:
    if not isinstance(value, str) or not re.fullmatch(r"\d{1,12}(?:\.\d{1,8})?", value):
        raise ValueError("amounts must be plain decimal strings: <=12 integer, <=8 fraction digits")
    result = Fraction(value)
    if positive and result <= 0:
        raise ValueError("quantity must be positive")
    return result


def exact(value: Fraction) -> str:
    if value.numerator.bit_length() > 4096 or value.denominator.bit_length() > 4096:
        raise ValueError("rollup exceeds the 4096-bit exact arithmetic budget")
    n, d = value.numerator, value.denominator
    sign = "-" if n < 0 else ""
    n = abs(n)
    whole, rem = divmod(n, d)
    if not rem:
        return sign + str(whole)
    digits = []
    while rem:
        rem *= 10
        digit, rem = divmod(rem, d)
        digits.append(str(digit))
        if len(digits) > 4096:
            raise ValueError("decimal output exceeds 4096 digits")
    return sign + str(whole) + "." + "".join(digits)


def identity(value: str) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= 128 or not value.isprintable():
        raise ValueError("part IDs must contain 1..128 printable characters")
    return value


def rows(text: str, header: list[str]) -> list[dict[str, str]]:
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise ValueError("CSV exceeds 2 MiB")
    reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
    if reader.fieldnames != header:
        raise ValueError("expected CSV header: " + ",".join(header))
    result = []
    for row in reader:
        if len(result) >= 5000 or None in row or any(v is None for v in row.values()):
            raise ValueError("CSV row limit or column count violated")
        result.append({k: v.strip() for k, v in row.items()})
    return result


def analyze(bom_csv: str, costs_csv: str, root: str, quantity: str = "1", currency: str = "USD") -> dict:
    identity(root)
    demand = amount(quantity, positive=True)
    if not isinstance(currency, str) or not re.fullmatch(r"[A-Z]{3}", currency):
        raise ValueError("currency is a caller-supplied three-letter label; no FX conversion")
    children: dict[str, dict[str, Fraction]] = defaultdict(dict)
    parts = {root}
    edges = []
    for row in rows(bom_csv, ["parent", "component", "quantity"]):
        parent, child = identity(row["parent"]), identity(row["component"])
        if child in children[parent]:
            raise ValueError("duplicate parent/component edge")
        qty = amount(row["quantity"], positive=True)
        children[parent][child] = qty
        parts.update((parent, child))
        edges.append((parent, child, qty))
    prices = {}
    for row in rows(costs_csv, ["part", "unit_cost"]):
        part = identity(row["part"])
        if part in prices:
            raise ValueError("duplicate part price")
        prices[part] = amount(row["unit_cost"])
        parts.add(part)
    if len(parts) > 2000:
        raise ValueError("at most 2000 distinct parts")
    if root not in prices and not any(root in (p, c) for p, c, _ in edges):
        raise ValueError("root is absent from BOM parents and prices")
    if set(children) & set(prices):
        raise ValueError("prices are for leaves only; assembly prices would double count")
    indegree = {p: 0 for p in parts}
    for parent, child, _ in edges:
        indegree[child] += 1
    queue = deque(sorted(p for p, n in indegree.items() if not n))
    order = []
    while queue:
        p = queue.popleft()
        order.append(p)
        for c in sorted(children.get(p, {})):
            indegree[c] -= 1
            if not indegree[c]:
                queue.append(c)
    if len(order) != len(parts):
        raise ValueError("BOM has a cycle; no partial rollup is issued")
    needed = defaultdict(Fraction, {root: demand})
    propagation = []
    for p in order:
        if not needed[p]:
            continue
        for c, q in sorted(children.get(p, {}).items()):
            contribution = needed[p] * q
            exact(contribution)
            needed[c] += contribution
            propagation.append({"parent": p, "component": c, "per_parent": exact(q),
                                "parent_demand": exact(needed[p]), "contribution": exact(contribution)})
    leaves = []
    subtotal = Fraction()
    missing = []
    for p in sorted(needed):
        if not needed[p] or children.get(p):
            continue
        price = prices.get(p)
        cost = needed[p] * price if price is not None else None
        if cost is None:
            missing.append(p)
        else:
            subtotal += cost
        leaves.append({"part": p, "quantity": exact(needed[p]),
                       "unit_cost": exact(price) if price is not None else None,
                       "extended_cost": exact(cost) if cost is not None else None})
    return {"root": root, "root_quantity": exact(demand), "currency_label": currency,
            "complete": not missing, "missing_prices": missing, "leaves": leaves,
            "known_material_subtotal": exact(subtotal), "total_material_cost": exact(subtotal) if not missing else None,
            "propagation": propagation, "unused_prices": sorted(set(prices) - {x["part"] for x in leaves})}


def read(path: str) -> str:
    with Path(path).open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("file exceeds 2 MiB")
    return data.decode("utf-8-sig")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("bom", help="CSV: parent,component,quantity")
    p.add_argument("costs", help="CSV: part,unit_cost")
    p.add_argument("--root", required=True)
    p.add_argument("--quantity", default="1")
    p.add_argument("--currency", default="USD")
    a = p.parse_args()
    try:
        result = analyze(read(a.bom), read(a.costs), a.root, a.quantity, a.currency)
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0 if result["complete"] else 1
    except (ValueError, OSError, UnicodeError, csv.Error, OverflowError) as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
