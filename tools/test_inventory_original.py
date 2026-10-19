# SPDX-License-Identifier: LGPL-3.0-only
"""Focused regression coverage for the bounded, static Java source inventory.

HBM_ORIGINAL_SOURCE=/path/to/pinned/original python3 -m unittest discover \
    -s tools -p 'test_inventory_original.py' -v
"""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import inventory_original as inventory


class SyntheticCheckout:
    """Keep unresolved class expressions explicit in synthetic parser cases."""
    def __init__(self, path, java):
        self.fixture = inventory.Source(path, java.encode())

    def source(self, path):
        if path != self.fixture.path:
            raise AssertionError(path)
        return self.fixture

    def resolve_class(self, source, tokens):
        return {"raw": inventory.raw(source.text, tokens), "qualified_name": None,
                "source": None, "status": "unresolved", "candidates": []}


class ParserTests(unittest.TestCase):
    def test_multiline_comments_strings_and_nested_argument_boundaries(self):
        java = r'''
            package fixture;
            class Mappings {
                public static void writeMappings() {
                    // put(Fake.class, "line-comment");
                    /* put(Fake.class, "block-comment"); */
                    put(
                        Demo.class, /* comma , closing ) */
                        "name,with)punctuation\"",
                        combine("nested,call", new int[] {1, 2})
                    );
                    String decoy = "put(Fake.class, not a call)";
                }
            }
        '''
        source = inventory.Source(inventory.TILE, java.encode())
        calls = [c for c in source.calls(source.method("writeMappings")) if c["name"] == "put"]
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(calls[0]["args"]), 3)
        self.assertEqual(calls[0]["raw_arguments"][0], "Demo.class")
        self.assertEqual(inventory.literal(calls[0]["args"][1]), 'name,with)punctuation"')
        self.assertIsNone(inventory.literal(calls[0]["args"][2]))
        self.assertLess(calls[0]["source"]["line"], calls[0]["source"]["end_line"])

    def test_tile_aliases_unresolved_values_and_helper_order(self):
        java = '''class Mappings {
            static void writeMappings() {
                put(Demo.class, "primary", "old_name");
                putNetwork();
                put(Unknown.class, PREFIX + "suffix");
            }
            static void putNetwork() {
                boolean present = Loader.isModLoaded("Optional");
                if (present) {
                    put(Conditional.class, "conditional");
                }
            }
            static void put(Class clazz, String... names) { map.put(clazz, names); }
        }'''
        entries, helpers = inventory.tile_entries(SyntheticCheckout(inventory.TILE, java))
        self.assertEqual([e["primary_name"] for e in entries], ["primary", "conditional", None])
        self.assertEqual(entries[0]["alternative_names"], ["old_name"])
        self.assertEqual(entries[2]["raw_arguments"][1], 'PREFIX + "suffix"')
        self.assertIn("declared_names[0]", entries[2]["unresolved_fields"])
        self.assertIn("java_class", entries[0]["unresolved_fields"])
        self.assertEqual(entries[1]["conditions"][0]["expression"], "present")
        self.assertEqual(entries[1]["condition_bindings"]["present"]["raw_expression"], 'Loader.isModLoaded("Optional")')
        self.assertEqual(helpers[0]["called_method"], "putNetwork")

    def test_entity_defaults_explicit_velocity_hex_and_unresolved_range(self):
        java = '''class Mappings {
            static void writeMappings() {
                addMob(Mob.class, "mob", 0x12ab34, 0xFFFFFF);
                addEntity(Bullet.class, "bullet", 250, false);
                addEntity(Thing.class, "thing", TRACKING_RANGE);
                addSpawn(Mob.class, 5, 1, 2, Type.monster, Biomes.forType("ocean,sea"));
            }
        }'''
        entries, spawns = inventory.entity_entries(SyntheticCheckout(inventory.ENTITY, java))
        mob, bullet, thing = entries
        self.assertEqual(mob["nominal_local_mod_id"], 2)
        self.assertEqual(bullet["nominal_local_mod_id"], 0)
        self.assertEqual(thing["nominal_local_mod_id"], 1)
        self.assertEqual(mob["spawn_egg"]["primary_color"], 0x12AB34)
        self.assertEqual(mob["tracking"]["range"], 80)
        self.assertEqual(mob["tracking"]["update_frequency_ticks"], 3)
        self.assertTrue(mob["tracking"]["sends_velocity_updates"])
        self.assertFalse(bullet["tracking"]["sends_velocity_updates"])
        self.assertIsNone(thing["tracking"]["range"])
        self.assertIn("tracking.range", thing["unresolved_fields"])
        self.assertEqual(spawns[0]["biome_expression"], 'Biomes.forType("ocean,sea")')
        self.assertIsNone(spawns[0]["effective_biome_entries"])

    def test_unreachable_tile_put_is_not_silently_dropped(self):
        java = '''class Mappings {
            static void writeMappings() { put(Demo.class, "primary"); }
            static void putUnused() { put(Other.class, "unused"); }
        }'''
        with self.assertRaisesRegex(inventory.InventoryError, "Unreachable"):
            inventory.tile_entries(SyntheticCheckout(inventory.TILE, java))

    def test_unsupported_else_is_not_mislabelled_unconditional(self):
        java = '''class Mappings {
            static void writeMappings() {
                if (condition) put(Demo.class, "one"); else put(Other.class, "two");
            }
        }'''
        with self.assertRaisesRegex(inventory.InventoryError, "Unsupported else"):
            inventory.tile_entries(SyntheticCheckout(inventory.TILE, java))

    def test_malformed_and_structural_unicode_inputs_fail(self):
        for java in ('class M { /* never closed', 'class M { void x() { put("oops); } }',
                     'class M { void x() { put(Demo.class, "id"); ] } }',
                     r'class M { void \u0078() {} }'):
            with self.subTest(java=java), self.assertRaises(inventory.InventoryError):
                inventory.Source("fixture.java", java.encode())

    def test_duplicate_names_are_preserved(self):
        records = [{"inventory_id": "a", "original_name": "same"},
                   {"inventory_id": "b", "original_name": "same"}]
        self.assertEqual(inventory.duplicates(records, "original_name"),
                         [{"value": "same", "declarations": ["a", "b"]}])

    def test_wrong_commit_fails_before_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "inventory.json"
            output.write_text("existing artifact\n")
            mismatch = subprocess.CompletedProcess([], 0, b"0" * 40 + b"\n", b"")
            with patch.object(inventory, "git", return_value=mismatch), contextlib.redirect_stderr(io.StringIO()):
                result = inventory.main(["--source", tmp, "--output", str(output)])
            self.assertEqual(result, 1)
            self.assertEqual(output.read_text(), "existing artifact\n")

    def test_dirty_java_fails_before_reading_sources(self):
        head = subprocess.CompletedProcess([], 0, inventory.COMMIT.encode() + b"\n", b"")
        dirty = subprocess.CompletedProcess([], 1, b"", b"")
        with patch.object(inventory, "git", side_effect=[head, dirty]), self.assertRaisesRegex(inventory.InventoryError, "sources differ"):
            inventory.Checkout(Path("/unused"))


