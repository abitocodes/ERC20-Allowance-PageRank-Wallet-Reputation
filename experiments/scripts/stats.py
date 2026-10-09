"""Kendall tau_b, Spearman rho and the paired bootstrap over cohort members (evaluate_alignment.py)."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from concurrent.futures import ProcessPoolExecutor
from typing import TYPE_CHECKING, Any

import numpy as np
from scipy.stats import kendalltau, spearmanr

if TYPE_CHECKING:  # pandas stays out of the worker processes' imports
    import pandas as pd

MIN_N = 5


def _finite_pairs(x: Any, y: Any) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray(x, dtype=np.float64).ravel()
    y = np.asarray(y, dtype=np.float64).ravel()
    if x.size != y.size:
        raise ValueError("vectors differ in length")
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.all():
        return x, y
    return x[mask], y[mask]


def _degenerate(x: np.ndarray, y: np.ndarray) -> bool:
    # min == max is np.unique(.).size < 2 for finite values, without the sort.
    return x.size < MIN_N or x.min() == x.max() or y.min() == y.max()


def _tau(x: np.ndarray, y: np.ndarray) -> float | None:
    if _degenerate(x, y):
        return None
    t = kendalltau(x, y).statistic
    return float(t) if np.isfinite(t) else None


def kendall_tau_b(x: Any, y: Any) -> float | None:
    """tau_b over the pairs where both values are finite; None below five pairs or for a constant vector."""
    return _tau(*_finite_pairs(x, y))


def spearman(x: Any, y: Any) -> float | None:
    """Spearman's rho with the same guards as kendall_tau_b."""
    x, y = _finite_pairs(x, y)
    if _degenerate(x, y):
        return None
    r = spearmanr(x, y).statistic
    return float(r) if np.isfinite(r) else None


def percentile_ci(samples: Any, ci: float = 0.95) -> tuple[float | None, float | None]:
    """Percentile interval (np.percentile, linear); (None, None) without samples."""
    arr = np.asarray(samples, dtype=np.float64)
    if arr.size == 0:
        return None, None
    lo = float(np.percentile(arr, (1.0 - ci) / 2.0 * 100.0))
    hi = float(np.percentile(arr, (1.0 + ci) / 2.0 * 100.0))
    return lo, hi


def resample_matrix(n: int, n_boot: int, seed: int) -> np.ndarray:
    """B x n member indices; row b equals the b-th draw of rng.integers(0, n, n) in holdout.bootstrap_kendall."""
    return np.random.default_rng(seed).integers(0, n, size=(n_boot, n))


def _dense_ranks(x: np.ndarray, mask: np.ndarray) -> np.ndarray:
    values, inverse = np.unique(x[mask], return_inverse=True)
    # 16-bit ranks let numpy's stable argsort inside kendalltau use radix sort (about twice as fast).
    dtype = np.int16 if values.size < 2**15 else np.int32
    r = np.full(x.size, -1, dtype=dtype)
    r[mask] = inverse
    return r


def resampled_taus(x: Any, y: Any, idx: np.ndarray) -> np.ndarray:
    """tau_b of (x, y) on every row of ``idx``; skipped resamples are left out.

    Members with a non-finite value in either vector are dropped inside each
    resample; a resample is skipped when fewer than five members remain or
    either vector is constant on it.
    """
    x = np.asarray(x, dtype=np.float64).ravel()
    y = np.asarray(y, dtype=np.float64).ravel()
    mask = np.isfinite(x) & np.isfinite(y)
    # tau_b depends on the order of the values alone, so ranks give the same coefficient.
    rx, ry = _dense_ranks(x, mask), _dense_ranks(y, mask)
    complete = bool(mask.all())
    out = np.empty(idx.shape[0], dtype=np.float64)
    k = 0
    for row in idx:
        xs, ys = rx[row], ry[row]
        if not complete:
            keep = mask[row]
            xs, ys = xs[keep], ys[keep]
        t = _tau(xs, ys)
        if t is not None:
            out[k] = t
            k += 1
    return out[:k].copy()


_WORKER_IDX: np.ndarray | None = None


def _init_worker(n: int, n_boot: int, seed: int) -> None:
    # Each worker draws the index matrix again from the seed instead of receiving it.
    global _WORKER_IDX
    _WORKER_IDX = resample_matrix(n, n_boot, seed)


def _worker_taus(args: tuple[np.ndarray, np.ndarray]) -> np.ndarray:
    return resampled_taus(args[0], args[1], _WORKER_IDX)


Spec = tuple[str, Any]


