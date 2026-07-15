# Persistence Boundaries

## Immediate durable transactions

Immediate transactions are reserved for operations where loss, duplication, or reordering is unacceptable: economy spending, ownership-changing item transfer, death idempotency, corpse creation, final reward claim, quest reward claim, explicit admin checkpoint, logout, and shutdown.

## Deferred work

Ordinary damage, healing, regeneration, target changes, wait states, round history, command history, scrollback, and transient combat status are resident mutations. They mark actors or encounters dirty and are eligible for bounded, coalesced persistence later.

## Worker contract

A single bounded persistence worker should own durable flushes. It may coalesce duplicate actor/encounter saves, preserve per-actor ordering, retry failures, record dead-letter diagnostics, and flush on clean shutdown. It must never mutate resident combat state while writing SQLite and must not run blocking SQLite work on FastAPI request or heartbeat tasks.
