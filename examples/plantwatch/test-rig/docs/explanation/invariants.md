# Invariants of test-rig

What is true of the rig at every moment. These lines keep its tests
independent of how the things under test are built.

- The rig never looks behind an interface to make a test easier: no
  database queries, no log files, no debug endpoints, no shared code with
  anything under test.
- The rig implements the central side from `link-profile` alone and
  builds readings from `reading-format` alone.
- Waiting times are in [configurations.md](../references/configurations.md).
  A test contains no waiting time of its own.
