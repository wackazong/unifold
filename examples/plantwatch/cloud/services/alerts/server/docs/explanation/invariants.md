# Invariants of server

What is true of the process at every moment. Every guarantee about "once" rests on these few lines, so they are concentrated here.

- `server` compares no measured value with a threshold. There is no `if` on a measured value or a threshold in this unit; a case that seems to need one belongs to whoever provides `evaluation`.
- A reading's outcome, the evaluation state and the owed notification are stored in one transaction.
- `notification` is never called inside the transaction that stores an alert, and never before it commits.
- An event is confirmed only after the transaction for it is committed. It stays unconfirmed while `evaluation` cannot decide.
- The evaluation state is neither read nor changed. What arrives is stored; what was stored is handed back.
