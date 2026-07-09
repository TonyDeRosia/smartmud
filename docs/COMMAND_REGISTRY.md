# Smart MUD Command Registry

Smart MUD owns command metadata in `engine.command_registry.CommandRegistry`. The registry is the canonical source for command names, aliases, categories, access constraints, implementation status, help text, and transport safety.

## Philosophy

Smart MUD is not a tbaMUD or CircleMUD clone. It is a modern runtime with web and telnet-safe command handling. Classic MUD coverage is still tracked deliberately so players can try familiar commands without receiving accidental `Unknown command` responses for planned systems.

## Metadata

Each command records: `command`, `aliases`, `category`, `minimum_position`, `minimum_role`, `status`, `handler`, `short_help`, `long_help`, `implemented`, `placeholder`, `future_phase`, `transport_safe`, `admin_only`, and `builder_only`.

## Categories and statuses

Categories include movement, informational, interaction, object, equipment, communication, social, character, magic, combat, group, economy, quest, clan, toggle, builder, admin, and system.

Statuses include implemented, placeholder, planned, intentionally_omitted, future_builder, future_admin, future_combat, future_magic, future_economy, and future_quest.

## Placeholders

A placeholder command is intentionally recognized and returns useful text without activating a future system. For example, mount commands explain mounts are not implemented yet, while combat commands remain tracked as future combat rather than implemented behavior.

## Commands and help

`commands` groups visible commands by registry category and hides admin/builder/future commands from normal players. `commands all` and `commands planned` may expose planned registry entries that are still safe to display. `help <command>` falls back to registry metadata when no full helpfile exists.

## Future upgrades

Future systems should upgrade a placeholder by changing its registry status and wiring its handler, preserving aliases and help text wherever possible.

## Phase 3E examination and interaction polish

Registered player commands now route through runtime-owned command handling and must execute, show registry usage, return a clean placeholder, or explicitly describe unavailable future work. The examination layer supports room, self, object, entity, direction, and room-feature targets; `identify`, `read`, and `use` publish EventBus events and return semantic output. See `docs/EXAMINATION_AND_INTERACTION.md`.

## Phase 4A Builder Foundation

Smart MUD supports an in-game Builder foundation for authorized `builder`, `admin`, and `owner` roles. Builder commands are registered in the command registry and are hidden from normal players. Draft edits are persisted under `worlds/<world_id>/builder/` rather than being written directly to live world package files.

The Builder workspace uses `audit`, `history`, `snapshots`, `exports`, `imports`, and `templates` folders. Room, exit, feature, item template, entity template, and spawn edits go through Builder services so runtime validation and permission checks remain authoritative. `builder validate` checks draft consistency; `builder save` creates a safe export; `builder reload` reloads drafts where safe; `builder snapshot` captures the current draft state; and `builder history` reads audit records.

Future work may add a richer semantic web Builder UI and AI-assisted Builder tools, but Phase 4A intentionally does not add AI Builder, combat, quests, shops, or spellcasting.

## Phase 4B Builder runtime navigation note

Builder-created draft rooms now participate in a runtime world graph overlay for builder/admin/owner users with Builder Mode enabled. Runtime lookup merges live world package rooms with BuilderWorkspace drafts, with drafts overriding live rooms for builders only. `goto`, `look`, `rooms`/`rlist`, `rfind`/`rsearch`, `dig`, `link`, `unlink`, and `map`/`rmap` use this merged lookup and the canonical room renderer. Normal players do not see builder-only metadata or draft-only rooms. Draft saves export BuilderWorkspace content; promotion to live packages is not implemented yet. See `docs/BUILDER_NAVIGATION.md`.