class PairedBootstrap:
    """Paired bootstrap over the n cohort members (evaluate_alignment.bootstrap_alignment).

    One index matrix of B resamples, drawn once from ``seed``, serves every
    statistic, so any two of them are paired. Score and label vectors are
    registered by name; the tau_b distribution of each pair of names is
    computed once and cached for family means and contrasts.
    """

    def __init__(self, n: int, n_boot: int = 400, seed: int = 42, ci: float = 0.95):
        self.n = int(n)
        self.n_boot = int(n_boot)
        self.seed = int(seed)
        self.ci = float(ci)
        self.idx = resample_matrix(self.n, self.n_boot, self.seed)
        self.vectors: dict[str, np.ndarray] = {}
        self._samples: dict[tuple[str, str], np.ndarray] = {}
        self._points: dict[tuple[str, str], float | None] = {}

    def add(self, name: str, values: Any) -> None:
        v = np.asarray(values, dtype=np.float64).ravel()
        if v.size != self.n:
            raise ValueError(f"{name}: {v.size} values for {self.n} members")
        self.vectors[name] = v
        self._samples = {k: s for k, s in self._samples.items() if name not in k}
        self._points = {k: p for k, p in self._points.items() if name not in k}

    def add_frame(self, frame: pd.DataFrame, columns: Iterable[str] | None = None) -> None:
        for col in columns if columns is not None else frame.columns:
            self.add(col, frame[col])

    def point(self, a: str, b: str) -> float | None:
        key = (a, b)
        if key not in self._points:
            self._points[key] = kendall_tau_b(self.vectors[a], self.vectors[b])
        return self._points[key]

    def samples(self, a: str, b: str) -> np.ndarray:
        """Bootstrap distribution of tau_b(a, b), without the skipped resamples."""
        key = (a, b)
        if key not in self._samples:
            self._samples[key] = resampled_taus(self.vectors[a], self.vectors[b], self.idx)
        return self._samples[key]

    def prefetch(self, pairs: Iterable[tuple[str, str]], workers: int = 1) -> None:
        """Compute the distributions of ``pairs`` not yet cached, over ``workers`` processes.

        With workers > 1 the caller's script needs the usual ``if __name__ == "__main__"`` guard.
        """
        todo = [p for p in dict.fromkeys(tuple(p) for p in pairs) if p not in self._samples]
        if workers <= 1 or len(todo) < 2:
            for a, b in todo:
                self.samples(a, b)
            return
        with ProcessPoolExecutor(
            max_workers=min(workers, len(todo)),
            initializer=_init_worker,
            initargs=(self.n, self.n_boot, self.seed),
        ) as pool:
            jobs = [(self.vectors[a], self.vectors[b]) for a, b in todo]
            for key, s in zip(todo, pool.map(_worker_taus, jobs)):
                self._samples[key] = s

    def tau(self, a: str, b: str) -> dict[str, Any]:
        s = self.samples(a, b)
        lo, hi = percentile_ci(s, self.ci)
        return {"kendall_tau": self.point(a, b), "ci_low": lo, "ci_high": hi, "n_boot": int(s.size)}

    def family_samples(self, a: str, labels: Sequence[str]) -> tuple[float | None, np.ndarray | None]:
        """Family mean of tau_b(a, label): point estimate and per-resample means.

        As in the reference, the point estimate averages the labels that have a
        coefficient, and the per-resample mean averages the labels that gave one
        on all B resamples; (None, None) when no label did.
        """
        cols = [c for c in (self.samples(a, lab) for lab in labels) if c.size == self.n_boot]
        if not cols:
            return None, None
        pts = [p for p in (self.point(a, lab) for lab in labels) if p is not None]
        return (float(np.mean(pts)) if pts else None), np.mean(np.vstack(cols), axis=0)

    def family(self, a: str, labels: Sequence[str]) -> dict[str, Any] | None:
        point, fam = self.family_samples(a, labels)
        if fam is None:
            return None
        lo, hi = percentile_ci(fam, self.ci)
        return {"mean_tau": point, "ci_low": lo, "ci_high": hi, "n_boot": int(fam.size)}

    def _resolve(self, spec: Spec) -> tuple[float | None, np.ndarray | None]:
        a, key = spec
        if isinstance(key, str):
            s = self.samples(a, key)
            return self.point(a, key), (s if s.size == self.n_boot else None)
        return self.family_samples(a, key)

    def contrast(self, spec_a: Spec, spec_b: Spec) -> dict[str, Any] | None:
        """tau(a) - tau(b) on the same resamples.

        A spec is (score, label) or (score, [labels]) for a family mean. None
        when either side lacks a point estimate or a value on every resample,
        where the reference leaves the contrast out.
        """
        pt_a, arr_a = self._resolve(spec_a)
        pt_b, arr_b = self._resolve(spec_b)
        if arr_a is None or arr_b is None or pt_a is None or pt_b is None:
            return None
        delta = arr_a - arr_b
        lo, hi = percentile_ci(delta, self.ci)
        return {
            "a_tau": pt_a,
            "b_tau": pt_b,
            "delta_tau": float(pt_a - pt_b),
            "ci_low": lo,
            "ci_high": hi,
            "share_positive": float(np.mean(delta > 0)),
            "n_boot": int(delta.size),
        }
