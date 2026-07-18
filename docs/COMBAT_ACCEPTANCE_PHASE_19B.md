# Phase 19B representative acceptance transcript

```
> score
HP: 30/30   Position: standing
> look
Forest Wolf (HP 500/500, natural attack: bite)
> kill forest wolf
You punch Forest Wolf for 1 damage.
> [advance one configured violence pulse]
Forest Wolf bites you for 4 damage.
<29/30hp ...>
> [advance three more pulses]
You punch Forest Wolf for 1 damage.
Forest Wolf bites you for 4 damage.
... (one action at most per participant per pulse)
> score
HP: 22/30
> north
You are too busy fighting to move normally.
> [defeat wolf]
Your attack defeats Forest Wolf.
Forest Wolf collapses and dies.
Combat ends; position: standing.
```

The async browser packet contains the delayed bite and updated prompt. Telnet
receives the same plain-text lines. On restart active encounters, targets, and
waits are normalized away; persisted HP remains subject to the existing
character/entity policy. No corpse, XP, loot, flee, assist, rescue, skill, or
spell implementation is claimed by this phase.
