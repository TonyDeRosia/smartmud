# tbaMUD-Inspired Command Parity Map

Smart MUD is not a tbaMUD clone. This map tracks familiar classic MUD commands so compatibility is deliberate and safe.

| Command | Aliases | Smart MUD status | Future phase | Notes |
|---|---|---:|---|---|
| look | l, glance, scan | implemented |  | Room/target rendering. |
| examine | exa | implemented |  | Target inspection. |
| exits |  | placeholder |  | Lists visible exits when runtime context provides them. |
| score | sc | implemented |  | Character summary. |
| worth |  | implemented |  | Gold summary. |
| inventory | inv, i | implemented |  | Inventory display. |
| equipment | eq | implemented |  | Equipment display. |
| affects | aff | implemented |  | Active affects. |
| skills | sk | implemented |  | Skill list. |
| spells | sp | implemented | Magic | Empty until magic grows. |
| commands | cmds | implemented |  | Registry-driven command list. |
| help | h | implemented |  | Registry metadata fallback. |
| who |  | implemented |  | Online list foundation. |
| where |  | placeholder |  | Location-safe response. |
| weather |  | placeholder | Weather | Safe weather text. |
| time |  | placeholder |  | Safe world time text. |
| consider | con | placeholder | Combat | No combat starts. |
| diagnose |  | placeholder | Combat | Safe assessment only. |
| levels |  | placeholder | Character | Level table future work. |
| get | take, pickup, grab | implemented |  | Object pickup. |
| drop |  | implemented |  | Object drop. |
| put |  | placeholder | Object | Container support future. |
| give |  | placeholder | Economy/interaction | Transfer systems future. |
| wear |  | implemented |  | Equipment. |
| remove | rem | implemented |  | Equipment. |
| wield |  | implemented |  | Equipment. |
| hold |  | implemented |  | Equipment. |
| eat/drink/taste/fill/pour/open/close/lock/unlock/pick/read/use/identify | id for identify | placeholder | Object/interaction | Safe responses until deeper systems exist. |
| north/south/east/west/up/down | n/s/e/w/u/d | implemented |  | Movement. |
| enter/leave/sit/stand/rest/sleep/wake/run/walk |  | implemented/placeholder |  | Position and movement foundations. |
| follow/unfollow/mount/dismount |  | placeholder | Group/mounts | No mount/group systems yet. |
| say/tell/reply/ask/whisper/emote/gossip/shout/holler/group say/socials |  | implemented/placeholder | Communication | Channels are safe placeholders where missing. |
| practice/train/spellbook/study/levels | prac | placeholder/future_magic | Character/Magic | No spellcasting added. |
| brief/compact/autoexits/afk |  | implemented | Preferences | Session/character preference toggles. |
| autoloot/autogold/autosplit/automap/norepeat/notell/nosummon/prompt |  | placeholder/implemented | Combat/Economy/UI | Preferences or explanatory placeholders only. |
| redit/oedit/medit/zedit/qedit/aedit/olc |  | future_builder | Builder Mode | Tracked and hidden from normal players. |
| goto/load/purge/stat/vnum/wizhelp |  | future_admin | Admin | Restricted. |
| kill/hit/flee/assist/rescue/kick/bash/backstab/cast/quaff/recite |  | future_combat/future_magic | Combat/Magic | Tracked only; no combat or spellcasting implemented. |
