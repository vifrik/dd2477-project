from github import Github
from github.GithubException import RateLimitExceededException
from time import sleep
import os
from datetime import datetime, timedelta


EXTENSIONS = {
    "Java": "java",
    "Python": "py",
    "JavaScript": "js",
    "C++": "cpp",
    "C": "c",
    "C#": "cs",
}


class Scraper:
    def __init__(
        self,
        token,
        language="Java",
        dates=(datetime.now() - timedelta(days=7), datetime.now()),
        path="data",
    ):
        assert language in EXTENSIONS, "Language not supported"
        assert all(
            (isinstance(date, datetime) for date in dates)
        ), "Dates must be datetime objects"
        assert len(dates) == 2, "Must provide start and end dates"
        assert dates[0] < dates[1], "Start date must be before end date"

        os.makedirs(path, exist_ok=True)

        self.g = Github(token)
        self.path = path
        self.language = language
        self.extension = EXTENSIONS[language]
        self.dates = dates
        self.scraped_repos = set()
        self.scraped_file_count = 0

    def get_repos(self):
        # One week at a time
        start, end = self.dates
        rate_limit = self.g.get_rate_limit()
        while rate_limit.search.remaining > 0:
            try:
                yield self.g.search_repositories(
                    f"language:{self.language} created:{start.isoformat()}..{end.isoformat()}",
                    sort="stars",
                )
                start, end = start - timedelta(days=7), start
            except RateLimitExceededException:
                print("Rate limit exceeded, sleeping for one minute")
                sleep(60)
            finally:
                rate_limit = self.g.get_rate_limit()
                print(f"Rate limit remaining: {rate_limit.search.remaining}")

    # Generate all files in a repo.
    def get_files(self):
        rate_limit = self.g.get_rate_limit()
        while rate_limit.core.remaining > 0:
            try:
                for file in self.repo.get_contents(""):
                    yield from self._get_files(file)
                break
            except RateLimitExceededException:
                print("Rate limit exceeded, sleeping for one hour")
                sleep(60 * 60)
                rate_limit = self.g.get_rate_limit()
                print(f"Rate limit remaining: {rate_limit.core.remaining}")
            except Exception as e:
                print(f"Could not get files: {e}")
                break

    # Step through directories recursively
    def _get_files(self, file):
        if file.type == "dir":
            for f in self.repo.get_contents(file.path):
                yield from self._get_files(f)
        elif file.path.endswith(self.extension):
            yield file

    def get_code(self, file):
        rate_limit = self.g.get_rate_limit()
        if rate_limit.core.remaining > 0:
            try:
                return file.decoded_content
            except Exception as e:
                print(f"Could not get code: {e}")

    def save_file(self, name, content):
        filename = os.path.join(self.path, name)
        base, ext = os.path.splitext(name)
        count = 1
        while os.path.exists(filename):
            # Add a number to the end of clashing filenames
            name = f"{base}_{count}{ext}"
            filename = os.path.join(self.path, name)
            count += 1
        with open(filename, "wb") as f:
            try:
                f.write(content)
                return True
            except Exception as e:
                print(f"Could not write file: {e}")
                return False

    def run(self):
        for repos in self.get_repos():
            for repo in repos:
                self.repo = repo
                if repo.full_name in self.scraped_repos:
                    print(f"Already scraped {repo.full_name}")
                    continue
                print(f"Scraping {repo.full_name}")
                for file in self.get_files():
                    rate_limit = self.g.get_rate_limit()
                    code = self.get_code(file)
                    if code:
                        if self.save_file(file.name, code):
                            self.scraped_file_count += 1
                            if self.scraped_file_count % 100 == 0:
                                print(
                                    f"Saved {self.scraped_file_count} files. (Rate limit remaining: {rate_limit.core.remaining})"
                                )
                self.scraped_repos.add(repo.full_name)


# NOTE: Replace with a valid token
token = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
crawler = Scraper(token)
crawler.run()
