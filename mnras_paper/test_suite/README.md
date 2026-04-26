# MNRAS Paper Test Suite

**Created:** 2026-04-24
**Purpose:** Comprehensive follow-up runs and analyses to address the scientific and methodological gaps identified in the first manuscript draft. Every run is named, session-planned, and matched to an analysis script so that work can be resumed deterministically across Claude sessions.

## Design principles

1. **Every run writes to a dedicated, descriptive path.** No output overwrites an existing repository CSV. See `MANIFEST.md` for the canonical list.
2. **Every run ships a sidecar `config.json`** next to its CSV, recording: waveform, n_live, num_delete, n_bins, seed, git SHA, and wall-clock timing. This is the unit of persistence.
3. **Session scripts are session-partitioned.** Each `session_plans/session_NN_*.sh` script is designed to fit inside one 12-hour A100 session with margin. The filename encodes the order.
4. **Analysis is separable from sampling.** `analysis/*.py` scripts never run the sampler; they consume CSVs and `config.json` files only. They can be run on CPU after any session.
5. **Claude-session-portable.** A future session reading only `MANIFEST.md` and `run_catalog.csv` can tell (i) what has completed, (ii) what is still pending, and (iii) what analysis to run next.

## Directory layout

```
mnras_paper/test_suite/
├── README.md                 ← this file
├── MANIFEST.md               ← canonical list of every expected output file
├── run_catalog.csv           ← machine-readable catalog of runs with status
├── CODE_CHANGES_NEEDED.md    ← exact patches required for runs that don't work with current CLI
├── session_plans/            ← bash scripts, one per GPU session
├── scripts/                  ← new Python helpers (CPU, for prior diagnostics)
├── analysis/                 ← post-hoc analysis scripts (CPU only)
├── expected_outputs/         ← placeholder, shows expected file tree
└── logs/                     ← each session script writes its own log here
```

Run outputs go to `Results/test_suite/<run_id>/` (a separate tree from the existing `Results/gwtc1_phasemarg/` and `Results/scaling_study/`, so nothing is at risk of overwrite).

## Time budget (A100, 12-hour sessions)

| Session | Scope | Wall-clock | Requires patch | Status |
|---|---|---:|:---:|:---:|
| 01 | TaylorF2 heterodyned scaling (500 → 20k live pts) | ~2.0 h | No | pending |
| 02 | ~~Repeat-run variance~~ | — | — | **DROPPED** (2026-04-25) |
| 03 | Unheterodyned TaylorF2 scaling (500, 1500, 2500 live pts) | ~8.0 h | No | pending |
| 04 | Unheterodyned IMRPhenomD_NRTidalv2 at n_live = 2500 | ~9.5 h | No | **DONE** (imported 2026-04-22) |
| 05 | Unheterodyned IMRPhenomD_NRTidalv2 at n_live = 500 + short hetero runs | ~2.5 h | No | pending |
| 06 | GW150914 with IMRPhenomXPHM (LVK production waveform) | ~20 min | Yes | pending |
| 07 | GW170817 with IMRPhenomXAS_NRTidalv3 (×3 priors) + IMRPhenomPv2 (×2 priors) | ~1.7 h | Yes | pending |
| 08 | num_delete sweep at fixed n_live = 5000 | ~1.5 h | Yes | pending |
| 09 | Heterodyne-bin sweep at fixed n_live = 5000 | ~1.5 h | Yes | pending |
| 10 | d_L–ι bimodality: Mode-B targeted + reference-parameter swap | ~1.5 h | Yes | pending |
| 11 | n_live = 20 000 anomaly diagnostic (tighter termination) | ~1.0 h | Yes | pending |
| H  | Prior-only q-diagnostic (CPU only — laptop is fine) | ~10 min | Yes | **DONE** |

See `WAVEFORM_RECOMMENDATION.md` for the rationale behind the Session 06 and 07 waveform choices given Ripple's current inventory (no precessing tidal waveform exists, so the BNS strategy is tides+aligned-spin as primary plus precession-without-tides as systematic).

Sessions 01–05 are the ready-to-run batch. Sessions 06–11 and H each require the targeted patch described in `CODE_CHANGES_NEEDED.md`; once those patches are applied, the session scripts work unchanged.

## Priority ordering

If only a subset can be run, the recommended ordering is:

1. ✓ **Session H (prior-only q-diagnostic)** — done. Initial finding: project prior P(q>0.95)=0.099 vs LVK-equivalent 0.074 vs actual posterior 0.139. Data pulls q up; the residual gap to LVK is partly waveform.
2. ✓ **Session 04 (unheterodyned IMR_NRT 2500)** — done; imported. ln Z = 490.51 ± 0.14, 10.3 h wall-clock.
3. **Session 06 (GW150914 IMRPhenomXPHM)** — 20 min. LVK production waveform; turns the d_L offset into a clean match.
4. **Session 07 (GW170817 IMRPhenomXAS_NRTidalv3 + IMRPhenomPv2)** — 1.7 h. Best-available tidal model + precession-only systematic. Brackets the residual waveform uncertainty given Ripple's inventory.
5. **Session 01 (TF2 heterodyned scaling)** — 2 h. Completes the scaling figure for the second waveform.
6. **Session 10 (bimodality)** — 1.5 h. Local-evidence Bayes factor for Mode B.
7. Sessions 03, 05, 08, 09, 11 as time permits.

## How to run a session

```bash
cd /Users/mingyang/Desktop/Project/CambridgeProject/GPU-Accelerated-Bayesian-Inference-of-Gravitational-Waves
bash mnras_paper/test_suite/session_plans/session_01_tf2_scaling.sh 2>&1 | tee mnras_paper/test_suite/logs/session_01_tf2_scaling.$(date +%Y%m%d_%H%M%S).log
```

Each session script:
1. Records its start/end wall-clock times and the current git SHA into the session log.
2. Calls the appropriate sampling script once per run, redirecting output to a dedicated directory under `Results/test_suite/`.
3. Writes a `config.json` next to each output CSV recording the invocation.
4. Updates `run_catalog.csv` on completion (or leaves it untouched on failure — check the log).

## How Claude should pick this up in a future session

1. Read `run_catalog.csv`: any row with `status=pending` is still to run; any with `status=done` has a CSV under `Results/test_suite/<run_id>/`.
2. Read `MANIFEST.md` for the per-file provenance notes (which analysis script consumes which CSV).
3. Run the relevant `analysis/*.py` script — each is standalone and reads from `Results/test_suite/` plus the sidecar `config.json`.
4. Post analysis results to the relevant section of `mnras_paper/main.tex` or the inventory under `paper_knowledge_base/`.

## Naming conventions

Run identifiers follow:
```
<session>__<event>__<waveform>__<config>__<seed>
```
e.g. `s01__gw170817__taylorf2__nlive05000__seed0000`, `s07__gw170817__imrphenompv2__baseline__seed0000`.

Output paths follow:
```
Results/test_suite/<run_id>/
  ├── samples.csv          ← nested-sampling output
  ├── config.json          ← invocation metadata
  └── sampler.log          ← stdout+stderr from the script
```

The `samples.csv` is the analysis-consumable file. Do not rename it — the analysis scripts expect this name.
