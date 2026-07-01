"""Developer-managed campaign intelligence source library."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ALLOWED_SOURCE_SUFFIXES = {".txt", ".md", ".json"}
CORE_SEEDS = {
    "player_agency.md": ("Player Agency", "Never decide the player character's actions, intent, emotions, or dialogue. Resolve explicit player choices and hand control back cleanly."),
    "dialogue_realism.md": ("Dialogue Realism", "Write dialogue as direct speech with character-specific voice. Avoid summarizing what the player says when exact wording is provided."),
    "npc_identity.md": ("NPC Identity", "Preserve established NPC names, roles, relationships, and motivations. Do not rename or merge NPCs once introduced."),
    "world_consistency.md": ("World Consistency", "Keep locations, factions, consequences, and physical scene details consistent with established campaign facts."),
    "memory_rules.md": ("Memory Rules", "Prefer current scene facts and recent player actions over stale context. Treat explicit player corrections as high-priority updates."),
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(value: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9_.-]+", "_", value.strip()).strip("._-").lower()
    return clean or "source"


@dataclass(frozen=True)
class IntelligenceSource:
    id: str
    filename: str
    title: str
    category: str
    priority: int
    enabled: bool
    imported_at: str
    updated_at: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "IntelligenceSource":
        return cls(
            id=str(payload.get("id", "")).strip(),
            filename=str(payload.get("filename", "")).strip(),
            title=str(payload.get("title", "")).strip(),
            category=str(payload.get("category", "packs")).strip() or "packs",
            priority=int(payload.get("priority", 0) or 0),
            enabled=bool(payload.get("enabled", True)),
            imported_at=str(payload.get("imported_at", "")).strip(),
            updated_at=str(payload.get("updated_at", "")).strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "filename": self.filename,
            "title": self.title,
            "category": self.category,
            "priority": self.priority,
            "enabled": self.enabled,
            "imported_at": self.imported_at,
            "updated_at": self.updated_at,
        }


class CampaignIntelligenceLibrary:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.manifest_path = self.root / "manifest.json"
        self.ensure_initialized()

    def ensure_initialized(self) -> None:
        for category in ("core", "packs", "imported"):
            (self.root / category).mkdir(parents=True, exist_ok=True)
        entries = self._load_manifest_entries(create_if_missing=True)
        by_filename = {entry.filename: entry for entry in entries}
        changed = False
        now = utc_now_iso()
        for index, (filename, (title, body)) in enumerate(CORE_SEEDS.items(), start=1):
            path = self.root / "core" / filename
            if not path.exists():
                path.write_text(f"# {title}\n\n{body}\n", encoding="utf-8")
            rel = f"core/{filename}"
            if rel not in by_filename:
                entries.append(IntelligenceSource(
                    id=Path(filename).stem,
                    filename=rel,
                    title=title,
                    category="core",
                    priority=1000 - index,
                    enabled=True,
                    imported_at=now,
                    updated_at=now,
                ))
                changed = True
        if changed or not self.manifest_path.exists():
            self._save_manifest_entries(entries)

    def list_sources(self) -> list[dict[str, Any]]:
        return [entry.to_dict() for entry in self._sorted_entries(self._load_manifest_entries())]

    def import_source(self, source_path: Path, *, title: str = "", category: str = "imported", priority: int = 0, enabled: bool = True) -> dict[str, Any]:
        source = self._validate_source_file(source_path)
        category = self._validate_category(category, allow_core=False)
        entries = self._load_manifest_entries()
        base = slugify(source.stem) + source.suffix.lower()
        filename = self._unique_filename(category, base)
        target = self.root / category / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        now = utc_now_iso()
        entry_id = self._unique_id(slugify(source.stem), entries)
        entry = IntelligenceSource(entry_id, f"{category}/{filename}", title.strip() or source.stem.replace("_", " ").title(), category, int(priority), bool(enabled), now, now)
        entries.append(entry)
        self._save_manifest_entries(entries)
        return entry.to_dict()

    def replace_source(self, source_id: str, source_path: Path, *, title: str | None = None) -> dict[str, Any]:
        source = self._validate_source_file(source_path)
        entries = self._load_manifest_entries()
        idx, entry = self._find_entry(entries, source_id)
        target = self._entry_path(entry)
        if source.suffix.lower() != target.suffix.lower():
            raise ValueError("Replacement file must use the same extension as the existing source file.")
        shutil.copy2(source, target)
        updated = IntelligenceSource(entry.id, entry.filename, title.strip() if isinstance(title, str) and title.strip() else entry.title, entry.category, entry.priority, entry.enabled, entry.imported_at, utc_now_iso())
        entries[idx] = updated
        self._save_manifest_entries(entries)
        return updated.to_dict()

    def set_enabled(self, source_id: str, enabled: bool) -> dict[str, Any]:
        entries = self._load_manifest_entries(); idx, entry = self._find_entry(entries, source_id)
        updated = IntelligenceSource(entry.id, entry.filename, entry.title, entry.category, entry.priority, bool(enabled), entry.imported_at, utc_now_iso())
        entries[idx] = updated; self._save_manifest_entries(entries); return updated.to_dict()

    def set_priority(self, source_id: str, priority: int) -> dict[str, Any]:
        entries = self._load_manifest_entries(); idx, entry = self._find_entry(entries, source_id)
        updated = IntelligenceSource(entry.id, entry.filename, entry.title, entry.category, int(priority), entry.enabled, entry.imported_at, utc_now_iso())
        entries[idx] = updated; self._save_manifest_entries(entries); return updated.to_dict()

    def read_enabled_sources(self, *, category: str | None = None) -> list[dict[str, Any]]:
        entries = [e for e in self._sorted_entries(self._load_manifest_entries()) if e.enabled]
        if category:
            entries = [e for e in entries if e.category == category]
        result = []
        for entry in entries:
            path = self._entry_path(entry)
            if path.exists():
                payload = entry.to_dict(); payload["content"] = path.read_text(encoding="utf-8")
                result.append(payload)
        return result

    def build_guidance(self, *, enabled_source_ids: list[str] | None = None, max_chars: int = 6000) -> tuple[str, list[dict[str, Any]]]:
        selected_ids = {str(v).strip() for v in (enabled_source_ids or []) if str(v).strip()}
        selected_allowed = bool(selected_ids)
        source_items = [item for item in self.read_enabled_sources() if item.get("category") == "core" or (selected_allowed and item.get("id") in selected_ids and item.get("category") in {"packs", "imported"})]
        source_items.sort(key=lambda item: (0 if item.get("category") == "core" else 1, -int(item.get("priority", 0) or 0), str(item.get("title") or item.get("id") or "").lower(), str(item.get("id") or "")))
        sections = []
        used = 0
        used_sources: list[dict[str, Any]] = []
        for item in source_items:
            text = str(item.get("content", "")).strip()
            if not text:
                continue
            block = f"## {item.get('title') or item.get('id')}\n{text}"
            remaining = max_chars - used
            if remaining <= 0:
                break
            chunk = block[:remaining]
            sections.append(chunk)
            used += len(chunk)
            used_payload = {k: item.get(k) for k in ("id", "title", "category", "filename", "priority")}
            used_payload["chars"] = len(chunk)
            used_sources.append(used_payload)
        return "\n\n".join(sections).strip(), used_sources

    def build_core_guidance(self, *, max_chars: int = 4000) -> str:
        guidance, _ = self.build_guidance(enabled_source_ids=[], max_chars=max_chars)
        return guidance

    def _load_manifest_entries(self, *, create_if_missing: bool = False) -> list[IntelligenceSource]:
        if not self.manifest_path.exists():
            if create_if_missing:
                self.manifest_path.parent.mkdir(parents=True, exist_ok=True); self.manifest_path.write_text("[]\n", encoding="utf-8")
            return []
        data = json.loads(self.manifest_path.read_text(encoding="utf-8") or "[]")
        return [IntelligenceSource.from_dict(item) for item in data if isinstance(item, dict)]

    def _save_manifest_entries(self, entries: list[IntelligenceSource]) -> None:
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(json.dumps([e.to_dict() for e in entries], indent=2) + "\n", encoding="utf-8")

    def _sorted_entries(self, entries: list[IntelligenceSource]) -> list[IntelligenceSource]:
        return sorted(entries, key=lambda e: (-e.priority, e.title.lower(), e.id))

    def _validate_source_file(self, source_path: Path) -> Path:
        source = source_path.expanduser().resolve()
        if not source.is_file():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        if source.suffix.lower() not in ALLOWED_SOURCE_SUFFIXES:
            raise ValueError("Source file must be .txt, .md, or .json.")
        return source

    def _validate_category(self, category: str, *, allow_core: bool) -> str:
        clean = str(category or "imported").strip().lower()
        allowed = {"packs", "imported"} | ({"core"} if allow_core else set())
        if clean not in allowed:
            raise ValueError(f"Category must be one of: {', '.join(sorted(allowed))}.")
        return clean

    def _entry_path(self, entry: IntelligenceSource) -> Path:
        path = (self.root / entry.filename).resolve()
        if self.root.resolve() not in path.parents:
            raise ValueError("Manifest entry points outside intelligence directory.")
        return path

    def _find_entry(self, entries: list[IntelligenceSource], source_id: str) -> tuple[int, IntelligenceSource]:
        for idx, entry in enumerate(entries):
            if entry.id == source_id:
                return idx, entry
        raise KeyError(f"Unknown intelligence source id: {source_id}")

    def _unique_id(self, base: str, entries: list[IntelligenceSource]) -> str:
        used = {e.id for e in entries}; candidate = base; counter = 2
        while candidate in used:
            candidate = f"{base}_{counter}"; counter += 1
        return candidate

    def _unique_filename(self, category: str, base: str) -> str:
        candidate = base; counter = 2
        while (self.root / category / candidate).exists():
            candidate = f"{Path(base).stem}_{counter}{Path(base).suffix}"; counter += 1
        return candidate


def default_intelligence_library() -> CampaignIntelligenceLibrary:
    from app.pathing import content_data_dir
    return CampaignIntelligenceLibrary(content_data_dir() / "intelligence")
