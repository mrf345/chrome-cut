# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from core import get_ips, loop_ips, is_ccast, cancel_app
import click


def v_local_ip(a, b, value):
    """ to validate the local ip """
    if value[0] not in get_ips():
        raise click.BadParameter(
            'requires your currently connected IP address')
    return value[0]


def v_cast_ip(a, b, value):
    """ to validate if ip is chrome cast """
    if not is_ccast(value[0]):
        raise click.BadParameter(
            'require active chrome cast device IP, try scan option to find it')
    return value[0]


@click.group()
def cli():
    """ group to gather all the commands in """
    pass


@click.command()
@click.option('--ip_address', '-ip', multiple=True,
              help='Your current IP address, to scan with',
              type=str, callback=v_local_ip)
def scan(ip_address):
    """to scan the local network for chrome cast devices, with inputted IP"""
    active_CC = loop_ips(ip_address, True)
    if active_CC is None:
        click.echo(
            click.style(
                'No active chrome cast devices were found',
                bold=True, fg='red'))
    else:
        click.echo(
            click.style(
                'Active chrome cast devices :',
                bold=True, fg='blue'))
        click.echo()
        for index, ip in enumerate(active_CC):
            click.echo(
                click.style(
                    ' < ' + str(index + 1) + ' > ' + ip,
                    bg='red', fg='black', blink=True))
    click.echo()


@click.command()
@click.option('--ip_address', '-ip', multiple=True,
              help='Chrome cast IP address', default='Not enterd',
              type=str)
def detect(ip_address):
    if is_ccast(ip_address[0]):
        click.echo(
            click.style(
                ip_address[0] + ' is Active chrome cast device.',
                bold=True, fg='blue'))
    else:
        click.echo(
            click.style(
                str(ip_address[0]) + ' is Not Active chrome cast devices.',
                bold=True, fg='red'))
    click.echo()


@click.command()
@click.option('--ip_address', '-ip', multiple=True,
              help='Chrome cast IP address',
              type=str, callback=v_cast_ip)
def abort_stream(ip_address):
    if cancel_app(ip_address[0]):
        click.echo(
            click.style(
                ip_address[0] + ' current stream got canceled.',
                bold=True, fg='blue'))
    else:
        click.echo(
            click.style(
                ip_address[0] + ' failed to cancel stream.',
                bold=True, fg='red'))


@click.command()
@click.option('--ip_address', '-ip', multiple=True,
              help='Chrome cast IP address',
              type=str)
@click.option('--youtube_video', '-v', multiple=True,
              help='Youtube video link to stream',
              type=str)
def stream(ip_address, youtube_video):
    click.echo('it got scanned !')


@click.command()
@click.option('--ip_address', '-ip', multiple=True,
              help='Chrome cast ip address',
              type=str)
@click.option('--youtube_video', '-v', multiple=True,
              help='Youtube video link to stream',
              type=str)
@click.option('--duration', '-d', multiple=True,
              help='Duration to wait between each streem command',
              type=int)
def loop_stream(ip_address, youtube_video, duration):
    click.echo('it got scanned !')


@click.command()
@click.option('--ip_address', '-ip', multiple=True,
              help='Chrome cast IP address',
              type=str)
def factory_restore(ip_address):
    click.echo('it got scanned !')


@click.command()
@click.option('--ip_address', '-ip', multiple=True,
              help='Chrome cast IP address',
              type=str)
@click.option('--duration', '-d', multiple=True,
              help='Duration to wait between each factory restore command',
              type=int)
def loop_factory_restore(ip_address, duration):
    click.echo('it got scanned !')


cli.add_command(scan)
cli.add_command(detect)
cli.add_command(abort_stream)
cli.add_command(stream)
cli.add_command(loop_stream)
cli.add_command(factory_restore)
cli.add_command(loop_factory_restore)

if __name__ == '__main__':
    cli()
