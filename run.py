#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Docstring for run.py."""
from utils import GitServices, AmazonS3, Boosters, generate_epom
import hashlib
import logging
import coloredlogs

coloredlogs.install(
    fmt='[%(asctime)s - %(name)s][%(levelname)s]: %(module)s - %(funcName)s - %(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
    delay(2)
