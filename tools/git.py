from pathlib import Path
import subprocess


def run_git_command(repo_path: str, *args: str) -> str:
    """
    Run a Git command inside a repository.
    """

    path = Path(repo_path).resolve()

    if not path.exists():
        return f"Repository does not exist: {repo_path}"

    if not path.is_dir():
        return f"Path is not a directory: {repo_path}"

    git_directory = path / ".git"

    if not git_directory.exists():
        return "Error: This directory is not a Git repository."

    try:
        result = subprocess.run(
            ["git", *args],
            cwd=path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30
        )

        if result.returncode != 0:
            return f"Git error:\n{result.stderr.strip()}"

        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        return "Error: Git command timed out."

    except OSError as e:
        return f"Error running Git: {e}"


def git_status(repo_path: str) -> str:
    """
    Return the current Git status of a repository.
    """

    return run_git_command(
        repo_path,
        "status",
        "--short"
    )


def git_log(repo_path: str, limit: int = 10) -> str:
    """
    Return recent Git commits.
    """

    if limit < 1:
        return "Error: limit must be at least 1."

    if limit > 50:
        limit = 50

    return run_git_command(
        repo_path,
        "log",
        f"-{limit}",
        "--oneline"
    )


def git_diff(repo_path: str) -> str:
    """
    Return the current uncommitted Git diff.
    """

    return run_git_command(
        repo_path,
        "diff"
    )