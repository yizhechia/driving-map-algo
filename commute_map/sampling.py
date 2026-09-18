"""Budgeted sampling at cell centres, with explicit interpolated/unknown cells."""
from dataclasses import dataclass
import heapq
import math
from .model import nonnegative


@dataclass(frozen=True)
class Observation:
    status: str
    minutes: float | None = None

    def __post_init__(self):
        if self.status not in ("ok", "no_route", "unknown"):
            raise ValueError("invalid observation status")
        if self.status == "ok":
            nonnegative(self.minutes, "observation minutes")
        elif self.minutes is not None:
            raise ValueError("non-ok observations must not have a duration")


class QueryBudget:
    def __init__(self, oracle, limit):
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
            raise ValueError("budget must be a nonnegative integer")
        self.oracle, self.limit = oracle, limit
        self.cache, self.calls, self.cache_hits = {}, 0, 0

    def get(self, point):
        if point in self.cache:
            self.cache_hits += 1
            return self.cache[point]
        if self.calls >= self.limit:
            return Observation("unknown")
        self.calls += 1
        # An oracle failure is not evidence that a place is outside the region.
        try:
            value = self.oracle(*point)
            if not isinstance(value, Observation):
                raise TypeError("oracle must return Observation")
        except (ValueError, TypeError, TimeoutError, ConnectionError):
            value = Observation("unknown")
        self.cache[point] = value
        return value


def sample_grid(oracle, size, threshold, budget, method="full"):
    if isinstance(size, bool) or not isinstance(size, int) or size < 2 or size > 128:
        raise ValueError("size must be an integer between 2 and 128")
    nonnegative(threshold, "threshold")
    if method not in ("full", "uniform", "adaptive"):
        raise ValueError("invalid sampling method")
    query = QueryBudget(oracle, budget)
    values = [[None] * size for _ in range(size)]
    labels = [["unknown"] * size for _ in range(size)]
    observed = [[False] * size for _ in range(size)]

    def corners(block):
        x0, y0, x1, y1 = block
        return [(x0,y0), (x1,y0), (x0,y1), (x1,y1)]

    def probe(block):
        x0,y0,x1,y1 = block
        points = sorted(set(corners(block) + [((x0+x1)//2, (y0+y1)//2)]))
        obs = [query.get(p) for p in points]
        valid = [o.minutes for o in obs if o.status == "ok"]
        mixed = len(valid) != len(obs)
        if valid:
            mixed |= min(valid) <= threshold < max(valid)
            near = min(abs(v-threshold) for v in valid)
            spread = max(valid)-min(valid)
        else:
            near, spread = 0, 0
        refine = mixed or near <= 4 or spread >= 8
        return refine, (0 if mixed else 1, near, -spread, -(x1-x0+1)*(y1-y0+1))

    def paint(block):
        x0,y0,x1,y1 = block
        obs = [query.cache.get(p, Observation("unknown")) for p in corners(block)]
        if any(o.status != "ok" for o in obs):
            return
        a,b,c,d = [o.minutes for o in obs]
        for y in range(y0,y1+1):
            v = (y-y0)/(y1-y0) if y1 != y0 else 0
            for x in range(x0,x1+1):
                u = (x-x0)/(x1-x0) if x1 != x0 else 0
                value = (1-v)*((1-u)*a+u*b) + v*((1-u)*c+u*d)
                values[y][x] = value
                labels[y][x] = "inside" if value <= threshold else "outside"

    leaves = []
    if method == "full" or budget >= size*size:
        for y in range(size):
            for x in range(size):
                query.get((x,y))
    elif method == "uniform":
        k = min(size, math.isqrt(budget))
        if k < 2:
            if k == 1:
                query.get((size//2,size//2))
        else:
            axes = [round(i*(size-1)/(k-1)) for i in range(k)]
            for y in axes:
                for x in axes:
                    query.get((x,y))
            leaves = [(axes[i],axes[j],axes[i+1],axes[j+1])
                      for j in range(k-1) for i in range(k-1)]
    else:
        # Four major blocks per axis, refined internally around cost changes.
        cuts = sorted(set([i*size//4 for i in range(4)] + [size]))
        heap, serial = [], 0
        active = {}
        def add(block):
            nonlocal serial
            active[block] = True
            refine, priority = probe(block)
            if refine and (block[0] < block[2] or block[1] < block[3]):
                heapq.heappush(heap,(priority,serial,block))
                serial += 1
        for j in range(len(cuts)-1):
            for i in range(len(cuts)-1):
                add((cuts[i],cuts[j],cuts[i+1]-1,cuts[j+1]-1))
        while heap and query.calls < budget:
            _,_,block = heapq.heappop(heap)
            del active[block]
            x0,y0,x1,y1 = block
            mx,my = (x0+x1)//2,(y0+y1)//2
            xs = [(x0,mx)] + ([(mx+1,x1)] if mx<x1 else [])
            ys = [(y0,my)] + ([(my+1,y1)] if my<y1 else [])
            for ya,yb in ys:
                for xa,xb in xs:
                    add((xa,ya,xb,yb))
        leaves = list(active)
    for block in leaves:
        paint(block)
    # Actual samples always override interpolation, including no_route/errors.
    for (x,y), obs in query.cache.items():
        observed[y][x] = True
        values[y][x] = obs.minutes
        labels[y][x] = ("inside" if obs.minutes <= threshold else "outside") if obs.status == "ok" else obs.status
    counts = {label: sum(row.count(label) for row in labels)
              for label in ("inside", "outside", "no_route", "unknown")}
    return {"size": size, "values": values, "labels": labels, "observed": observed,
            "queries": query.calls, "cache_hits": query.cache_hits,
            "budget": budget, "method": method, "leaf_blocks": len(leaves),
            "estimated_cells": sum(not observed[y][x] and values[y][x] is not None
                                   for y in range(size) for x in range(size)),
            "counts": counts, "budget_exhausted": query.calls >= budget and len(query.cache) < size*size}
