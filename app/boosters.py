"""Collect boosters from booster catalog."""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from io import BytesIO
from requests import get
import zipfile
import yaml
import os
import logging


logger = logging.getLogger(__name__)


class Boosters:
    """Docstring for Boosters class."""

    def __init__(self):
        """Docstring for __init__ method."""
        catalog_url = '/'.join([os.getenv("BOOSTER_CATALOG",
                                          ''), "archive/master.zip"])
        self.resp = get(catalog_url, stream=True)
        if self.resp.status_code != 200:
            logger.error("Unable to access url {} \n STATUS_CODE={}".format(
                catalog_url, self.resp.status_code))
        else:
            logger.info("successfully fetched booster catalog")
            self._zip = zipfile.ZipFile(BytesIO(self.resp.content))

    def __iter__(self):
        """Docstring for __iter__ method."""
        for _file in self._zip.infolist():
            if str(_file).find('booster.yaml') != -1 or str(_file).find('common.yaml') != -1:
                with self._zip.open(_file) as yaml_file:
                    data = yaml.safe_load(yaml_file)
                    source = data.get("source", {})
                    git = source.get('git', {})
                    env = data.get('environment', {})
                    url = git.get('url')
                    if url:
                        for item in env.values():
                            _source = item.get('source', {})
                            _git = _source.get('git', {})
                            _ref = _git.get('ref')
                            yield (url, _ref)
                        ref = git.get('ref')
                        yield (url, ref)
