from mcp.server import MCPServer

from tools.repository import (
    analyze_repository,
    get_project_structure,
    search_code,
    read_file,
)

from tools.git import (
    git_status,
    git_log,
    git_diff,
)

from tools.testing import discover_tests

from tools.project import detect_project

mcp = MCPServer("DevIntel")


@mcp.tool()
def analyze_repo(repo_path: str) -> dict:
    """Analyze a software repository."""
    return analyze_repository(repo_path)


@mcp.tool()
def project_structure(repo_path: str) -> str:
    """Get the directory structure of a software repository."""
    return get_project_structure(repo_path)


@mcp.tool()
def search_repository(repo_path: str, query: str) -> list[dict]:
    """Search for a text query inside repository source files."""
    return search_code(repo_path, query)


@mcp.tool()
def read_repository_file(repo_path: str, file_path: str) -> str:
    """Read a text file from a software repository."""
    return read_file(repo_path, file_path)


@mcp.tool()
def repository_git_status(repo_path: str) -> str:
    """Return the current Git status of a repository."""
    return git_status(repo_path)


@mcp.tool()
def repository_git_log(repo_path: str, limit: int = 10) -> str:
    """Return recent Git commits."""
    return git_log(repo_path, limit)


@mcp.tool()
def repository_git_diff(repo_path: str) -> str:
    """Return the current uncommitted Git diff."""
    return git_diff(repo_path)


@mcp.tool()
def repository_tests(repo_path: str) -> dict:
    """Discover test files in a software repository."""
    return discover_tests(repo_path)


@mcp.tool()
def project_info(repo_path: str) -> dict:
    """Detect the technology stack and project type."""
    return detect_project(repo_path)



if __name__ == "__main__":
    mcp.run()