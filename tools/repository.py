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


IGNORED_EXTENSIONS = {
    ".pyc",
    ".pyd",
    ".dll",
    ".exe",
}


def analyze_repository(repo_path: str) -> dict:
    """
    Analyze a software repository and return basic statistics.
    """

    path = Path(repo_path)

    if not path.exists():
        return {
            "error": f"Repository does not exist: {repo_path}"
        }

    if not path.is_dir():
        return {
            "error": f"Path is not a directory: {repo_path}"
        }

    files = []
    directories = []

    for item in path.rglob("*"):

        if any(part in IGNORED_DIRECTORIES for part in item.parts):
            continue

        if item.is_file():

            if item.suffix.lower() in IGNORED_EXTENSIONS:
                continue

            files.append(item)

        elif item.is_dir():
            directories.append(item)

    extensions = {}

    for file in files:

        extension = file.suffix.lower()

        if extension:
            extensions[extension] = extensions.get(extension, 0) + 1
        else:
            extensions["no_extension"] = extensions.get(
                "no_extension", 0
            ) + 1

    return {
        "repository": path.name,
        "path": str(path),
        "total_files": len(files),
        "total_directories": len(directories),
        "file_types": extensions,
    }
    
def get_project_structure(repo_path: str) -> str:
    """
    Return the directory structure of a software repository.
    """

    path = Path(repo_path)

    if not path.exists():
        return f"Repository does not exist: {repo_path}"

    if not path.is_dir():
        return f"Path is not a directory: {repo_path}"

    lines = [f"{path.name}/"]

    for item in sorted(path.rglob("*")):

        if any(part in IGNORED_DIRECTORIES for part in item.parts):
            continue

        relative_path = item.relative_to(path)

        depth = len(relative_path.parts) - 1

        prefix = "    " * depth

        if item.is_dir():
            lines.append(f"{prefix}├── {item.name}/")

        elif item.is_file():

            if item.suffix.lower() in IGNORED_EXTENSIONS:
                continue

            lines.append(f"{prefix}├── {item.name}")

    return "\n".join(lines)

def search_code(repo_path: str, query: str) -> list[dict]:
    """
    Search for a text query inside source files of a repository.
    """

    path = Path(repo_path)

    if not path.exists():
        return [{"error": f"Repository does not exist: {repo_path}"}]

    if not path.is_dir():
        return [{"error": f"Path is not a directory: {repo_path}"}]

    results = []

    for file in path.rglob("*"):

        if not file.is_file():
            continue

        if any(part in IGNORED_DIRECTORIES for part in file.parts):
            continue

        if file.suffix.lower() in IGNORED_EXTENSIONS:
            continue

        try:
            content = file.read_text(encoding="utf-8")

        except (UnicodeDecodeError, OSError):
            continue

        for line_number, line in enumerate(content.splitlines(), start=1):

            if query.lower() in line.lower():

                results.append({
                    "file": str(file.relative_to(path)),
                    "line": line_number,
                    "content": line.strip()
                })

    return results

def read_file(repo_path: str, file_path: str) -> str:
    """
    Read a file from a repository safely.
    """

    repository = Path(repo_path).resolve()
    target_file = (repository / file_path).resolve()

    # Prevent reading files outside the repository
    try:
        target_file.relative_to(repository)
    except ValueError:
        return "Error: File is outside the repository."

    if not target_file.exists():
        return f"File does not exist: {file_path}"

    if not target_file.is_file():
        return f"Path is not a file: {file_path}"

    if target_file.suffix.lower() in IGNORED_EXTENSIONS:
        return f"File type is not supported: {file_path}"

    try:
        return target_file.read_text(encoding="utf-8")

    except UnicodeDecodeError:
        return "Error: File is not a UTF-8 text file."

    except OSError as e:
        return f"Error reading file: {e}"