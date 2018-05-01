# -*- coding: utf-8 -*-

import click
import logging
import sys
import atexit
import textwrap
import os
import hashlib
import functools

from ._version import VERSION

def exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    click.echo("Uncaught exception: {0}: {1}".format(str(exc_value.__class__.__name__), str(exc_value)), sys.stdout.isatty())

sys.excepthook = exception_handler

def estimate_hash(fname):
    return os.path.getsize(fname)

def file_hash(fname, update_cb=lambda x: x):
    hash = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            update_cb(len(chunk))
            hash.update(chunk)
    return hash.hexdigest()


def estimate_name_size(fname):
    return 1

def file_name_size(fname, update_cb=lambda x: x):
    update_cb(1)
    return os.path.basename(fname), os.path.getsize(fname)

def list_files(base, estimator=None):
    def handle_walk_error(err):
        raise err

    for path, _, files in os.walk(base, onerror=handle_walk_error):
        for filename in files:
            filepath = os.path.join(path, filename)
            estimation = estimator(filepath) if estimator else 0
            yield (filepath, estimation)

def find_missing_files(source_filelist, target_filelist, fingerprinter):
    lookup_table = {}
    for filepath in target_filelist:
        fingerprint = fingerprinter(filepath)
        lookup_table[fingerprint] = filepath

    mapped_files = []
    missing_files = []
    for filepath in source_filelist:
        fingerprint = fingerprinter(filepath)

        if fingerprint in lookup_table:
            mapped_files.append((filepath, lookup_table[fingerprint]))
        else:
            missing_files.append(filepath)

    return mapped_files, missing_files

@click.command(help="""Lists all files that are contained in directory SOURCE and that
    are not present in directory TARGET. The search includes files in any subdirectory. This tool
    identifies identical files by sha256 hashes (default) or base on filename and -size.""")
@click.option("--batch", "-b", is_flag=True,  help="""Enables raw text output. Enabled by default if using a non-interactive output stream.""") 
@click.option("--quick", "-q", is_flag=True, help="Compare files by name and size instead of sha256 hash.")
@click.option("--verbose", "-v", is_flag=True, help="Additionaly output all mapped files.")
@click.argument("source")
@click.argument("target")
@click.version_option(version=VERSION)
def cli(batch, quick, verbose, source, target):
    if not sys.stdout.isatty():
        batch = True

    if quick:
        estimator = estimate_name_size
        fingerprinter = file_name_size
    else:
        estimator = estimate_hash
        fingerprinter = file_hash

    source_files = list_files(source, estimator)
    target_files = list_files(target, estimator)

    source_files, source_files_estimates = [list(r) for r in zip(*source_files)]
    target_files, target_files_estimates = [list(r) for r in zip(*target_files)]
    estimation = sum(source_files_estimates) + sum(target_files_estimates)

    if batch:
        mapped_files, missing_files = find_missing_files(source_files, target_files, fingerprinter)
    else:
        with click.progressbar(length=estimation, label="Searching for matching files") as bar:
            fpr = functools.partial(fingerprinter, update_cb=bar.update)
            mapped_files, missing_files = find_missing_files(source_files, target_files, fpr)
    
    if verbose:
        if not batch:
            click.echo()
            click.secho("Mapped files:", fg='green', bold=True)

        for source, target in mapped_files:
            click.echo("%s -> %s" % (source, target))

    if not batch:
        click.echo()
        click.secho("Missing files:", fg='red', bold=True)
    
    for source in missing_files:
        click.echo(source)

    if not batch:
        click.echo()
        click.secho("Summary:", fg='yellow', bold=True)
        click.secho("Number of mapped files: {0}".format(len(mapped_files)))
        click.secho("Number of missing files: {0}".format(len(missing_files)))