@unittest.skipUnless(os.environ.get("HBM_ORIGINAL_SOURCE"), "Set HBM_ORIGINAL_SOURCE for the pinned external-source integration check")
class PinnedOriginalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(os.environ["HBM_ORIGINAL_SOURCE"])
        cls.data = inventory.build_inventory(cls.root)

    def test_exact_declaration_coverage_and_literal_resolution(self):
        expected = {"non_mob_declarations": 121, "mob_declarations": 29, "entity_declarations": 150,
                    "entity_distinct_names": 149, "spawn_rules": 5, "tile_declarations": 378,
                    "tile_conditional_declarations": 1, "tile_unconditional_declarations": 377,
                    "tile_name_declarations": 379, "tile_alternative_names": 1, "resolved_class_references": 533}
        self.assertEqual(self.data["summary"], expected)
        self.assertEqual(self.data["completeness"]["unresolved_declaration_count"], 0)
        self.assertEqual([e["nominal_local_mod_id"] for e in self.data["entities"]], list(range(150)))

    def test_alias_conflict_condition_tracking_and_linkage(self):
        aliases = [e for e in self.data["tiles"] if e["alternative_names"]]
        self.assertEqual(len(aliases), 1)
        self.assertEqual(aliases[0]["declared_names"], ["tileentity_cable", "tileentity_wirecoated"])
        conditional = [e for e in self.data["tiles"] if e["conditions"]]
        self.assertEqual(conditional[0]["primary_name"], "tileentity_oc_cable_paintable")
        self.assertEqual(conditional[0]["condition_bindings"]["ocPresent"]["raw_expression"], 'Loader.isModLoaded("OpenComputers")')
        conflicts = self.data["conflicts_and_aliases"]["duplicate_entity_names"]
        self.assertEqual(conflicts, [{"value": "entity_cloud_rainbow", "declarations": ["entity-declaration:034", "entity-declaration:038"]}])
        non_mobs = [e for e in self.data["entities"] if e["declaration_group"] == "non_mob"]
        self.assertEqual(sum(not e["tracking"]["sends_velocity_updates"] for e in non_mobs), 21)
        self.assertEqual({e["tracking"]["update_frequency_ticks"] for e in non_mobs}, {1})
        calls = self.data["registration_flow"]["main_registry_calls"]
        self.assertEqual([c["source"]["line"] for c in calls], [317, 324, 326, 343])
        for e in self.data["entities"] + self.data["spawn_rules"]:
            self.assertIn("MOB-001", e["matrix_ids"])
        for e in self.data["tiles"]:
            self.assertIn("BASE-004", e["matrix_ids"])

    def test_source_hashes_and_committed_artifact_match(self):
        for source in self.data["sources"]:
            self.assertEqual(hashlib.sha256(inventory.git(self.root, "show", f"{inventory.COMMIT}:{source['path']}").stdout).hexdigest(), source["sha256"])
        self.assertEqual(inventory.serialize(self.data), inventory.DEFAULT_OUTPUT.read_bytes())
        # JSON can be consumed independently without loading the extractor.
        self.assertEqual(json.loads(inventory.DEFAULT_OUTPUT.read_text())["schema_version"], 1)


if __name__ == "__main__":
    unittest.main()
