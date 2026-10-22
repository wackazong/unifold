# Invariants of sampling

What is true of measuring at every moment. These lines protect the rule "one reading per interval, complete and final when it leaves".

- The sampling times are computed from the seconds since start: first time plus n times the interval. Never "now plus interval"; that drifts by the duration of every measurement.
- One request for raw values per reading. Measuring twice to be sure doubles the largest item of the energy budget cited in [context.md](context.md).
- No value from an earlier reading fills a gap. An unavailable value makes the quantity absent.
- The count of readings since start lives in RAM and starts at 1 with every start. It is continued from nowhere.
