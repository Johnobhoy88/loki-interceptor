#!/usr/bin/env python3
"""
LOKI Platform Administration CLI
Comprehensive admin tools for platform management
"""

import asyncio
import click
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.platform.orchestrator import get_orchestrator, PlatformOrchestrator
from backend.platform.config import get_config
from backend.platform.feature_flags import RolloutStrategy

logger = logging.getLogger(__name__)


@click.group()
@click.option('--config', help='Configuration file path')
@click.pass_context
def cli(ctx, config):
    """LOKI Platform Administration CLI"""
    ctx.ensure_object(dict)
    ctx.obj['config_file'] = config


# Health Commands

@cli.group()
def health():
    """Health monitoring commands"""
    pass


@health.command()
def check():
    """Run health check"""
    async def run():
        orchestrator = get_orchestrator()
        await orchestrator.startup()

        health = await orchestrator.health_monitor.check_health()

        click.echo("\n=== HEALTH CHECK REPORT ===\n")
        click.echo(f"Overall Status: {health.status.value.upper()}")
        click.echo(f"Uptime: {health.uptime:.2f}s")
        click.echo(f"Timestamp: {health.timestamp.isoformat()}\n")

        click.echo("Component Checks:")
        for check in health.checks:
            status_color = {
                'healthy': 'green',
                'degraded': 'yellow',
                'unhealthy': 'red',
                'unknown': 'white'
            }.get(check.status.value, 'white')

            click.echo(f"  [{click.style(check.status.value.upper(), fg=status_color)}] {check.name}")
            click.echo(f"      Message: {check.message}")
            click.echo(f"      Response Time: {check.response_time:.2f}ms\n")

        await orchestrator.shutdown()

    asyncio.run(run())


@health.command()
@click.option('--last', default=10, help='Number of recent checks to show')
def history(last):
    """Show health check history"""
    async def run():
        orchestrator = get_orchestrator()
        await orchestrator.startup()

        history = orchestrator.health_monitor.get_health_history(last_n=last)

        click.echo(f"\n=== LAST {len(history)} HEALTH CHECKS ===\n")

        for i, health in enumerate(history, 1):
            click.echo(f"{i}. {health.timestamp.isoformat()} - {health.status.value.upper()}")

        await orchestrator.shutdown()

    asyncio.run(run())


@health.command()
def metrics():
    """Show health metrics"""
    async def run():
        orchestrator = get_orchestrator()
        await orchestrator.startup()

        metrics = orchestrator.health_monitor.get_metrics()

        click.echo("\n=== HEALTH METRICS ===\n")
        click.echo(f"Uptime: {metrics.get('uptime', 0):.2f}s")
        click.echo(f"Total Checks: {metrics.get('total_checks', 0)}")
        click.echo(f"Recent Status: {metrics.get('recent_status', 'unknown').upper()}")

        click.echo("\nAverage Response Times:")
        for check_name, avg_time in metrics.get('average_response_times', {}).items():
            click.echo(f"  {check_name}: {avg_time:.2f}ms")

        await orchestrator.shutdown()

    asyncio.run(run())


# Feature Flags Commands

@cli.group()
def flags():
    """Feature flags management"""
    pass


@flags.command('list')
@click.option('--enabled-only', is_flag=True, help='Show only enabled flags')
def list_flags(enabled_only):
    """List all feature flags"""
    async def run():
        orchestrator = get_orchestrator()
        await orchestrator.startup()

        all_flags = orchestrator.feature_flags.get_all_flags()

        click.echo("\n=== FEATURE FLAGS ===\n")

        for name, flag in all_flags.items():
            if enabled_only and not flag.enabled:
                continue

            status = click.style('ENABLED', fg='green') if flag.enabled else click.style('DISABLED', fg='red')
            click.echo(f"{status} {name}")
            click.echo(f"  Description: {flag.description}")
            click.echo(f"  Strategy: {flag.strategy.value}")
            if flag.strategy.value == 'percentage':
                click.echo(f"  Rollout: {flag.percentage}%")
            click.echo()

        await orchestrator.shutdown()

    asyncio.run(run())


@flags.command()
@click.argument('name')
@click.option('--enabled/--disabled', default=True)
@click.option('--description', help='Flag description')
@click.option('--strategy', type=click.Choice(['all', 'none', 'percentage', 'users', 'groups']), default='all')
@click.option('--percentage', type=int, help='Rollout percentage (0-100)')
def create(name, enabled, description, strategy, percentage):
    """Create a new feature flag"""
    async def run():
        orchestrator = get_orchestrator()
        await orchestrator.startup()

        strategy_enum = RolloutStrategy(strategy)

        flag = orchestrator.feature_flags.create_flag(
            name=name,
            enabled=enabled,
            description=description or '',
            strategy=strategy_enum,
            percentage=percentage or 0
        )

        click.echo(f"\n{click.style('SUCCESS', fg='green')} Created feature flag: {name}")
        click.echo(f"  Enabled: {flag.enabled}")
        click.echo(f"  Strategy: {flag.strategy.value}")

        await orchestrator.shutdown()

    asyncio.run(run())


