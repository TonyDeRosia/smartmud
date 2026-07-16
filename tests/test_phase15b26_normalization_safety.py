from types import SimpleNamespace
from smart_mud.builder import BuilderService, BuilderWorkspace, NormalizationFailureInjector


def actor():
    return SimpleNamespace(id="builder", name="Builder", account_id="acct", session_id="sess", role="admin", account_role="admin", world_id="shattered_realms", room_id="room")


def seed(ws):
    d = ws.load("shattered_realms")
    d["areas"]["starter_guildlands"] = {"id":"starter_guildlands","name":"Starter Guildlands","world_id":"shattered_realms"}
    d["zones"]["guildhall_crossing"] = {"id":"guildhall_crossing","name":"Guildhall Crossing","area_id":"starter_guildlands","world_id":"shattered_realms","vnum_start":1000,"vnum_end":1029}
    d["rooms"]["room"] = {"id":"room","name":"Room","vnum":1000,"area_id":"starter_guildlands","zone_id":"guildhall_crossing","world_id":"shattered_realms"}
    d["entities"]["training_rat"] = {"id":"training_rat","name":"Training Rat","default_room_id":"room"}
    d["items"]["training_sword"] = {"id":"training_sword","name":"Training Sword","vnum":1300,"area_id":"starter_guildlands","zone_id":"guildhall_crossing"}
    d["spawns"]["rat_spawn"] = {"id":"rat_spawn","room_id":"room","entity_id":"training_rat","vnum":1700,"area_id":"starter_guildlands","zone_id":"guildhall_crossing"}
    ws.save_drafts("shattered_realms", d)


def test_candidate_verification_uses_explicit_records_and_preserves_method(tmp_path):
    ws = BuilderWorkspace(worlds_dir=tmp_path / "worlds"); svc = BuilderService(ws); a = actor(); seed(ws)
    original = svc._normalization_records
    plan = svc.normalization_plan(a)
    candidate, errors = svc._candidate_drafts_for_plan(a, plan)
    current_records = svc._normalization_records(a)[0]
    assert svc._normalization_records.__func__ is original.__func__
    assert not errors
    assert candidate["entities"]["training_rat"]["zone_id"] == "guildhall_crossing"
    assert "zone_id" not in current_records["entities"]["training_rat"]


def test_reference_index_reports_incoming_outgoing_and_unresolved(tmp_path):
    ws = BuilderWorkspace(worlds_dir=tmp_path / "worlds"); svc = BuilderService(ws); a = actor(); seed(ws)
    d = ws.load("shattered_realms")
    d["spawns"]["bad_spawn"] = {"id":"bad_spawn","room_id":"missing_room","entity_id":"training_rat","vnum":1701,"area_id":"starter_guildlands","zone_id":"guildhall_crossing"}
    ws.save_drafts("shattered_realms", d)
    index = svc._build_reference_index(a)
    assert index.incoming["rooms:room"]
    assert index.outgoing["spawns:bad_spawn"]
    assert any(r.target_id == "missing_room" for r in index.unresolved)
    issues = svc._verify_issues(a, reference_index=index)
    assert any(i["code"] == "reference_missing" and i["id"] == "bad_spawn" for i in issues)


def test_transactional_restore_writes_restore_journal_and_exact_hashes(tmp_path):
    ws = BuilderWorkspace(worlds_dir=tmp_path / "worlds"); svc = BuilderService(ws); a = actor(); seed(ws)
    before = svc._draft_file_hashes("shattered_realms")
    ready = svc.normalize_command(a, ["apply"]); assert not ready.ok
    applied = svc.normalize_command(a, ["confirm", "1"]); assert applied.ok, applied.message
    restored = svc._restore_normalization_snapshot_internal("shattered_realms", applied.data["snapshot_id"], reason="test", actor=a)
    assert restored.ok, restored.errors
    assert svc._draft_file_hashes("shattered_realms") == before
    txs = svc.normalize_command(a, ["restore-transactions"])
    assert txs.ok and "restoretx_" in txs.message


def test_restore_recovery_command_handles_failed_restore_journal(tmp_path):
    ws = BuilderWorkspace(worlds_dir=tmp_path / "worlds"); svc = BuilderService(ws); a = actor(); seed(ws)
    svc.normalize_command(a, ["apply"]); applied = svc.normalize_command(a, ["confirm", "1"]); assert applied.ok
    snap = svc._find_normalization_snapshot("shattered_realms", applied.data["snapshot_id"])
    missing = snap / "entity_templates.json"
    backup = missing.read_bytes(); missing.unlink()
    failed = svc._restore_normalization_snapshot_internal("shattered_realms", applied.data["snapshot_id"], reason="forced_failure", actor=a)
    assert not failed.ok
    missing.write_bytes(backup)
    recovered = svc.normalize_command(a, ["recover"])
    assert recovered.ok
    assert "restoretx_" in recovered.message


def test_failure_injector_exposes_requested_matrix_points():
    points = {"CANDIDATE_BUILD","CANDIDATE_VERIFY","STAGING_DIRECTORY_CREATE","STAGING_WRITE_FIRST","STAGING_WRITE_MIDDLE","STAGING_WRITE_LAST","STAGING_PARSE","STAGING_HASH","SNAPSHOT_DIRECTORY_CREATE","SNAPSHOT_MANIFEST_WRITE","SNAPSHOT_FILE_COPY_FIRST","SNAPSHOT_FILE_COPY_MIDDLE","SNAPSHOT_FILE_COPY_LAST","JOURNAL_PREPARE","COMMIT_FIRST_REPLACE","COMMIT_MIDDLE_REPLACE","COMMIT_LAST_REPLACE","POST_COMMIT_RELOAD","POST_COMMIT_HASH","POST_COMMIT_VERIFY","AUTO_RESTORE_PREPARE","AUTO_RESTORE_FIRST_REPLACE","AUTO_RESTORE_MIDDLE_REPLACE","AUTO_RESTORE_LAST_REPLACE","AUTO_RESTORE_VERIFY"}
    injector = NormalizationFailureInjector(points)
    for point in sorted(points):
        try:
            injector.check(point)
        except RuntimeError as exc:
            assert point in str(exc)
    assert set(injector.triggered) == points
