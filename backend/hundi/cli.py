#!/usr/bin/env python

from action.health import Health
import logging
import sys
import click

from lib import bootstrap

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("-i", "--info", "log_level", flag_value=logging.INFO)
@click.option("-d", "--debug", "log_level", flag_value=logging.DEBUG)
@click.pass_context
def cli(ctx, log_level):
    if log_level is logging.DEBUG:
        click.echo("Starting cli application: {}".format(" ".join(sys.argv)))
    bootstrap.initialize_logging(log_level if log_level is not None else logging.WARNING)


@cli.command("healthcheck")
def healthcheck():
    click.echo(Health("cli").check())


def main():
    cli()


if __name__ == "__main__":
    cli()
