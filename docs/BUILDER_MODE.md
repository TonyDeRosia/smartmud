# Smart MUD Builder Mode

Builder Mode is the command-first foundation for safe in-game world editing.

## Permissions

Only accounts/characters with the `builder`, `admin`, or `owner` role can run Builder commands. Normal `player` and `helper` roles cannot see or use Builder internals.

## Workspace

Drafts are stored under `worlds/<world_id>/builder/` with these folders:

- `audit`
- `history`
- `snapshots`
- `exports`
- `imports`
- `templates`

Live world files are not overwritten by normal edit commands. `builder save` writes a safe export into `builder/exports` for manual promotion.

## Commands

Mode and lifecycle commands:

- `builder`, `build`, `builder on`, `builder off`
- `builder validate`
- `builder save`
- `builder reload`
- `builder snapshot`
- `builder history`

Room commands:

- `redit`, `rstat`, `rcreate`, `rset`, `rdesc`, `rname`, `rexits`, `rfeature`, `rdelete`

Exit commands:

- `exedit`, `excreate`, `exset`, `exdelete`

Feature commands:

- `fedit`, `fcreate`, `fset`, `fdesc`, `fdelete`

Item template commands:

- `oedit`, `ocreate`, `oset`, `odesc`, `odelete`, `ostat`

Entity template commands:

- `medit`, `mcreate`, `mset`, `mdesc`, `mdelete`, `mstat`

Spawn commands:

- `spawnedit`, `spawncreate`, `spawnset`, `spawndelete`, `spawnstat`

World inspection commands:

- `zstat`, `astat`, `wstat`

## Draft vs. Live Data

Builder edits create draft JSON records. Movement, interaction, rendering, and spawning remain runtime-owned and must continue to use runtime validation. Builder features can be discovered by draft-aware look/examine-style flows without hardcoding individual feature IDs.

## Validation

`builder validate` reports duplicate/missing IDs where represented in draft data, missing names, broken room exits, missing spawn entity templates, invalid wear slots, invalid entity types, invalid JSON/plugin data, and world-package compliance issues that can be checked safely from drafts.

## Audit, History, and Snapshots

Every Builder change records timestamp, account ID, character ID, world ID, action, target type, target ID, before/after snapshots where feasible, and reason when supplied. Audit JSONL files are written under `builder/audit` and mirrored to `builder/history`. Snapshots copy current draft files to a timestamped folder under `builder/snapshots`.

## Web and Telnet

Builder commands use normal command input. Web output remains semantic text/HTML through existing rendering paths, and telnet output remains plain/ANSI. A full web Builder UI is future work.

## Explicit Non-Goals

Phase 4A does not implement AI Builder, combat, quests, shops, spellcasting, or a redesigned UI.
