from pathlib import Path


IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "target",
    "build",
    "dist",
    "bin",
    "obj",
}


TEST_PATTERNS = {
    "python": ["test_*.py", "*_test.py"],
    "java": ["*Test.java", "*Tests.java", "*TestCase.java"],
    "csharp": ["*Test.cs", "*Tests.cs"],
    "javascript": ["*.test.js", "*.spec.js"],
    "typescript": ["*.test.ts", "*.spec.ts"],
}


def discover_tests(repo_path: str) -> dict:
    """
    Discover test files inside a software repository.
    """

    path = Path(repo_path).resolve()

    if not path.exists():
        return {
            "error": f"Repository does not exist: {repo_path}"
        }

    if not path.is_dir():
        return {
            "error": f"Path is not a directory: {repo_path}"
        }

    tests = []

    for file in path.rglob("*"):

        if not file.is_file():
            continue

        if any(part in IGNORED_DIRECTORIES for part in file.parts):
            continue

        for language, patterns in TEST_PATTERNS.items():

            if any(file.match(pattern) for pattern in patterns):

                tests.append({
                    "file": str(file.relative_to(path)),
                    "language": language
                })

                break

    return {
        "repository": path.name,
        "total_tests": len(tests),
        "tests": tests
    }