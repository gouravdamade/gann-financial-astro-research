"""Compatibility entry point for the repository-owned corrected TN event generator.

The pre-2026-07-11 implementation imported recovery-only JDML4.py and mixed astronomy,
chart rendering, market labels, and source logging. Git history retains that implementation;
current rebuilds deliberately route through the narrow native generator instead.
"""

from build_corrected_natal_event_source import main


if __name__ == "__main__":
    main()
