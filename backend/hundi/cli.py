#!/usr/bin/env python

from action import health, observer
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
    click.echo(health.check("cli"))


@click.option("--log_level", default=logging.INFO)
@click.option("--filter")
@cli.command("observe")
def observe(log_level, filter):
    click.echo(observer.observe(log_level, filter, cli=click))


def main():
    cli()


if __name__ == "__main__":
    cli()
