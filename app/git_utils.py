"""Github utility functions."""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from github import GithubException, Github, BadCredentialsException
from datetime import datetime
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a logging format
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '[%(asctime)s - %(name)s]: %(module)s - %(funcName)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class GitServices:
    """Docstring for GitServices."""

    def __init__(self, access_token):
        """Docstring for __init__."""
        self.access_token = access_token
        self.github_object = Github(self.access_token)
        try:
            self.github_user = self.github_object.get_user().login
        except BadCredentialsException:
            logger.error("Invalid github access token")

    def get_last_modified_date(self, repo, org=None):
        """Docstring for get_last_modified_date."""
        if org:
            input_repo = '/'.join([org, self.validate_repo(repo,
                                                           fetch_repo_only=True)])
        else:
            input_repo = self.validate_repo(repo)
        self.repo = self.github_object.get_repo(input_repo)
        logger.info("fetching details for Github Repository {}".format(
            self.repo.archive_url))
        return datetime.strptime(self.repo.last_modified, "%a, %d %b %Y %H:%M:%S GMT")

    def is_modified_in_days(self, repo, day=1, org=None):
        """Docstring for get_last_modified_date."""
        if (datetime.now() - self.get_last_modified_date(repo, org)).days <= day:
            return True
        else:
            return False

    def validate_repo(self, url, fetch_repo_only=False):
        """Docstring for validate_repo."""
        try:
            if not url:
                raise ValueError('Not a valid Repository "{}"'.format(url))

            if url.endswith('.git'):
                url = url[:-len('.git')]
            _temp = url.split('/')
            if len(_temp) == 1:
                # look into the user Github Space if only repo name provided.
                return '/'.join([self.github_user] + _temp)
            org, repo = _temp[-2:]

            if fetch_repo_only:
                return [repo]

            org = org.split(':')[-1]
            return '/'.join([org, repo])

        except Exception as e:
            logger.error(
                'An Exception occured while validating repo `{}`'.format(str(e)))
