from github import Github
from github.PaginatedList import PaginatedList
from github.GithubException import RateLimitExceededException
from time import sleep
import os
from datetime import datetime, timezone
import json
from dotenv import load_dotenv
from credentials import token
import requests
from shutil import rmtree
import traceback


EXTENSIONS = {
    "Java": "java",
    "Python": "py",
    "JavaScript": "js",
    "C++": "cpp",
    "C": "c",
    "C#": "cs",
}


class Scraper:
    """
    Scrapes GitHub for files of a given language and saves them to disk.
    """

    def __init__(
        self,
        gh_token=token,
        language="Java",
        peek_endpoint="https://scrape.åt.se/peek",
        fetch_endpoint="https://scrape.åt.se/fetch",
        path="data",
        batch_size=100,
    ):
        """
        Initializes the scraper.

        :param gh_token: GitHub token
        :param language: Language to scrape
        :param peek_endpoint: Endpoint to peek at the number of repos left
        :param fetch_endpoint: Endpoint to fetch a list of repo URLs
        :param path: Path to save the files to
        :param check_for_duplicates: Try to avoid scraping the same repo twice
        :param files_per_run: Number of files to scrape before returning control
        """
        assert language in EXTENSIONS, "Language not supported"
        assert batch_size > 0, "files_per_run must be greater than 0"

        load_dotenv()
        self.username = os.getenv("AUTH_USER")
        self.password = os.getenv("AUTH_PASSWORD")
        assert self.username and self.password, "Username and password not set"

        self.g = Github(gh_token)
        self.path = os.path.join(path, EXTENSIONS[language])
        self.metadata_path = os.path.join(self.path, "metadata.json")
        self.extension = EXTENSIONS[language]
        self.peek_endpoint = peek_endpoint
        self.fetch_endpoint = fetch_endpoint
        self.batch_size = batch_size
        self.scraped_file_count = 0

        self.path_setup()

    def path_setup(self):
        """
        Creates the directory and metadata file if they don't exist.
        """
        os.makedirs(self.path, exist_ok=True)
        try:
            self.metadata_file = open(self.metadata_path, "r+")
            # Remove the closing brace and add a comma
            self.metadata_file.seek(0, 2)
            # Seek back depending on the OS newline character
            if os.linesep == "\r\n":
                self.metadata_file.seek(self.metadata_file.tell() - 3, 0)
            else:
                self.metadata_file.seek(self.metadata_file.tell() - 2, 0)
            self.metadata_file.truncate()
            self.metadata_file.write(",\n")

        except FileNotFoundError:
            with open(self.metadata_path, "w") as f:
                f.write("{\n")
            self.metadata_file = open(self.metadata_path, "r+")
            self.metadata_file.seek(0, 2)

    def close_metadata(self):
        """
        Closes the metadata file.
        """
        self.metadata_file.seek(0, 2)
        if os.linesep == "\r\n":
            self.metadata_file.seek(self.metadata_file.tell() - 3, 0)
        else:
            self.metadata_file.seek(self.metadata_file.tell() - 2, 0)
        self.metadata_file.write("\n}")
        self.metadata_file.close()

    def has_more(self):
        """
        Checks if there are more repos to scrape.
        """
        num_repos = int(
            requests.get(self.peek_endpoint, auth=(self.username, self.password)).text
        )
        return num_repos > 0

    def fetch(self):
        """
        Fetches a list of repos from the server.
        """
        return list(
            requests.get(
                self.fetch_endpoint,
                auth=(self.username, self.password),
            ).json()
        )

    def wait(self):
        """
        Waits until the core rate limit resets.
        """
        reset = self.g.get_rate_limit().core.reset
        delta = (reset - datetime.utcnow()).total_seconds() + 1
        print(f"Rate limit exceeded, sleeping for {delta // 60} minutes")
        sleep(delta)

    def get_repos(self):
        """
        Generates all repos to scrape.
        """
        while self.has_more():
            repo_urls = self.fetch()
            for repo_url in repo_urls:
                parts = repo_url.split("/")
                full_name = parts[-2] + "/" + parts[-1]
                try:
                    yield self.g.get_repo(full_name)
                except RateLimitExceededException:
                    self.wait()
                    yield self.g.get_repo(full_name)
                except Exception as e:
                    print(f"Could not get repo: {e}")

    def get_files(self, repo):
        """
        Generates all files in a repo.
        """
        try:
            contents = repo.get_contents("")
            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(repo.get_contents(file_content.path))
                elif file_content.path.endswith(self.extension):
                    yield file_content
        except RateLimitExceededException:
            self.wait()
            yield from self.get_files(repo)
        except Exception as e:
            print(f"Could not get files: {e}")

    def get_code(self, file):
        """
        Gets the code from a file.
        """
        try:
            return file.decoded_content.decode("utf-8")
        except UnicodeDecodeError:
            return None

    def get_commit_hash(self, repo, file):
        """
        Gets the hash of the latest commit of a file.
        """
        try:
            commit = repo.get_commits(path=file.path)
            if isinstance(commit, PaginatedList):
                commit = commit[0]
            return commit.sha
        except RateLimitExceededException:
            self.wait()
            return self.get_commit_hash(repo, file)

    def save_file(self, name, content, **kwargs):
        """
        Saves a file to disk and writes metadata to metadata.json.
        """
        file_path = os.path.join(self.path, name.lower())
        base, ext = os.path.splitext(name)
        count = 1
        filename = name
        while os.path.exists(file_path):
            # Add a number to the end of clashing filenames
            filename = f"{base}_{count}{ext}"
            file_path = os.path.join(self.path, filename.lower())
            count += 1
        file_path = os.path.join(self.path, filename)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"Could not write file: {e}")
            os.remove(file_path)
            return False
        metadata = {
            "name": name,
            "given_name": filename,
            "timestamp": datetime.now().isoformat(),
        } | kwargs
        try:
            self.metadata_file.write(f'"{filename}": {json.dumps(metadata)},\n')
            return True
        except Exception as e:
            print(f"Could not write metadata: {e}")
            return False

    def run(self):
        """
        Returns a generator that yields the number of scraped files per run.
        """
        try:
            for repo in self.get_repos():
                encoding_errors = 0
                print(f"Scraping {repo.full_name}")
                for file in self.get_files(repo):
                    code = self.get_code(file)
                    if not code:
                        encoding_errors += 1
                        if encoding_errors > 10:
                            print("Too many encoding errors, skipping repo")
                            break
                        continue
                    sha = self.get_commit_hash(repo, file)
                    download_url = f"https://raw.githubusercontent.com/{repo.full_name}/{sha}/{file.path}"
                    if self.save_file(
                        file.name,
                        code,
                        repo=repo.full_name,
                        path=file.path,
                        commit_sha=sha,
                        download_url=download_url,
                    ):
                        self.scraped_file_count += 1
                        if self.scraped_file_count % 100 == 0:
                            print(
                                f"Saved {self.scraped_file_count} files. (Rate limit remaining: {self.g.get_rate_limit().core.remaining})"
                            )
                        if self.scraped_file_count % self.batch_size == 0:
                            self.close_metadata()
                            yield self.batch_size
                            # Clean up before starting a new run
                            rmtree(self.path)
                            self.path_setup()

            # Deal with leftover files from the last run
            self.close_metadata()
            yield self.scraped_file_count % self.batch_size
            rmtree(self.path)

        except:
            print(f"Uncaught exception while scraping:")
            traceback.print_exc()
            if not self.metadata_file.closed:
                if self.metadata_file.tell() < 4:
                    print("Deleting empty metadata file")
                    self.metadata_file.close()
                    os.remove(self.metadata_path)
                else:
                    self.close_metadata()


if __name__ == "__main__":
    scraper = Scraper(batch_size=5)
    for count in scraper.run():
        print(f"Scraped {count} files")
