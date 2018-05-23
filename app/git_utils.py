#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Github utilities."""
from github import Github, BadCredentialsException, RateLimitExceededException, GithubException
from datetime import datetime
import logging
import os


logger = logging.getLogger(__name__)


class GitServices:
    """Docstring for GitServices."""

    def __init__(self, access_token=None):
        """Docstring for __init__."""
        self.access_token = access_token or os.getenv("GITHUB_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError("Github Access Token not provided")
        self.github_object = Github(self.access_token)
        try:
            self.github_user = self.github_object.get_user().login
        except BadCredentialsException:
            logger.error("Invalid github access token")
        except Exception as e:
            logger.error("An Exception occurred \n {}".format(str(e)))

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

    def is_modified_in_days(self, repo, days=1, org=None):
        """Docstring for get_last_modified_date."""
        if (datetime.now() - self.get_last_modified_date(repo, org)).days <= days:
            return True
        else:
            return False

    def validate_repo(self, url, fetch_repo_only=False):
        """Docstring for validate_repo."""
        logger.info("input repo for validate_repo is {}".format(url))
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
            logger.info(
                "extracted org and repo is `{}` `{}`".format(org, repo))
            if fetch_repo_only:
                return [repo]
            org = org.split(':')[-1]
            return '/'.join([org, repo])

        except Exception as e:
            logger.error(
                'An Exception occurred while validating repo `{}`'.format(str(e)))

    def fetch_file_from_github_release(self, repo=None, filename="pom.xml", ref=None):
        """Return file content from github release."""
        try:
            if repo:
                self.repo = self.github_object.get_repo(self.validate_repo(repo))
            if ref:
                file_content = self.repo.get_file_contents(
                    filename, ref).decoded_content
            else:
                file_content = self.repo.get_file_contents(
                    filename).decoded_content
            return file_content.decode('utf-8')
        except RateLimitExceededException:
            logger.error("Github API rate limit exceeded")
        except BadCredentialsException:
            logger.error("Invalid github access token")
        except GithubException as e:
            logger.error('Github repository or file {} does not exist {}'.format(filename, str(e)))
        except Exception as e:
            logger.error('An Exception occured while fetching file github release {}'
                         .format(str(e)))
