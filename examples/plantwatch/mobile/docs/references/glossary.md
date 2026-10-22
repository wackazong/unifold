# Glossary of the app

Terms that have one fixed meaning in the app and its parts. The terms of the
whole project are cited in [context.md](../explanation/context.md) and are not repeated
here.

| Term | Meaning |
|---|---|
| Fetch | Taking the stored readings of one sensor stick onto the phone and confirming them to the sensor stick. |
| Exchange | One round with the server: the phone sends what waits on it, then takes plants, alerts and history. |
| Upload | The part of an exchange that sends readings. |
| Store | The data the app keeps durably on the phone. The screens show nothing else. |
| Background slot | The run time the operating system gives the app after waking it while it is not on the screen. Its length is in the [platform limits](platform-limits.md). |
| Standing request | What the app leaves with the operating system per paired sensor stick, so that the system wakes the app when that sensor stick appears. |
| Server | Whatever provides `cloud-api`. |

The things the app handles, among them paired sensor stick, session, change
state and the two ages of data, are defined with their fields in the
[data model](data-model.md).
