# mcp-quickstart

A small, tested **Model Context Protocol** server in Python — a little **finance
toolkit**. It exposes finance/stat tools over MCP so any MCP client (Claude Code,
Cursor, Windsurf) can call them, and it demonstrates the *full* MCP surface:
**tools**, a **resource**, and a **prompt**.

Built with the official [`mcp`](https://github.com/modelcontextprotocol/python-sdk)
Python SDK (`FastMCP`).

## Tools

| Tool | Description |
|---|---|
| `summary_stats(numbers)` | count / mean / median / stdev for a list |
| `compound_interest(principal, annual_rate, years, compounds_per_year=12)` | future value + interest earned |
| `loan_payment(principal, annual_rate, months)` | monthly payment, total paid, total interest (amortizing loan) |
| `percentage_change(old, new)` | percent change between two values |
| `moving_average(numbers, window)` | simple moving average over a sliding window |
| `utc_now()` | current UTC time, ISO-8601 |

Plus an MCP **resource** (`finance://reference`, the conventions the tools assume)
and a **prompt** (`savings_plan`, a reusable savings-goal template).

> Rates are decimals throughout: `0.05` means 5%.

## Run

```bash
pip install -e ".[dev]"
python server.py
```

## Use it in Claude Code

```bash
claude mcp add finance-toolkit -- python /absolute/path/to/server.py
```

Then ask your agent, e.g. *"use loan_payment for a 250000 loan at 6% APR over 360
months"* or *"run summary_stats on [4, 8, 15, 16, 23, 42]"*.

## Develop

```bash
ruff check .   # lint
pytest -q      # tests
```

Each tool is a plain, validated function, so the math is unit-tested directly
(`test_server.py`) without going through the protocol. CI runs lint + tests on
every push (`.github/workflows/ci.yml`).
