# Legacy Entity Source Retirement

Phase 5A retires legacy room NPC declarations as active gameplay content. A legacy declaration such as `room.npcs`, `room.mobs`, `room.entities`, or an entity template `default_room_id` is now a compatibility input only: it is normalized to a deterministic canonical spawn declaration, materialized once, and then represented in gameplay by SQLite-backed runtime entity instances.

## Runtime invariant

Normal gameplay uses this path only:

`legacy declaration -> normalized spawn declaration -> content materialization -> entity_instances row -> canonical room-content query -> rendering/targeting/dialogue`

The canonical `entity_instances` collection contains runtime rows only. It must not contain templates, spawn declarations, legacy declarations, or materialization records. Builder diagnostics may show those source collections separately.

Name-based deduplication is forbidden. Two runtime rows with the same name are two visible NPCs if both are alive and visible.

## Compatibility and precedence

Legacy-only worlds remain compatible because startup produces a stable spawn ID of the form `legacy_<room_id>_<template_id>`. If an equivalent canonical spawn already exists for the same room, template, and quantity, the canonical spawn supersedes the legacy declaration. The legacy declaration remains diagnostic-only.

## Upgraded databases

If an upgraded database already has the matching runtime entity row and lacks a materialization record, materialization adopts that row and records its instance ID. Extra matching rows are reported as duplicate candidates rather than hidden or deleted.

## Diagnostics

Use `rcontents`, `sstat`, `mstat`/`estat`, and `entityaudit here` to inspect runtime instances, canonical spawns, legacy declarations, materialization records, and duplicate risks. A healthy room reports `Entity runtime source integrity: PASS` and `Legacy declarations contributing to gameplay: no`.
