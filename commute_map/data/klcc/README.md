# KLCC frozen OpenStreetMap data

© [OpenStreetMap contributors](https://www.openstreetmap.org/copyright).
The OpenStreetMap-derived database in `roads.json.gz` is available under the
[Open Data Commons Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
This data licence does not select a software licence for the rest of the repository.

`manifest.json` records the source timestamp, bounding box, raw response SHA-256,
normalized compressed snapshot SHA-256, normalization, and road-node anchor.
`query.overpassql` contains the exact query submitted to the public Overpass API.
The normalized snapshot preserves all 31,057 returned element IDs, all road-node
coordinates and way node sequences, complete restriction tags/members, and the
way/node tags used by the importer. Other way/node tags were discarded.
The source response had 4,068,974 bytes; the frozen compressed snapshot has 444,194.

The snapshot includes full ways that intersect the query box and restrictions
referencing them. A restriction can reference ways absent from the response.
The importer clips segments to the box and explicitly handles incomplete relations
with conservative closures. Neither the extraction nor the importer establishes
that every legal real-world route is represented.

No network request occurs when running the case. To prepare a new version, obtain
a complete JSON response for `query.overpassql`, respecting the public service's
[usage guidance](https://wiki.openstreetmap.org/wiki/Overpass_API), then run:

```bash
python -m scripts.prepare_road_snapshot /path/to/response.json commute_map/data/klcc/query.overpassql
```

This replaces the checked-in snapshot and manifest, so review and re-evaluate the
change. A later query returns newer data and will not recreate this historical
snapshot. Routing results, derived GeoJSON and maps must retain attribution and
the applicable ODbL information. The bundled file is the replayable source for
the recorded results.
