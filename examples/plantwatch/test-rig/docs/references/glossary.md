# Glossary of test-rig

Terms that have one fixed meaning inside this unit. Inherited terms are cited in [context.md](../explanation/context.md) and are not repeated here.

| Term | Meaning |
|---|---|
| Device under test | The one thing a run fetches readings from: a real sensor stick or a simulated one. |
| Run | One execution of the rig from start to report. |
| Configuration | `real` or `simulated`: what the device under test is in a run ([configurations.md](configurations.md)). |
| Promise | A statement about the system that a user of its public interfaces can rely on. A test verifies one promise. |
| Stimulus | What a test does at the public interfaces to put a promise to the test. |
| Expected observation | What the rig must see at the public interfaces if the promise holds. |
| Group | Tests that share a part of the path: `link`, `relay` or `alert`. |
| Fresh plant | A plant the rig creates for one test and binds to the device under test, after removing the plant of the tests before. |
| Passed, failed, in error, skipped | The four results of a test, defined in [test-report.md](test-report.md). |
