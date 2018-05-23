#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Generate epom from normal pom."""
from functools import partial
import subprocess
import shlex
import logging
import tempfile

logger = logging.getLogger(__name__)


def generate_epom(pom):
    """Docstring for generate_epom function."""
    cmd = "mvn -T10 help:effective-pom -f {ipath} -Doutput={opath}"
    tfile = partial(tempfile.NamedTemporaryFile, 'r+b', suffix='.xml')
    with tfile() as ifile, tfile() as ofile:
        ifile.write(pom)
        ifile.flush()
        ifile.seek(0)
        cmd = cmd.format(ipath=ifile.name, opath=ofile.name)
        try:
            process = subprocess.Popen(
                shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while True:
                output = process.stdout.readline()
                error = process.stderr.readline()
                if (not output and not error) and process.poll() is not None:
                    break
                if error:
                    logger.error(error.strip())
                if output:
                    logger.info(output.strip())
            return ofile.read()
        except Exception as e:
            logger.error(
                "Can't Run the command `{}` \n ERROR: {} ".format(cmd, str(e)))
