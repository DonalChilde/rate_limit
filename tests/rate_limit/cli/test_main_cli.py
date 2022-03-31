"""Tests for `rate_limit.cli.main_cli` module.

These tests are for the default behavior of the `rate_limit.cli.main_cli` module.

Some changes may be necessary if the default behavior is changed.
"""

from click.testing import CliRunner

from rate_limit.cli import main_cli as cli


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert "Console script for rate_limit" in result.output
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "Show this message and exit." in help_result.output
