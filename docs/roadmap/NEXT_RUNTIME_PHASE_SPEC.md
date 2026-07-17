# Next Runtime Phase Spec — Phase 16B

## Exact objective
Implement persistent exit and door state parity for closed, open, locked, unlocked, keyed, hidden, and one-way exits on Smart MUD's production movement path.

## Source evidence
Adventurer's Lair ownership is in `src/act.movement.c` command handlers, `src/db.c` room/exit loaders and reset handling, and `src/structs.h` exit/room flag structs.

## Existing Smart MUD path
Use `engine/mud_runtime.py`, `engine/mud_commands.py`, `smart_mud/event_bus.py`, world registry data, and existing Builder draft room/exit records.

## Required runtime behavior
Movement must block closed/locked exits, allow open exits, require matching keys to unlock, support no-key failure messages, preserve one-way exits, expose hidden exits only through appropriate observation rules, persist mutable configured door state, and accept reset restoration through the reset service.

## Architecture rules
Runtime service first; commands call canonical operations; Builder only edits definitions; direct schema mutation is forbidden.

## Schemas and persistence
Add minimal SQLite/world-state rows only if existing runtime store cannot represent mutable door state. Migrate conservatively.

## Events
Publish `door_opened`, `door_closed`, `door_locked`, `door_unlocked`, `movement_blocked`, and `movement_completed`.

## Commands
`open`, `close`, `lock`, `unlock`, `pick`, `bash`, and movement aliases; no broad REDIT/ZEDIT.

## Validation
Validate exit target references, key item references, reset door-state commands, one-way exits, and hidden-exit metadata.

## Builder exposure requirements
Only document dependency and preserve existing draft fields. Do not implement broad Builder UI in Phase 16B.

## Tests
Unit and command tests for success/failure, key checks, persistence across runtime restart, reset behavior, one-way exits, hidden exits, and event publication.

## Manual acceptance
Create two rooms with a locked north/south door and key; fail to move north, unlock/open with key, move, restart, verify configured persistence/reset semantics.

## Exclusions
No visual Builder, no new combat bash damage, no full trap system, no broad content migration.

## Completion standard
All focused tests pass and docs/matrix update from STRUCTURAL/FUNCTIONAL partial toward FULL for door capabilities.
