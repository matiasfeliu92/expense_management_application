"""Whitelist of currency codes accounts may be created in."""

import os

# Configurable via env so a deployment can support a different local currency
# without a schema migration — Account.currency is a plain String(3), not a SQLEnum.
SUPPORTED_CURRENCIES = {
    code.strip().upper()
    for code in os.getenv("SUPPORTED_CURRENCIES", "USD,ARS").split(",")
    if code.strip()
}