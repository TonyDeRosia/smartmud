from pathlib import Path

from app.intelligence import CampaignIntelligenceLibrary


def test_manifest_creation_seeds_core_files(tmp_path: Path) -> None:
    library = CampaignIntelligenceLibrary(tmp_path / "intelligence")

    sources = library.list_sources()

    assert (tmp_path / "intelligence" / "manifest.json").exists()
    assert (tmp_path / "intelligence" / "core" / "player_agency.md").exists()
    assert {source["category"] for source in sources} == {"core"}
    assert any(source["id"] == "player_agency" for source in sources)


def test_import_listing_enable_disable_and_priority_order(tmp_path: Path) -> None:
    source_a = tmp_path / "a.md"
    source_b = tmp_path / "b.txt"
    source_a.write_text("alpha", encoding="utf-8")
    source_b.write_text("bravo", encoding="utf-8")
    library = CampaignIntelligenceLibrary(tmp_path / "intelligence")

    imported_a = library.import_source(source_a, title="Alpha", priority=5)
    imported_b = library.import_source(source_b, title="Bravo", priority=25)
    library.set_enabled(imported_a["id"], False)

    listed = library.list_sources()
    enabled = library.read_enabled_sources()

    assert listed[0]["priority"] >= listed[-1]["priority"]
    assert imported_b["id"] in [source["id"] for source in enabled]
    assert imported_a["id"] not in [source["id"] for source in enabled]
    assert (tmp_path / "intelligence" / imported_a["filename"]).read_text(encoding="utf-8") == "alpha"


def test_replace_source_preserves_manifest_identity(tmp_path: Path) -> None:
    original = tmp_path / "original.md"
    replacement = tmp_path / "replacement.md"
    original.write_text("original", encoding="utf-8")
    replacement.write_text("replacement", encoding="utf-8")
    library = CampaignIntelligenceLibrary(tmp_path / "intelligence")
    imported = library.import_source(original, title="Original", priority=1)

    replaced = library.replace_source(imported["id"], replacement, title="Updated")

    assert replaced["id"] == imported["id"]
    assert replaced["title"] == "Updated"
    assert (tmp_path / "intelligence" / replaced["filename"]).read_text(encoding="utf-8") == "replacement"


def test_core_guidance_uses_enabled_core_priority_order(tmp_path: Path) -> None:
    library = CampaignIntelligenceLibrary(tmp_path / "intelligence")
    library.set_priority("memory_rules", 2000)
    library.set_enabled("player_agency", False)

    guidance = library.build_core_guidance()

    assert guidance.find("Memory Rules") < guidance.find("Dialogue Realism")
    assert "Player Agency" not in guidance


def test_campaign_guidance_includes_core_by_default_and_excludes_imports(tmp_path: Path) -> None:
    source = tmp_path / "pack.md"
    source.write_text("pack-only guidance", encoding="utf-8")
    library = CampaignIntelligenceLibrary(tmp_path / "intelligence")
    library.import_source(source, title="Pack", category="packs", priority=5000)

    guidance, used = library.build_guidance(enabled_source_ids=[])

    assert "Player Agency" in guidance
    assert "pack-only guidance" not in guidance
    assert {item["category"] for item in used} == {"core"}


def test_selected_campaign_guidance_injects_after_core_and_respects_priority(tmp_path: Path) -> None:
    low = tmp_path / "low.md"
    high = tmp_path / "high.md"
    low.write_text("low pack guidance", encoding="utf-8")
    high.write_text("high import guidance", encoding="utf-8")
    library = CampaignIntelligenceLibrary(tmp_path / "intelligence")
    low_entry = library.import_source(low, title="Low Pack", category="packs", priority=10)
    high_entry = library.import_source(high, title="High Import", category="imported", priority=99)

    guidance, used = library.build_guidance(enabled_source_ids=[low_entry["id"], high_entry["id"]])

    assert guidance.find("Memory Rules") < guidance.find("High Import")
    assert guidance.find("High Import") < guidance.find("Low Pack")
    assert [item["id"] for item in used if item["category"] != "core"] == [high_entry["id"], low_entry["id"]]


def test_disabled_selected_campaign_source_does_not_inject(tmp_path: Path) -> None:
    source = tmp_path / "disabled.md"
    source.write_text("disabled guidance", encoding="utf-8")
    library = CampaignIntelligenceLibrary(tmp_path / "intelligence")
    entry = library.import_source(source, title="Disabled", category="imported", priority=50)
    library.set_enabled(entry["id"], False)

    guidance, used = library.build_guidance(enabled_source_ids=[entry["id"]])

    assert "disabled guidance" not in guidance
    assert entry["id"] not in [item["id"] for item in used]


def test_delete_source_removes_manifest_entry_and_index_chunks(tmp_path: Path) -> None:
    library = CampaignIntelligenceLibrary(tmp_path / "intelligence")
    source = tmp_path / "delete_me.md"
    source.write_text("delete-only guidance", encoding="utf-8")
    entry = library.import_source(source, title="Delete Me", category="imported")
    assert any(chunk["source_id"] == entry["id"] for chunk in library._load_index()["chunks"])

    library.delete_source(entry["id"])

    assert entry["id"] not in [item["id"] for item in library.list_sources()]
    assert not any(chunk["source_id"] == entry["id"] for chunk in library._load_index()["chunks"])
