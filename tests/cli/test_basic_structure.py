"""Basic CLI structure tests.

Verifies that the CLI module can be imported and that the main command
group and subcommands are properly registered.
"""

import pytest


class TestCLIModuleImport:
    """Test CLI module can be imported."""

    def test_import_cli_package(self):
        """Test that the CLI package can be imported."""
        from netbox_dio import cli
        assert hasattr(cli, "__version__") or hasattr(cli, "__name__")

    def test_import_cli_app(self):
        """Test that the CLI app can be imported."""
        from netbox_dio.cli.app import create_app
        cli_app = create_app()
        assert cli_app is not None

    def test_cli_command_group_exists(self):
        """Test that the main CLI command group exists."""
        from typer import Typer
        from netbox_dio.cli.app import create_app

        cli_app = create_app()
        assert isinstance(cli_app, Typer)


class TestCommandRegistration:
    """Test that all CLI commands are properly registered."""

    def test_import_command_registered(self):
        """Test that the import command is registered."""
        from netbox_dio.cli.app import create_app

        cli_app = create_app()
        # Check that 'import' command exists
        commands = [cmd.name for cmd in cli_app.registered_commands]
        assert "import" in commands or "import_" in commands

    def test_export_command_registered(self):
        """Test that the export command is registered."""
        from netbox_dio.cli.app import create_app

        cli_app = create_app()
        commands = [cmd.name for cmd in cli_app.registered_commands]
        assert "export" in commands

    def test_dryrun_command_registered(self):
        """Test that the dry-run command is registered."""
        from netbox_dio.cli.app import create_app

        cli_app = create_app()
        commands = [cmd.name for cmd in cli_app.registered_commands]
        assert "dryrun" in commands or "dry_run" in commands or "dry-run" in commands

    def test_batch_command_registered(self):
        """Test that the batch command is registered."""
        from netbox_dio.cli.app import create_app

        cli_app = create_app()
        commands = [cmd.name for cmd in cli_app.registered_commands]
        assert "batch" in commands or "batch_" in commands


class TestHelpCommands:
    """Test help output for CLI commands."""

    def test_main_help_output(self):
        """Test that main CLI help produces output."""
        from netbox_dio.cli.app import create_app

        cli_app = create_app()

        # Simulate running --help
        from typer.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(cli_app, ["--help"])

        assert result.exit_code == 0
        assert "import" in result.output.lower() or "import_" in result.output.lower()
        assert "export" in result.output.lower()

    def test_import_help_output(self):
        """Test that import command help produces output."""
        from netbox_dio.cli.app import create_app

        cli_app = create_app()

        from typer.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(cli_app, ["import", "--help"])

        assert result.exit_code == 0
        # Help output should describe the import functionality
        assert "import" in result.output.lower() or "json" in result.output.lower() or "yaml" in result.output.lower()

    def test_export_help_output(self):
        """Test that export command help produces output."""
        from netbox_dio.cli.app import create_app

        cli_app = create_app()

        from typer.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(cli_app, ["export", "--help"])

        assert result.exit_code == 0
        assert "export" in result.output.lower()


class TestCommandOptions:
    """Test CLI command options."""

    def test_import_file_option(self):
        """Test that import command has --file option."""
        from netbox_dio.cli.app import create_app

        cli_app = create_app()

        from typer.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(cli_app, ["import", "--help"])

        assert result.exit_code == 0
        # Typer may use single or double dash, check for either
        assert "-file" in result.output or "--file" in result.output

    def test_export_format_option(self):
        """Test that export command has --format option."""
        from netbox_dio.cli.app import create_app

        cli_app = create_app()

        from typer.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(cli_app, ["export", "--help"])

        assert result.exit_code == 0
        assert "--format" in result.output or "format" in result.output.lower()

    def test_dryrun_option(self):
        """Test that dry-run mode is available."""
        from netbox_dio.cli.app import create_app

        cli_app = create_app()

        from typer.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(cli_app, ["dry-run", "--help"])

        assert result.exit_code == 0
        assert "dry-run" in result.output.lower() or "dry run" in result.output.lower() or "dry" in result.output.lower()
