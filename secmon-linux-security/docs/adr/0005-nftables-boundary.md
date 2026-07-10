# ADR-0005: Controlled nftables integration

- Status: accepted
- Date: 2026-07-10

Firewall changes will go through a dedicated blocker service and a named
nftables set. External IP/CIDR values must be parsed with Python's `ipaddress`
module and passed as structured arguments. No code may concatenate untrusted
values into `sh -c`, `shell=True`, or an arbitrary command line. Automatic
blocking remains disabled by default.
