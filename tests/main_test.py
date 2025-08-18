import sys
import pathlib
from typing import List

try:
	import pytest
except Exception:
	print("pytest is required to run tests. Install it via 'uv add pytest' or ensure your env is synced.")
	raise


def _collect_test_dirs(tests_dir: pathlib.Path) -> List[str]:
	# Always include the top-level tests dir
	paths: List[str] = [str(tests_dir)]
	# Include all nested subdirectories to ensure discovery when custom layouts are used
	for sub in sorted(tests_dir.rglob("*")):
		if sub.is_dir():
			paths.append(str(sub))
	return paths


def main() -> int:
	project_root = pathlib.Path(__file__).resolve().parent.parent
	tests_dir = project_root / "tests"
	base_args = _collect_test_dirs(tests_dir)
	extra_args = sys.argv[1:]
	return pytest.main(base_args + extra_args)


if __name__ == "__main__":
	sys.exit(main())
