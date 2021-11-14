#!/usr/bin/env python

import logging
import sys
import click


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("-d", "--debug", "log_level", flag_value=logging.DEBUG)
@click.pass_context
def cli(ctx, log_level):
    # bootstrap.initialize_logging(log_level)
    logging.info("Starting cli application: {}".format(" ".join(sys.argv)))
