# Deployment of cloud

Every service is one container image. The table shows what the folder tree cannot: how many instances run and what must survive a restart.

| Part | Instances | Volume | Reachable from outside |
|---|---|---|---|
| [gateway](../../services/gateway/README.md) | 2 or more | none | yes, one port |
| [ingest](../../services/ingest/README.md) | 2 or more | none | no |
| [plants](../../services/plants/README.md) | 1 or more | none | no |
| [alerts](../../services/alerts/README.md) | 1 or more | none | no |
| [platform](../../platform/README.md) | 1 per container | yes | no |

Consequences:

- Every service can be stopped and started without losing data. All durable state is in [platform](../../platform/README.md).
- A service image is replaced by starting new instances before the old ones stop. Events that arrive in between wait on the event bus.
- [platform](../../platform/README.md) is the single point of failure of version 1. While it is down, uploads are refused with `unavailable` and the client keeps its readings.
