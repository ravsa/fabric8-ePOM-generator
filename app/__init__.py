#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Initialize the package app."""

from .git_utils import GitServices
from .boosters import Boosters
from .generate_epom import generate_epom
import logging
import coloredlogs

coloredlogs.install(
    fmt='[%(asctime)s - %(name)s][%(levelname)s]: %(module)s - %(funcName)s - %(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
