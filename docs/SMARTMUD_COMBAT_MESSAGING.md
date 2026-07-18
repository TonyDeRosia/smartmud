# Combat messaging — Phase 19B

Combat resolution formats attacker, victim, and observer perspectives using
the Phase 19A selected weapon/natural attack profile. `CombatRuntimeService`
queues each heartbeat message once per eligible active character, excluding
attacker/victim observer duplicates. Packets are sequence ordered and include
a fresh prompt/resource snapshot for attack, defeat, and combat-end changes.

Browser polling drains these packets after the original command response.
Telnet consumes the same ordered text payload through its session transport;
combat packets intentionally carry plain text and no raw HTML. Disconnect and
logout remove resident actor state so later combat cannot queue output to it.

The EventBus publishes round, attack, damage, wait, skip, and end events from
the combat runtime. Existing event names remain compatible; Phase 19B also
emits dotted `combat.wait.applied`, `combat.wait.expired`, and
`combat.actor.skipped` diagnostics for future ability gateways.