@flags.command()
@click.argument('name')
@click.option('--enabled/--disabled', help='Enable or disable flag')
@click.option('--percentage', type=int, help='Rollout percentage (0-100)')
def update(name, enabled, percentage):
    """Update a feature flag"""
    async def run():
        orchestrator = get_orchestrator()
        await orchestrator.startup()

        kwargs = {}
        if enabled is not None:
            kwargs['enabled'] = enabled
        if percentage is not None:
            kwargs['percentage'] = percentage

        flag = orchestrator.feature_flags.update_flag(name, **kwargs)

        if flag:
            click.echo(f"\n{click.style('SUCCESS', fg='green')} Updated feature flag: {name}")
        else:
            click.echo(f"\n{click.style('ERROR', fg='red')} Flag not found: {name}")

        await orchestrator.shutdown()

    asyncio.run(run())


@flags.command()
@click.argument('name')
def delete(name):
    """Delete a feature flag"""
    async def run():
        orchestrator = get_orchestrator()
        await orchestrator.startup()

        if click.confirm(f"Are you sure you want to delete flag '{name}'?"):
            success = orchestrator.feature_flags.delete_flag(name)

            if success:
                click.echo(f"\n{click.style('SUCCESS', fg='green')} Deleted feature flag: {name}")
            else:
                click.echo(f"\n{click.style('ERROR', fg='red')} Flag not found: {name}")

        await orchestrator.shutdown()

    asyncio.run(run())


@flags.command()
def stats():
    """Show feature flags statistics"""
    async def run():
        orchestrator = get_orchestrator()
        await orchestrator.startup()

        stats = orchestrator.feature_flags.get_stats()

        click.echo("\n=== FEATURE FLAGS STATISTICS ===\n")
        click.echo(f"Total Flags: {stats['total']}")
        click.echo(f"Enabled: {stats['enabled']}")
        click.echo(f"Disabled: {stats['disabled']}")

        click.echo("\nBy Strategy:")
        for strategy, count in stats['by_strategy'].items():
            click.echo(f"  {strategy}: {count}")

        await orchestrator.shutdown()

    asyncio.run(run())


# System Commands

@cli.group()
def system():
    """System management commands"""
    pass


@system.command()
def status():
    """Show system status"""
    async def run():
        orchestrator = get_orchestrator()
        await orchestrator.startup()

        status = await orchestrator.get_full_status()

        click.echo("\n=== SYSTEM STATUS ===\n")
        click.echo(f"State: {status['state'].upper()}")
        click.echo(f"Environment: {status['environment']}")
        click.echo(f"Uptime: {status['uptime']:.2f}s")

        if status['start_time']:
            click.echo(f"Started: {status['start_time']}")

        click.echo("\nSubsystems:")
        for name, active in status['subsystems'].items():
            status_text = click.style('ACTIVE', fg='green') if active else click.style('INACTIVE', fg='red')
            click.echo(f"  {name}: {status_text}")

        if status.get('health'):
            health = status['health']
            click.echo(f"\nHealth: {health['status'].upper()}")

        await orchestrator.shutdown()

    asyncio.run(run())


@system.command()
@click.option('--output', type=click.Path(), help='Output file path')
def diagnostics(output):
    """Run comprehensive diagnostics"""
    async def run():
        orchestrator = get_orchestrator()
        await orchestrator.startup()

        diagnostics = await orchestrator.run_diagnostics()

        if output:
            with open(output, 'w') as f:
                json.dump(diagnostics, f, indent=2, default=str)
            click.echo(f"\n{click.style('SUCCESS', fg='green')} Diagnostics saved to: {output}")
        else:
            click.echo("\n=== DIAGNOSTICS REPORT ===\n")
            click.echo(json.dumps(diagnostics, indent=2, default=str))

        await orchestrator.shutdown()

    asyncio.run(run())


@system.command()
def reload():
    """Reload configuration"""
    async def run():
        orchestrator = get_orchestrator()
        await orchestrator.startup()

        try:
            await orchestrator.reload_config()
            click.echo(f"\n{click.style('SUCCESS', fg='green')} Configuration reloaded")
        except Exception as e:
            click.echo(f"\n{click.style('ERROR', fg='red')} Failed to reload configuration: {e}")

        await orchestrator.shutdown()

    asyncio.run(run())


# Metrics Commands

@cli.group()
def metrics():
    """Metrics and telemetry commands"""
    pass


@metrics.command()
def summary():
    """Show metrics summary"""
    async def run():
        orchestrator = get_orchestrator()
        await orchestrator.startup()

        summary = orchestrator.telemetry.get_summary()

        click.echo("\n=== TELEMETRY SUMMARY ===\n")

        click.echo("Metrics:")
        for key, value in summary.get('metrics', {}).items():
            click.echo(f"  {key}: {value}")

        click.echo("\nTraces:")
        for key, value in summary.get('traces', {}).items():
            click.echo(f"  {key}: {value}")

        click.echo("\nRequests:")
        for key, value in summary.get('requests', {}).items():
            click.echo(f"  {key}: {value}")

        click.echo("\nTop Endpoints:")
        for endpoint in summary.get('top_endpoints', []):
            click.echo(f"  {endpoint['endpoint']}: {endpoint['requests']} requests, {endpoint['errors']} errors")

        await orchestrator.shutdown()

    asyncio.run(run())


