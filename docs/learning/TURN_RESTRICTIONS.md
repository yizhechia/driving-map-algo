# Why a road node is not enough routing state

Status: implemented and tested; developer understanding **unverified**.
Autonomous implementation was authorized for this build session. No answer is
required before necessary fixes or delivery.

In the synthetic graph, reaching a node with a lower total cost dominates a
more expensive arrival there: future choices depend only on the node. On a real
road network, an arrival via one street can forbid a turn that is allowed when
arriving via another. Keeping only the cheapest arrival can then discard the
cheapest valid complete route.

The new index stores `(last directed edge, restriction-prefix memory)`. The memory
is the longest suffix of the journey so far that could begin a forbidden sequence.
Every possible shorter matching suffix is contained in that suffix, so the next
edge can be checked without retaining the entire journey. Repeated visits to a
node with different relevant histories are different search states.

Consider a forbidden sequence `(a, b, c)`. Travelling `a, b` needs to retain that
history so that `c` is disallowed. Starting directly on `b` does not trigger this
rule. For an only-turn path `(a, b, c)`, deviations immediately after `a` and after
`a, b` must both be prohibited. Blocking only the wrong final turn is insufficient.

For inbound indexing, reversed traversal sees `(c, b, a)`. The forbidden sequence
must also be reversed. The original edge costs do not change. This is valid for
the fixed additive model; it does not solve departure-time-dependent traffic.

Questions to work through when ready:

1. Build a four- or five-node example where the cheapest arrival at an intersection
   cannot take the desired next turn, but a more expensive arrival can.
2. Explain why remembering only the previous edge is insufficient for a rule with
   a via way containing several segments.
3. Why does an `only_*` rule need to forbid premature exits from its via path?
4. Show a three-edge prohibited path and the corresponding reversed rule.
5. Why does a no-route result in this clipped, conservative model fail to prove
   that an actual driver has no legal route?
6. Explain why the 74 m example supports a model demonstration but cannot validate
   actual commute times or a 90% arrival guarantee.

Implementation: `commute_map/osm.py`, `commute_map/turn_routing.py`.
Independent reference and fixtures: `tests/test_roads.py`.
Evidence and limits: [real-road report](../evaluation/KLCC_ROAD_CASE.md).
