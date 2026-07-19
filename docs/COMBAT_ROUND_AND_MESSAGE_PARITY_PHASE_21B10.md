# Phase 21B10: combat-round and spell-message foundation

## Implemented foundation

* Canonical combat timing remains one 2.0-second scheduler interval: the
  runtime's 100 ms pulse dispatches violence every 20 pulses. Commands,
  ability execution, rendering, browser polling, and projection generation do
  not dispatch rounds.
* Magic Missile carries `source_type=spell` and `source_category=spell` through
  its combat request. Spell narration is selected from those fields rather than
  a natural weapon or narrative string.
* A nonterminal hostile spell starts/updates a resident engagement but performs
  no physical opening attack. Its first possible basic attacks are on the next
  eligible violence pulse. A terminal spell closes combat and says, for
  example, `Your Magic Missile defeats Forest Wolf.`
* Message ownership is: ability layer (cast acknowledgement), combat/damage
  layer (impact), lifecycle/death layer (corpse and cleanup), transport layer
  (HTML/ANSI/plain conversion). Combat output packets retain sequence, pulse,
  encounter, and round metadata.

## Evidence and remaining gaps

`tests/test_spell_vs_physical_damage_messages.py` covers terminal spell
attribution and nonterminal engagement-without-a-free-swing at the real web
adapter boundary. Existing Phase 21B production acceptance tests cover durable
death receipts and Browser/Telnet parity. The complete requested C-source
matrix, custom Magic Missile formula, custom severity thresholds, corpse timer
conversion, and all thirteen requested scenarios remain unverified until the
actual supplied C archive is available; therefore Phase 21B is **not closed**
and Phase 21C combat-command work is **not yet safe** to begin.
