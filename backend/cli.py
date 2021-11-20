#!/usr/bin/env python

from hundi.lib import helper
from hundi.action import health, observer
from hundi.action.crypto.ftx.ticker import TickerFtxCryptoAction
from hundi.config.ticker import TICKER_ACTION
from hundi.lib import bootstrap
from hundi.lib.executor.websocket import WebSocketExecutorLib
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
    bootstrap.initialize_logging(log_level if log_level else logging.INFO)


@cli.command("healthcheck")
def healthcheck():
    click.echo(health.check("cli"))


@cli.command("observe")
@click.option("--filter", default="")
def observe(filter):
    click.echo(observer.observe(filter, cli=click))


@cli.command("hundi.action.ticker")
@click.option("--type", default="crypto")
@click.option("--exchange", default="ftx")
@click.option("--market_type", default="spot")
@click.option("--markets", default="TRYBBULL/USD")
def ticker_action(type: str, exchange: str, market_type: str, markets: str) -> None:
    try:
        action = TickerFtxCryptoAction(helper.get_paths(type, exchange, market_type, markets, "ticker"))
        action.start()
    except Exception as e:
        click.echo(e)
        # action.stop()


@cli.command("hundi.action.markets")
@click.option("--type", default="crypto")
@click.option("--exchange", default="ftx")
@click.option("--market_type", default="spot")
def markets_action(type: str, exchange: str, market_type: str) -> None:
    try:
        action = TickerFtxCryptoAction(helper.get_paths(type, exchange, market_type, "markets"))
        action.start()
    except Exception as e:
        click.echo(e)


def main():
    cli()


if __name__ == "__main__":
    cli()
