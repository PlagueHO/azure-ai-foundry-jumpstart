"""
Compatibility namespace for tests importing `src.data_generator`.

The real implementation lives under `src/tools/python/data_generator`.
This package extends its __path__ to include that location so imports like
`from src.data_generator.tools import insurance_claim` work without modifying
the project layout.
"""

from __future__ import annotations

from pathlib import Path

# Current package dir: <repo>/src/data_generator
_pkg_dir = Path(__file__).resolve().parent
# Sibling tools path: <repo>/src/tools/python/data_generator
_real_pkg = _pkg_dir.parent / "tools" / "python" / "data_generator"

# Make this a namespace-style package that also searches the real location.
if _real_pkg.exists():
	__path__ = [str(_pkg_dir), str(_real_pkg)]  # type: ignore[assignment]

__all__: list[str] = []
