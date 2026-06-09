"""Web-log metrics — every function here is CORRECT, but three are too slow.

The behavior tests pass already.  The PERFORMANCE tests fail, because
three of these functions do quadratic work where linear work would do.
Your fixes must keep behavior identical (the behavior tests pin it) and
bring each function inside its generous time budget.

Your job:
  - Find and fix the 3 performance bugs.
  - All tests — behavior AND performance — must pass without modification.

Relevant reading: exercises/36_performance_tuning/README.md.
"""


def unique_visitors(visits):
    """Distinct visitor ids, in first-seen order."""
    seen = []
    for visitor in visits:
        if visitor not in seen:
            seen.append(visitor)
    return seen


def running_averages(latencies):
    """For every prefix of *latencies*, its mean.

    result[i] == mean(latencies[0..i]).  Used to chart how the average
    response time evolves over a day of traffic.
    """
    averages = []
    for i in range(len(latencies)):
        window = latencies[:i + 1]
        averages.append(sum(window) / len(window))
    return averages


def newest_first(entries):
    """Entries in reverse arrival order (newest first).

    *entries* arrives oldest-first; dashboards want the newest at the top.
    """
    ordered = []
    for entry in entries:
        ordered.insert(0, entry)
    return ordered


def error_rate(entries):
    """Fraction of entries whose status is >= 500.  (Already fine.)"""
    if not entries:
        return 0.0
    errors = sum(1 for entry in entries if entry["status"] >= 500)
    return errors / len(entries)
