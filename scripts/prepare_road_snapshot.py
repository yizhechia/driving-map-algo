"""Normalize a manually downloaded Overpass response; never contacts a service."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path


BOUNDS = [3.149, 101.701, 3.176, 101.734]
DESTINATION = Path(__file__).resolve().parents[1] / "commute_map/data/klcc"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_json", type=Path)
    parser.add_argument("query", type=Path)
    args = parser.parse_args()
    raw = args.raw_json.read_bytes()
    payload = json.loads(raw)
    if payload.get("remark"):
        raise ValueError("Overpass returned a remark; do not freeze an incomplete response")
    relevant = {"highway", "name", "junction", "barrier", "area"}
    prefixes = ("access", "vehicle", "motor_vehicle", "motorcar", "oneway")
    for element in payload["elements"]:
        tags = element.get("tags", {})
        if element["type"] != "relation":
            tags = {k: v for k, v in tags.items() if k in relevant or k.startswith(prefixes)}
        if tags:
            element["tags"] = tags
        else:
            element.pop("tags", None)
    payload["elements"].sort(key=lambda x: (x["type"], x["id"]))
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    compressed = gzip.compress(encoded, compresslevel=9, mtime=0)
    manifest = {
        "case": "KLCC bounded static road-network experiment",
        "source": "OpenStreetMap contributors, via Overpass API",
        "source_url": "https://www.openstreetmap.org/copyright",
        "endpoint": "https://overpass-api.de/api/interpreter",
        "osm_base_timestamp": payload["osm3s"]["timestamp_osm_base"],
        "snapshot_sha256": hashlib.sha256(compressed).hexdigest(),
        "raw_response_sha256": hashlib.sha256(raw).hexdigest(),
        "raw_response_bytes": len(raw),
        "query_bounds_south_west_north_east": BOUNDS,
        "anchor_node": 1198097247,
        "anchor_label": "Jalan Ampang road node near KLCC (unverified workplace entrance)",
        "normalization": "Preserve all element IDs, road-node coordinates, way node sequences, restriction members/tags, names and routing-relevant way/node tags. Other way/node tags omitted. Sorted compact JSON, gzip mtime=0.",
        "license": "ODbL 1.0",
        "license_url": "https://opendatacommons.org/licenses/odbl/1-0/",
        "attribution": "© OpenStreetMap contributors",
    }
    DESTINATION.mkdir(parents=True, exist_ok=True)
    (DESTINATION / "roads.json.gz").write_bytes(compressed)
    (DESTINATION / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (DESTINATION / "query.overpassql").write_text(args.query.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Saved frozen snapshot: {len(compressed):,} bytes, {len(payload['elements']):,} elements")


if __name__ == "__main__":
    main()
