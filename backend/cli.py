#!/usr/bin/env python

from hundi.action import health, observer
from hundi.action.crypto.ftx.ticker import TickerFtxCryptoAction
from hundi.config.ticker import TICKER_ACTION
from hundi.lib import bootstrap
from hundi.lib.executor import ExecutorLib as Executor
import logging
import sys
import click

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


@cli.command("observe")
@click.option("--log_level", default=logging.INFO)
@click.option("--filter")
def observe(log_level, filter):
    click.echo(observer.observe(log_level, filter, cli=click))


@cli.command(TICKER_ACTION)
@click.option("--market_type", default="spot")
@click.option("--pair", default="abnb-1231")
def ticker_ftx_crypto_action(market_type: str, pair: str):
    try:
        executor = Executor()
        action = TickerFtxCryptoAction(market_type, pair)
        executor.try_run_async(TICKER_ACTION, action._ws.run_forever)
    except KeyboardInterrupt:
        executor.cancel()


def main():
    cli()


if __name__ == "__main__":
    cli()
