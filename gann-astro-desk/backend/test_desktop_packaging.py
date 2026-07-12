from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from repository import DataPaths


class DesktopPackagingTests(unittest.TestCase):
    def test_default_paths_respect_packaged_environment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            annotation = root / "state" / "annotations.sqlite"
            with patch.dict(
                os.environ,
                {
                    "GANN_ASTRO_PROJECT_ROOT": str(root),
                    "GANN_ASTRO_ANNOTATION_DB": str(annotation),
                    "GANN_ASTRO_ARTIFACTS_DIR": str(root / "artifacts"),
                },
                clear=False,
            ):
                paths = DataPaths.default()
        self.assertEqual(paths.project_root, root)
        self.assertEqual(paths.annotation_db, annotation)
        self.assertEqual(paths.artifacts_dir, root / "artifacts")
        self.assertEqual(paths.source_events.parent, root)


if __name__ == "__main__":
    unittest.main()
