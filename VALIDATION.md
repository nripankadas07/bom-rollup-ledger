# Validation

Acceptance contract: Shared diamond propagation yields 4.6 leaf units and an exact 11.5 subtotal for the synthetic two-unit root; missing prices withhold the total; cycles fail; deep chains do not require Python recursion.

The behavior suite has 19 test methods; this includes meaningful malformed-input cases. CI executes unit tests, Python compilation, wheel build and a new-environment installed-console-command check on Linux/Python 3.10, 3.12 and 3.14. A configured workflow is not proof it passed: inspect this repository's current Actions run before making a health claim.

Preparation: all behavior tests passed on Python 3.12.14. Clean wheel/CLI evidence is recorded in `PREPARATION.json` after execution. Future security advisories, all possible inputs and Windows/macOS behavior are not certified by these checks. No performance benchmark or production-use evidence is claimed.
