#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Generate epom from normal pom."""
from functools import partial
import subprocess
import shlex
import logging
import tempfile
import os

logger = logging.getLogger(__name__)


def run_cmd(cmd):
    process = subprocess.Popen(
        shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        output = process.stdout.readline() or process.stderr.readline()
        if not output and process.poll() is not None:
            break
        if output:
            logger.info(output.strip())
    return process.poll()


def generate_epom(pom):
    """Docstring for generate_epom function."""
    cmd = "mvn -T10 help:effective-pom -f {ipath} -Doutput={opath}"
    tfile = partial(tempfile.NamedTemporaryFile, 'r+b', suffix='.xml')
    with tfile() as ifile, tfile() as ofile:
        ifile.write(pom)
        ifile.flush()
        ifile.seek(0)
        cmd = cmd.format(ipath=ifile.name, opath=ofile.name)
        logger.info('RUNNING CMD: {}'.format(cmd))
        try:
            _status = run_cmd(cmd)
            ofile.seek(0)
            return _status, ofile.read()
        except Exception as e:
            logger.error(
                "Can't Run the command `{}` \n ERROR: {} ".format(cmd, str(e)))


def generate_epom_locally(temp_repo):
    """Docstring for generate_epom_locally function."""
    cmd = "mvn -T10 help:effective-pom -f {ipath} -Doutput={opath}"
    try:
        input_path = os.path.join(temp_repo, 'pom.xml')
        output_path = os.path.join(temp_repo, 'epom.xml')
        open(output_path, 'a').close()
        cmd = cmd.format(ipath=input_path, opath=output_path)
        _status = run_cmd(cmd)
        with open(output_path, 'rb') as _file:
            return _status, _file.read()
    except Exception as exe:
        logger.error(
            "Can't Run the command `{}` \n ERROR: {} ".format(cmd, str(exe)))
