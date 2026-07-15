# SQLite Runtime Policy

SQLite is the durable persistence layer, not the live gameplay authority.

* Use WAL where safe, foreign keys on, bounded busy timeouts, and short transactions.
* Do not open a new connection per combat hit or per violence participant.
* Do not hold resident combat locks while writing SQLite.
* Do not hold SQLite transactions across event-loop awaits.
* Combat tables are classified as checkpoint/audit/legacy compatibility unless an immediate death transaction is executing.
* Canonical tracing for database work records category, statement type, duration, lock wait, transaction duration, connection ID, task/thread, caller, and trace ID. For resident combat the expected trace is empty.
