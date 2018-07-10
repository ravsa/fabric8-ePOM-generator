#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Docstring for run.py."""
from utils import GitServices, AmazonS3, Boosters, generate_epom, generate_epom_locally
import hashlib
import logging
import coloredlogs
import shutil
import glob

coloredlogs.install(
    fmt='[%(asctime)s - %(name)s][%(levelname)s]: %(module)s - %(funcName)s - %(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

delay = __import__('time').sleep

git_service = GitServices()
boosters = Boosters()
s3 = AmazonS3(local_dev=True)
s3.connect()

for repo, ref in boosters:
    if git_service.is_modified_in_days(repo, days=31):
        logger.info("fetching file from {} for ref {}".format(repo, ref))
        content = git_service.fetch_file_from_github_release(
            filename='pom.xml', ref=ref if ref else None)
        hash_obj = hashlib.sha1(content.encode('utf-8')).hexdigest()
        logger.info("hash for content generated {}".format(hash_obj))
        status, epom = generate_epom(content.encode('utf-8'))
        if status == 0:
            logger.info("epom for content generated")
            s3.store_blob(epom, hash_obj)
        else:
            try:
                ref = ref or 'master'
                _repo, content_zip = git_service.clone_repo_from_github_release(
                    repo=repo, ref=ref)
                temp_dir = '/tmp'
                content_zip.extractall(temp_dir)
                dir_name = glob.glob(temp_dir + '/' + _repo + '*')[0]
                logger.info("repo is extracted dir: {}".format(dir_name))
                status, epom = generate_epom_locally(dir_name)
                if status == 0:
                    logger.info("epom for content generated")
                    s3.store_blob(epom, hash_obj)
                else:
                    logger.info("Unable to generate_epom for {}".format(dir_name))
            except Exception as exc:
                logger.error(exc)
            finally:
                shutil.rmtree(dir_name)
                logger.info("repo {} is removed".format(dir_name))
    delay(2)
