#!/usr/bin/env python
"""
SSH Attack Report CLI Tool

Generates reports on SSH authentication failures and attacking IPs.
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

import sqlite3


def get_database_path() -> Path:
    """Get database path from settings or default."""
    try:
        from secmon_backend.config import get_settings
        settings = get_settings()
        return settings.database_path
    except Exception:
        return Path("./var/secmon.db")


def generate_report(
    database_path: Path,
    hours: int = 24,
    top_n: int = 10,
    detailed: bool = False,
) -> dict:
    """
    Generate attack report for specified time period.

    Args:
        database_path: Path to SQLite database
        hours: Number of hours to look back (default: 24)
        top_n: Number of top attacking IPs to show (default: 10)
        detailed: Show detailed information (default: False)

    Returns:
        Dictionary with report data
    """
    if not database_path.exists():
        print(f"Error: Database not found at {database_path}")
        sys.exit(1)

    try:
        conn = sqlite3.connect(database_path)
        conn.row_factory = sqlite3.Row

        # Calculate time threshold
        threshold = (datetime.now() - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")

        # Get total attack count
        cursor = conn.execute(
            "SELECT COUNT(*) as total FROM attack_events WHERE timestamp >= ?",
            (threshold,),
        )
        total_attacks = cursor.fetchone()["total"]

        # Get top attacking IPs
        cursor = conn.execute(
            f"""
            SELECT
                source_ip,
                COUNT(*) as attack_count,
                MAX(timestamp) as last_seen,
                MIN(timestamp) as first_seen,
                GROUP_CONCAT(DISTINCT username) as usernames
            FROM attack_events
            WHERE timestamp >= ?
            GROUP BY source_ip
            ORDER BY attack_count DESC
            LIMIT {top_n}
            """,
            (threshold,),
        )
        top_attackers = cursor.fetchall()

        # Get attack distribution by service
        cursor = conn.execute(
            "SELECT service, COUNT(*) as count FROM attack_events WHERE timestamp >= ? GROUP BY service ORDER BY count DESC",
            (threshold,),
        )
        service_distribution = cursor.fetchall()

        # Get attack distribution by failure reason
        cursor = conn.execute(
            "SELECT failure_reason, COUNT(*) as count FROM attack_events WHERE timestamp >= ? GROUP BY failure_reason ORDER BY count DESC",
            (threshold,),
        )
        failure_reasons = cursor.fetchall()

        # Get unique attackers count
        cursor = conn.execute(
            "SELECT COUNT(DISTINCT source_ip) as unique_attackers FROM attack_events WHERE timestamp >= ?",
            (threshold,),
        )
        unique_attackers = cursor.fetchone()["unique_attackers"]

        # Run PRAGMA quick_check
        cursor = conn.execute("PRAGMA quick_check")
        integrity_result = cursor.fetchone()

        conn.close()

        return {
            "period_hours": hours,
            "total_attacks": total_attacks,
            "unique_attackers": unique_attackers,
            "top_attackers": [dict(row) for row in top_attackers],
            "service_distribution": [dict(row) for row in service_distribution],
            "failure_reasons": [dict(row) for row in failure_reasons],
            "integrity_check": integrity_result[0] if integrity_result else "unknown",
            "detailed": detailed,
        }

    except Exception as e:
        print(f"Error generating report: {e}")
        sys.exit(1)


def print_report(report: dict) -> None:
    """Print formatted report to stdout."""
    print("=" * 70)
    print(f"SSH Attack Report - Last {report['period_hours']} Hours")
    print("=" * 70)
    print()

    print(f"Total Attacks: {report['total_attacks']}")
    print(f"Unique Attackers: {report['unique_attackers']}")
    print()

    if report["top_attackers"]:
        print(f"Top {len(report['top_attackers'])} Attacking IPs:")
        print("-" * 70)
        print(f"{'Rank':<6}{'IP Address':<16}{'Count':<8}{'First Seen':<20}{'Last Seen':<20}")
        print("-" * 70)

        for i, attacker in enumerate(report["top_attackers"], 1):
            print(
                f"{i:<6}{attacker['source_ip']:<16}{attacker['attack_count']:<8}"
                f"{attacker['first_seen'][:19]:<20}{attacker['last_seen'][:19]:<20}"
            )
            if report["detailed"] and attacker.get("usernames"):
                print(f"       Usernames: {attacker['usernames']}")
        print()

    if report["service_distribution"]:
        print("Attacks by Service:")
        print("-" * 40)
        for item in report["service_distribution"]:
            print(f"  {item['service']:<20} {item['count']:>10}")
        print()

    if report["failure_reasons"]:
        print("Attacks by Failure Reason:")
        print("-" * 40)
        for item in report["failure_reasons"]:
            print(f"  {item['failure_reason']:<20} {item['count']:>10}")
        print()

    print("Database Integrity Check:")
    print(f"  PRAGMA quick_check: {report['integrity_check']}")
    print()


def main():
    """Main entry point for CLI tool."""
    parser = argparse.ArgumentParser(
        description="Generate SSH attack reports from SecMon database"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Number of hours to look back (default: 24)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of top attacking IPs to show (default: 10)",
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed information including usernames",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help="Path to database file (default: from settings or ./var/secmon.db)",
    )

    args = parser.parse_args()

    # Get database path
    db_path = args.db or get_database_path()

    # Generate report
    report = generate_report(db_path, args.hours, args.top, args.detailed)

    # Print report
    print_report(report)


if __name__ == "__main__":
    main()
