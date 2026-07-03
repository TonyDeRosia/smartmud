# Smart MUD tbaMUD Command and Display Audit

Reference reviewed by file family: `src/interpreter.c`, `src/act.informative.c`, `src/act.item.c`, `src/act.movement.c`, `src/act.offensive.c`, `src/act.other.c`, `src/act.social.c`, `src/act.wizard.c`, `src/class.c`, `src/fight.c`, `src/magic.c`, `src/spell_parser.c`, `src/shop.c`, `src/spec_procs.c`, and `src/quest.c` when present. This document records design parity only; no C code is copied.

## Runtime systems required

* Command registry with aliases, category filtering, staff visibility, and deterministic/AI/hybrid routing.
* Terminal display builders for classic MUD sheets and line-oriented output.
* SQLite character persistence for role, optional immortal level, and builder enablement.
* Room, item, shop, combat, spell, skill, quest, affect, and social runtimes.
* Semantic color roles for rooms, exits, objects, scores, equipment, prompts, combat, magic, skills, quests, warnings, and errors.

## Normal player commands

| Command / aliases | Category | Expected output/display | Routing | Status | Required systems |
|---|---|---|---|---|---|
| north/n, south/s, east/e, west/w, up/u, down/d, northeast/ne, northwest/nw, southeast/se, southwest/sw, in/enter, out/leave, go | Movement | Movement echo and rendered destination room | deterministic | implemented now | room exits, doors |
| run | Movement | Direction prompt or future rapid movement | deterministic | scaffolded now | pathing/combat |
| flee | Movement/Combat | Combat escape result | hybrid | scaffolded now | combat state |
| exits | Movement | Obvious exits list | deterministic | implemented now | room exits |
| look/l, examine/exa, inspect, read, scan | Informative | Room, target, readable, or nearby scan text | deterministic/hybrid | implemented/scaffolded now | world registry, object descriptions |
| where, map, areas, time, weather | Informative | Location, local map, area list, time, weather display | deterministic | implemented now | world metadata, time/weather runtime |
| score/sc, worth, stats, attr, affects, resists | Informative | Character score, worth, stats, affects, resist sheets | deterministic | implemented now | character state, affects |
| inventory/i/inv, equipment/eq, gold | Informative | Inventory grouping, equipment slots, currency | deterministic | implemented now | inventory/equipment |
| who, finger | Informative | Online list / character profile | deterministic | finger implemented; who deferred | player directory/session list |
| help, commands/com, socials, history | Informative | Help entry, grouped commands, social list, command history | deterministic | implemented now | registry/history |
| spells/sp, spellbook, skills/sk, abilities, cooldowns/cd | Magic/Character | Known spells/skills with costs, ranks, cooldowns | deterministic | implemented/scaffolded now | ability registry/cooldowns |
| cast/c, spellup, buffup, recite, quaff, use | Magic/Items | Cast usage/effect, routine unavailable, item use messages | hybrid | scaffolded now | magic engine/items |
| get/take/grab, get all, drop, drop all, junk, put, give | Items | Item transfer/equipment-safe messages | deterministic/hybrid | implemented/scaffolded now | inventory/room items |
| wear, wield, hold, remove | Items | Equipment changed message and slots | deterministic | implemented now | inventory/equipment |
| eat, drink, sip, taste, open, close, lock, unlock, pick | Items | Consumption or door interaction messages | deterministic | door implemented; consumption scaffolded | consumables/doors |
| kill/k, hit, attack, assist, rescue, consider/con, appraise, bash, kick, backstab, hide, sneak, steal | Combat | Target prompts, comparison, combat maneuver outcomes | hybrid | scaffolded now | combat/mob runtime |
| say/', tell, reply, ask, talk, whisper, shout, gossip, emote/:, pose, group, gsay | Social | Speech/social echo and AI-routed NPC handling | AI-routed/hybrid | partially implemented; additional socials documented | dialogue/social runtime |
| practice/prac, train, study, level, levels | Progression | Trainer or level display | deterministic | scaffolded now | trainer/progression |
| quest/quests, journal | Progression | Quest and journal display | deterministic | implemented now | quest runtime |
| list, browse, buy, sell, value | Shop | Shop inventory or no-shopkeeper messages | deterministic | scaffolded now | shop runtime |
| save, quit, settings, clear/cls | Utility | Save/quit/settings/clear messages | deterministic | implemented/scaffolded now | save/session |

## Admin and builder commands (hidden from normal players)

| Command | Category | Expected output/display | Routing | Status | Required systems |
|---|---|---|---|---|---|
| wizhelp | Admin | Staff-only command list | deterministic | implemented safe scaffold | roles |
| goto, transfer, load, purge, stat, set, restore, advance, shutdown | Admin | Permission-gated safe scaffold; no destructive effect | deterministic | implemented safe scaffold | roles, future admin services |
| redit, oedit, medit, zedit, sedit, aedit, dig, build | Builder | Permission-gated safe scaffold | deterministic | implemented safe scaffold | roles, future builders |

Normal command listings and normal help must not expose this table at runtime. Admins/builders can invoke their commands directly after privilege checks.

## Display parity findings

* tbaMUD-style gameplay is line-oriented, concise, and terminal-first. Smart MUD display builders now live in `engine/mud_displays.py` and return semantic MUD text, not web cards.
* Required display sheets: score, worth, finger, inventory, equipment, spells, skills, abilities, affects, resists, who, commands, help, socials, quests, journal, areas, map, time, weather, practice, train, shops/list, consider, and history.
* Display commands should favor stable deterministic formatting; AI should embellish conversations and freeform actions only after deterministic command parsing fails or a command is explicitly hybrid.
* Semantic color roles should be consumed by terminal rendering, not embedded as web card layout.

## Deferred full systems

* Full combat rounds, special procedures, class trainers, banking, persistent who-list, destructive wizard commands, online editing, full shop inventories, scripted socials, memorized spells, spell components, and production weather/time calendars remain future work.