@metrics.command()
@click.option('--output', type=click.Path(), help='Output file path')
def export(output):
    """Export all metrics"""
    async def run():
        orchestrator = get_orchestrator()
        await orchestrator.startup()

        metrics = orchestrator.telemetry.export_metrics()

        if output:
            with open(output, 'w') as f:
                json.dump(metrics, f, indent=2, default=str)
            click.echo(f"\n{click.style('SUCCESS', fg='green')} Metrics exported to: {output}")
        else:
            click.echo(json.dumps(metrics, indent=2, default=str))

        await orchestrator.shutdown()

    asyncio.run(run())


# Errors Commands

@cli.group()
def errors():
    """Error monitoring commands"""
    pass


@errors.command()
def stats():
    """Show error statistics"""
    async def run():
        orchestrator = get_orchestrator()
        await orchestrator.startup()

        stats = orchestrator.error_handler.get_error_stats()

        click.echo("\n=== ERROR STATISTICS ===\n")
        click.echo(f"Total Errors: {stats['total_errors']}")
        click.echo(f"Recent Errors: {stats['recent_errors']}")

        click.echo("\nError Counts by Type:")
        for error_type, count in stats.get('error_counts', {}).items():
            click.echo(f"  {error_type}: {count}")

        click.echo("\nSeverity Distribution:")
        for severity, count in stats.get('severity_distribution', {}).items():
            click.echo(f"  {severity.upper()}: {count}")

        click.echo("\nCircuit Breakers:")
        for name, breaker_info in stats.get('circuit_breakers', {}).items():
            state_color = {'closed': 'green', 'open': 'red', 'half_open': 'yellow'}.get(breaker_info['state'], 'white')
            state_text = click.style(breaker_info['state'].upper(), fg=state_color)
            click.echo(f"  {name}: {state_text} ({breaker_info['failures']} failures)")

        await orchestrator.shutdown()

    asyncio.run(run())


@errors.command()
@click.option('--last', default=10, help='Number of recent errors to show')
@click.option('--severity', type=click.Choice(['low', 'medium', 'high', 'critical']), help='Filter by severity')
def recent(last, severity):
    """Show recent errors"""
    async def run():
        orchestrator = get_orchestrator()
        await orchestrator.startup()

        from backend.platform.error_handler import ErrorSeverity

        severity_filter = ErrorSeverity(severity) if severity else None
        recent_errors = orchestrator.error_handler.get_recent_errors(last, severity_filter)

        click.echo(f"\n=== LAST {len(recent_errors)} ERRORS ===\n")

        for i, error in enumerate(recent_errors, 1):
            severity_color = {'low': 'white', 'medium': 'yellow', 'high': 'red', 'critical': 'red'}.get(error.severity.value, 'white')
            severity_text = click.style(error.severity.value.upper(), fg=severity_color)

            click.echo(f"{i}. [{severity_text}] {error.error_type}")
            click.echo(f"   Time: {error.timestamp.isoformat()}")
            click.echo(f"   Message: {error.message}")
            if error.recovery_attempted:
                recovery_text = click.style('SUCCESS', fg='green') if error.recovery_successful else click.style('FAILED', fg='red')
                click.echo(f"   Recovery: {recovery_text}")
            click.echo()

        await orchestrator.shutdown()

    asyncio.run(run())


@errors.command()
@click.argument('service')
def reset_breaker(service):
    """Reset a circuit breaker"""
    async def run():
        orchestrator = get_orchestrator()
        await orchestrator.startup()

        orchestrator.error_handler.reset_circuit_breaker(service)
        click.echo(f"\n{click.style('SUCCESS', fg='green')} Circuit breaker '{service}' has been reset")

        await orchestrator.shutdown()

    asyncio.run(run())


# Configuration Commands

@cli.group()
def config():
    """Configuration management"""
    pass


@config.command()
def show():
    """Show current configuration"""
    async def run():
        orchestrator = get_orchestrator()
        await orchestrator.startup()

        config_dict = orchestrator.config.to_dict()

        click.echo("\n=== CURRENT CONFIGURATION ===\n")
        click.echo(json.dumps(config_dict, indent=2, default=str))

        await orchestrator.shutdown()

    asyncio.run(run())


@config.command()
def validate():
    """Validate configuration"""
    async def run():
        config = get_config()
        errors = config.validate()

        if errors:
            click.echo(f"\n{click.style('CONFIGURATION ERRORS', fg='red')}\n")
            for error in errors:
                click.echo(f"  ✗ {error}")
            sys.exit(1)
        else:
            click.echo(f"\n{click.style('✓ CONFIGURATION VALID', fg='green')}\n")

    asyncio.run(run())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    cli()
