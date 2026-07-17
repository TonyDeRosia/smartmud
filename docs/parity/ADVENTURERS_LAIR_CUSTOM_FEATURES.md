# Adventurer's Lair Custom Features — Phase 16A

| Feature | Purpose | Source evidence | Data/help references | Smart MUD support | Priority | Recommendation |
| AI actor brain/reactions | richer mobile decision behavior | `src/ai_actor.c`, `src/ai_actor_brain.c`, `src/ai_reactions.c` | mob specs/world mobs | partial via `engine/combat_behavior.py`, `engine/living_world.py` | high | modernize as behavior-profile service |
| Critical hits | expanded combat outcomes | `src/criticalhits.c/h`, `src/fight.c` integration | combat messages | partial | high | reproduce behavior through combat formula/message services |
| Class tracks | customized advancement | `src/classtrack.c/h`, `src/class.c` | player/class data | partial/exceeds structurally | medium | migrate into progression/training services |
| Accounts | account layer beyond flat players | `src/accounts.c/h`, README account path | `lib/plrfiles/accounts/` | partial | medium | modernize account/session service |
| ASCII map | player-visible area map | `src/asciimap.c/h` | room exits/sectors | partial via rendering/pathing | medium | modern renderer over canonical room graph |
| DG scripts and OLC | content behavior hooks | `src/dg_*.c`, `src/*edit.c` | world trigger files | missing | high | implement safe script/trigger runtime, not C interpreter clone |
