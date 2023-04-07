from github import Github
import numpy as np
from github.GithubException import RateLimitExceededException
import os
from dotenv import load_dotenv


def approximate_repos_with_stars(stars):
    """Approximates the number of repos with a number of stars using an exponential curve.
    The parameters of the curve were found by using `fit_exponential_curve`."""
    return 238015 * stars**-1.61190


def fit_exponential_curve():
    """Fits an exponential curve to the data."""
    load_dotenv()
    token = os.getenv("GH_TOKEN")
    if token is None:
        raise ValueError("Please set the GH_TOKEN environment variable")
    g = Github(token)
    data = np.zeros((30, 2))  # 30 requests/minute
    for i in range(100, 3000, 100):
        repos = g.search_repositories(f"language:Java stars:{i}")
        data[i // 100][0] = i
        try:
            data[i // 100][1] = repos.totalCount
        except RateLimitExceededException as e:
            print("Could not get enough data, please wait one minute")
            return

    data = data[data[:, 1] != 0]

    # Fit an exponential curve to the data
    fit = np.polyfit(np.log(data[:, 0]), np.log(data[:, 1]), 1)
    return np.exp(fit[1]), fit[0]


fit_exponential_curve()
