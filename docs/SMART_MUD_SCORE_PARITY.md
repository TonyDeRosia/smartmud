# Smart MUD SCORE Parity

Status: Partial. This pass corrects the existing SCORE renderer and snapshot contract without starting Phase 15A or zone reset work.

## Approved visible mortal fixture

```text
╔═══════════════════════════════════════════════════════════════════════════════╗
║ CHARACTER STATUS                                                              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Name: Aster                  Title: the Bold                                  ║
║ Race: Human                  Class: Warrior                                   ║
║ Level: 7                     Age: 22 years old                                ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║ Exp: 12345                           TNL: 55                                  ║
║                                                                               ║
║ Carry Capacity: 42 / 100 (Moderate)                                           ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Base Stats: Str 14 (+0) Dex 13 (+0) Con 12 (+0)                               ║
║             Int 11 (+0) Wis 10 (+0) Cha 8 (+0)                                ║
║                                                                               ║
║ Armor: 12       Evasion: 7     Spell Saves: 10                                ║
║                                                                               ║
║ Offense: Hitroll +4 Damroll +3 Accuracy: 82%                                  ║
║                                                                               ║
║ Critical hit: 5 Critical Spell: 2 Critical Heal: 1                            ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Currencies                                                                    ║
║ Gold:       99 Diamonds:      0 Glory:      0 Bank:        4                  ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Quests completed: 0                                           Quest Points: 9 ║
║ Not currently on a quest.                                                     ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Play time: 1 day, 2 hours                                                     ║
║ Status: Standing Hunger: Satisfied Thirst: Quenched                           ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## Intentional Smart MUD divergence

Implemented: normal SCORE omits current HP, maximum HP, current Mana, maximum Mana, current Move/Stamina, maximum Move/Stamina, and Alignment. These systems remain canonical prompt/resource/combat systems and are not moved elsewhere in SCORE.

## Field authority matrix

| Field | Status | Canonical authority | Persistence source | Gameplay consumer | Projection dependency | Invalidation reason |
|---|---|---|---|---|---|---|
| Name/title | Implemented | CharacterDisplaySnapshotService | characters/data identity | command/session identity | identity,title | identity/title mutation |
| Race | Partial | progression/race assignment surfaced through CharacterDisplaySnapshotService | actor_progression_state.race_id or character data | attributes/progression | race, world definitions | race mutation |
| Class/class track | Partial | progression/class-track assignment surfaced through CharacterDisplaySnapshotService | actor_progression_state primary_class_id/primary_class_track_id or character data | progression/abilities | class,class track, world definitions | class mutation |
| Level/XP/TNL | Implemented | ProgressionDisplayAdapter/ProgressionService | actor_progression_state or legacy character fields | leveling | progression | XP/level mutation |
| Age/birthday | Partial | snapshot age provider | character birth fields plus world calendar when available | calendar/lifecycle | birth state, calendar | calendar/birth mutation |
| Carrying | Implemented | CombatStatService carrying snapshot / CarryingDisplaySource | inventory/equipment runtime | encumbrance | carrying,equipment,inventory | item/equipment mutation |
| Attributes | Implemented | CombatStatService/AttributeDisplaySource | character attributes/equipment/effects | combat/resource formulas | attributes,effects,equipment | stat/effect/equipment mutation |
| Armor/evasion/spell saves | Implemented | CombatStatService | formula definitions and actor state | combat hit/spell resolution | combat statistics | combat-stat mutation |
| Hitroll/damroll/accuracy | Implemented | CombatStatService | formula definitions and actor state | hit/damage resolution | combat statistics | combat-stat mutation |
| Unarmed dice | Partial | CombatStatService unarmed_profile | body/combat formulas | unarmed attacks | weapon state, unarmed profile | equipment/combat formula mutation |
| Criticals | Implemented | CombatStatService | formula definitions and actor state | melee/spell/heal critical resolution | critical statistics | combat-stat mutation |
| Currencies | Implemented | EconomyService/CurrencyDisplaySource | economy balances | shops/rewards/banking | currencies, bank balance | economy mutation |
| Quests | Partial | QuestService snapshot data | actor_quest_instances/history | journal/rewards | quest history, active quest, Show VNUMs | quest mutation |
| Play time | Implemented | session lifecycle snapshot time | accumulated played seconds plus active session | session accounting | play-time display generation | session tick/save |
| Status/survival/conditions | Partial | actor runtime/survival snapshot | actor posture/survival state | movement/combat/survival | position,target,hunger,thirst,intoxication | actor/survival mutation |
| Summonable/show VNUMs | Partial | player preference authority | preferences/identity snapshot | summon permission/builder display | preferences | preference mutation |
| Immortal poof/builder zone | Partial | identity and Builder editing context snapshot | character prefs/builder context | immortal movement/builder | poof text,builder zone | preference/builder mutation |

## Golden fixture coverage

Implemented focused coverage: framed width, left-aligned title, exact dividers and blank rows, no HP/Mana/Move/Alignment row, no modern sections, no unavailable/not implemented placeholders, fixed currency order, numeric spell saves, zero/normal play-time formatting, immortal poof and Builder zone rows.

Partial remaining fixture expansion: separate complete-string cases for every requested encumbrance threshold, active quest VNUM, birthday, sitting/fighting, condition notices, and transport visible-text equivalence.

## Windows testing status

Not run in this Linux container. Manual Windows acceptance should enter existing `Kraevok`, run `score`, and compare visible text after stripping ANSI/HTML to the fixed 81-column contract. No SQLite reset, world recreation, or character recreation is required by this code change.

## Remaining differences

Partial: canonical persisted Kraevok data was not present in this container, so no one-time repair command was applied. If live Windows Kraevok still lacks race/class/birth fields, use existing progression/admin tools to assign valid world definitions without changing the renderer. Valid IDs must be selected from `data/worlds/shattered_realms` progression definitions in the target checkout.
