from pathlib import Path


def detect_project(repo_path: str) -> dict:
    """
    Detect the technology stack and project type of a repository.
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

    files = {
        file.name.lower()
        for file in path.iterdir()
        if file.is_file()
    }

    technologies = []
    project_type = "Unknown"

    if "pom.xml" in files:
        technologies.extend(["Java", "Maven"])
        project_type = "Java Maven project"

    elif "build.gradle" in files or "build.gradle.kts" in files:
        technologies.extend(["Java", "Gradle"])
        project_type = "Java Gradle project"

    elif (
        "pyproject.toml" in files
        or "requirements.txt" in files
        or "setup.py" in files
    ):
        technologies.append("Python")
        project_type = "Python project"

    elif "package.json" in files:
        technologies.extend(["JavaScript", "Node.js"])
        project_type = "Node.js project"

    elif any(file.endswith(".csproj") for file in files):
        technologies.extend(["C#", ".NET"])
        project_type = ".NET project"

    return {
        "repository": path.name,
        "project_type": project_type,
        "technologies": technologies
    }