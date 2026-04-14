from github import Github
import os

class GithubManager:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        if self.token:
            self.g = Github(self.token)
        else:
            self.g = None

    def update_readme(self, repo_name: str, new_content: str, message: str = "Update README with campaign message"):
        if not self.g: return "No token"
        repo = self.g.get_user().get_repo(repo_name)
        contents = repo.get_contents("README.md")
        repo.update_file(contents.path, message, new_content, contents.sha)
        return f"README updated in {repo_name}"

    def create_release(self, repo_name: str, tag: str, name: str, body: str):
        if not self.g: return "No token"
        repo = self.g.get_user().get_repo(repo_name)
        repo.create_git_release(tag, name, body)
        return f"Release {tag} created"
