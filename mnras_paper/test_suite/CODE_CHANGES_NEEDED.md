# Code changes required to run the patched sessions

Sessions 01, 03, 04 (already done), 05, H (already done) work with the existing CLI and need no code changes. Sessions 06, 07, 08, 09, 10, 11 each require one of the patches below. Each patch is small and localised; the affected lines are given explicitly so a future Claude session can apply them mechanically.

All line numbers are relative to the file head, verified 2026-04-24. If line numbers drift, `grep -n` for the anchor strings below.

The Ripple waveform inventory is:
```
TaylorF2, IMRPhenomD, IMRPhenomD_NRTidalv2,
IMRPhenomXAS, IMRPhenomXAS_NRTidalv3,
IMRPhenomPv2, IMRPhenomXPHM (MSA)
```
There is no precessing tidal waveform in Ripple. The patches and session scripts are designed around this constraint.

---

## §1 Patch P-WAV-GW150914 — IMRPhenomXPHM for GW150914

**Purpose:** add the LVK GWTC-2.1+ production waveform (`IMRPhenomXPHM`) for the BBH validation event.

**File:** `GW150914/Scripts/GW150914_heterodyned.py`

**Anchors:**
- Import: line 60 `from jimgw.core.single_event.waveform import RippleIMRPhenomD`
- argparse: line 68 `parser.add_argument('--waveform', choices=['IMRPhenomD'], ...`
- WAVEFORM_MAP: line 378 `'IMRPhenomD': RippleIMRPhenomD`

**Diff sketch:**
```python
# line 60 — add import
from jimgw.core.single_event.waveform import RippleIMRPhenomD, RippleIMRPhenomXPHM

# line 68 — extend choices
parser.add_argument(
    '--waveform',
    choices=['IMRPhenomD', 'IMRPhenomXPHM'],
    default='IMRPhenomD',
    help='Waveform approximant',
)

# line 378 — extend map
WAVEFORM_MAP = {
    'IMRPhenomD':    RippleIMRPhenomD,
    'IMRPhenomXPHM': RippleIMRPhenomXPHM,
}
```

**Required for IMRPhenomXPHM (precessing + higher modes):**
The XPHM model needs the full 6-component spin vector $(s_{1x}, s_{1y}, s_{1z}, s_{2x}, s_{2y}, s_{2z})$ rather than the two aligned components $(s_{1z}, s_{2z})$.
- Extend the `parameter_names` tuple from `[M_c, q, s1_z, s2_z, iota, d_L, t_c, psi, ra, dec]` to `[M_c, q, s1_x, s1_y, s1_z, s2_x, s2_y, s2_z, iota, d_L, t_c, psi, ra, dec]`.
- Extend the prior transform: spin magnitudes uniform in $[0, 0.99]$ (high-spin), tilt angles isotropic ($\cos\theta$ uniform in $[-1, 1]$), azimuthal angles uniform in $[0, 2\pi]$. Use `jimgw.core.single_event.prior` helpers if available.
- Parameter-vector length is 14 instead of 10 (or 15 vs 11 without phase-marg).

**Smoke test after patch:**
```bash
${PYTHON} GW150914/Scripts/GW150914_heterodyned.py \
  --waveform IMRPhenomXPHM --n-live 500 \
  --data-source local --psd-source gwtc2p1 \
  --ref-params gwtc1 --phase-marginalization \
  --output-dir /tmp/gw150914_xphm_smoke
```
Should complete in <10 minutes and produce a CSV with 14 parameter columns.

---

## §2 Patch P-WAV-GW170817 — IMRPhenomXAS_NRTidalv3 (primary) and IMRPhenomPv2 (systematic)

**Purpose:** add the best-available tidal waveform (`IMRPhenomXAS_NRTidalv3`) and a precession-only systematic (`IMRPhenomPv2`, BBH, no tides). Ripple does not provide a precessing tidal waveform; this trade-off is unavoidable.

**File:** `GW170817/Scripts/GW170817_heterodyned_1.py` (and `_2.py`, `_3.py` for the flatZ and vp250 variants).

**Anchors:**
- Import: line 47 `from jimgw.core.single_event.waveform import RippleIMRPhenomD_NRTidalv2, RippleTaylorF2`
- argparse: line 55 `parser.add_argument('--waveform', choices=['IMRPhenomD_NRTidalv2', 'TaylorF2'], ...`
- Waveform selection: lines 380–384 (if/elif block).

**Diff sketch:**
```python
# line 47
from jimgw.core.single_event.waveform import (
    RippleTaylorF2,
    RippleIMRPhenomD_NRTidalv2,
    RippleIMRPhenomXAS_NRTidalv3,
    RippleIMRPhenomPv2,
)

# line 55
parser.add_argument(
    '--waveform',
    choices=[
        'IMRPhenomD_NRTidalv2',
        'TaylorF2',
        'IMRPhenomXAS_NRTidalv3',
        'IMRPhenomPv2',
    ],
    default='IMRPhenomD_NRTidalv2',
)

# line 380
if waveform_tag == 'TaylorF2':
    waveform = RippleTaylorF2(f_ref=20.0, use_lambda_tildes=False)
elif waveform_tag == 'IMRPhenomXAS_NRTidalv3':
    waveform = RippleIMRPhenomXAS_NRTidalv3(f_ref=20.0, use_lambda_tildes=False)
elif waveform_tag == 'IMRPhenomPv2':
    waveform = RippleIMRPhenomPv2(f_ref=20.0)   # BBH; no tidal arguments
else:
    waveform_tag = 'IMRPhenomD_NRTidalv2'
    waveform = RippleIMRPhenomD_NRTidalv2(f_ref=20.0, use_lambda_tildes=False, no_taper=False)
```

**Parameter-vector changes:**

- **`IMRPhenomXAS_NRTidalv3`** has the same parameter set as `IMRPhenomD_NRTidalv2` (aligned-spin + tides). No prior changes needed; only the waveform-evaluation call differs.
- **`IMRPhenomPv2`** is precessing BBH:
  - Add 4 in-plane spin parameters: $(s_{1x}, s_{1y}, s_{2x}, s_{2y})$.
  - Drop the tidal parameters $(\Lambda_1, \Lambda_2)$ from the active sampling (or set them to 0 inside the likelihood — the BBH waveform call ignores them).
  - Use a low-spin prior consistent with the GW170817 bright-siren analysis: spin magnitudes uniform in $[0, 0.05]$, tilt angles isotropic, azimuths uniform in $[0, 2\pi]$.
  - Final parameter-vector length: 16 (vs 14 for the aligned-spin tidal models).

**Verify availability in Ripple before applying:**
```bash
${PYTHON} -c "from jimgw.core.single_event.waveform import RippleIMRPhenomXAS_NRTidalv3, RippleIMRPhenomPv2; print('ok')"
```
If either import fails, your installed Ripple version is older than the version that exposes these models — update Ripple, or fall back to `IMRPhenomD_NRTidalv2` only.

---

## §3 Patch P-NDELETE — expose num_delete as a CLI argument

**File:** `GW170817/Scripts/GW170817_heterodyned_1.py`

**Anchors:**
- argparse block around line 75 (after `--n-live`)
- Usage: line 817 `num_delete = int(num_live * 0.5)`

**Diff:**
```python
# after line 75
parser.add_argument('--num-delete', type=int, default=None,
                    help='Points deleted per NS iteration. Default: 0.5 * n_live.')

# line 817
num_delete = args.num_delete if args.num_delete is not None else int(num_live * 0.5)
```

Apply the identical change to `_2.py` and `_3.py`.

---

## §4 Patch P-NBINS — expose n_bins as a CLI argument

**File:** `GW170817/Scripts/GW170817_heterodyned_1.py`

**Anchor:** the constant `N_BINS` is used at line 719 `hetero = setup_heterodyne(..., N_BINS)` and defined earlier in the file. `grep -n 'N_BINS\s*=\s*' GW170817/Scripts/GW170817_heterodyned_1.py` to find the definition.

**Diff:**
```python
# in argparse block
parser.add_argument('--n-bins', type=int, default=501,
                    help='Number of heterodyne bins (default: 501).')

# replace the N_BINS constant with:
N_BINS = args.n_bins
```

Apply identically to `_2.py` and `_3.py`.

---

## §5 Patch P-MODEB — custom d_L prior bounds and alternative reference parameters

**File:** `GW170817/Scripts/GW170817_heterodyned_2.py` (the flatZ script)

**Anchors:**
- `grep -n "d_L.*prior\|d_L.*uniform\|Prior.*d_L\|10.*75" GW170817/Scripts/GW170817_heterodyned_2.py` to locate the d_L prior definition.
- `grep -n "load_reference_params\|ref_params\s*=" GW170817/Scripts/GW170817_heterodyned_2.py` to locate reference-parameter loading.

**Diff sketch:**
```python
# argparse additions
parser.add_argument('--dl-min', type=float, default=10.0,
                    help='Minimum d_L for the flat-in-z prior (Mpc).')
parser.add_argument('--dl-max', type=float, default=75.0,
                    help='Maximum d_L for the flat-in-z prior (Mpc).')
parser.add_argument('--ref-dl', type=float, default=None,
                    help='Override reference waveform d_L (Mpc); use for reference-swap test.')
parser.add_argument('--ref-iota', type=float, default=None,
                    help='Override reference waveform inclination (rad).')

# at d_L prior construction:
d_L_prior = FlatInRedshift(args.dl_min, args.dl_max)  # adjust to your prior class

# after ref_params load:
if args.ref_dl is not None:
    ref_params = ref_params._replace(d_L=args.ref_dl)
if args.ref_iota is not None:
    ref_params = ref_params._replace(iota=args.ref_iota)
```

Use `_replace` for NamedTuples or direct dict update if `ref_params` is a dict.

---

## §6 Patch P-TERM — expose stopping tolerance

**File:** `GW170817/Scripts/GW170817_heterodyned_1.py`

**Anchor:** `grep -n "dlogZ\|termination\|tolerance\|fractional" GW170817/Scripts/GW170817_heterodyned_1.py`

**Diff:**
```python
parser.add_argument('--tolerance', type=float, default=1e-3,
                    help='Fractional evidence termination tolerance (default: 1e-3).')
```
Pass `args.tolerance` to the BlackJAX-NS termination condition call.

---

---

## §7 Patch P-MASSBOUNDS — expose component-mass bounds as CLI arguments

**Purpose:** match the LVK low-spin prior bounds [0.87, 1.74] M_⊙ for GW170817 (and [5, 100] M_⊙ for GW150914) without rewriting the file. The wide bounds in the current scripts are the suspected cause of the q-posterior discrepancy with LVK; see `DATA_EQUIVALENCE.md` for the analysis.

**Files:**
- `GW170817/Scripts/GW170817_heterodyned_1.py` (line 146–147 sets `M_COMP_LO = 0.5`, `M_COMP_HI = 7.7`)
- `GW150914/Scripts/GW150914_heterodyned.py` (line 162–163 sets `M_COMP_LO = 1.0`, `M_COMP_HI = 100.0`)

The script applies `M_COMP_LO/HI` as a hard cut inside `logprior_fn` (line 205) and as a rejection-sampling bound in the prior-transform (line 881). Both call sites read the module-level constants, so converting them to CLI-driven values is a single-point change.

**Diff (apply to both scripts):**
```python
# Before the M_COMP_LO/HI assignments, in the argparse block:
parser.add_argument('--m-comp-lo', type=float, default=None,
                    help='Lower bound on component masses (M_sun). Defaults to script-internal value.')
parser.add_argument('--m-comp-hi', type=float, default=None,
                    help='Upper bound on component masses (M_sun). Defaults to script-internal value.')
args = parser.parse_args()

# Then replace the literal constant lines:
M_COMP_LO = args.m_comp_lo if args.m_comp_lo is not None else 0.5   # M_sun
M_COMP_HI = args.m_comp_hi if args.m_comp_hi is not None else 7.7   # M_sun
```

(For GW150914 the defaults stay at 1.0 / 100.0; only override on the command line when running the LVK-matched comparison.)

**Apply identically to** `GW170817_heterodyned_2.py` (flatZ) and `GW170817_heterodyned_3.py` (vp250) so that future flat-in-z reruns can also be done at matched bounds if needed.

**Smoke test after patch:**
```bash
${PYTHON} GW170817/Scripts/GW170817_heterodyned_1.py \
  --waveform IMRPhenomD_NRTidalv2 --n-live 200 \
  --data-source local --psd-source gwtc1 --ref-params gwtc1 \
  --phase-marginalization \
  --m-comp-lo 0.87 --m-comp-hi 1.74 \
  --output-dir /tmp/lvk_bounds_smoke
```
Should complete in ~3 min and produce a CSV whose `q` column ranges over a narrower support than the wide-bounds default.

---

## Quick verification after applying any patch

```bash
# Smoke run at n_live=100 for 1 minute, expect a small CSV
${PYTHON} GW170817/Scripts/GW170817_heterodyned_1.py --waveform IMRPhenomXAS_NRTidalv3 \
  --n-live 100 --data-source local --psd-source gwtc1 --ref-params gwtc1 \
  --phase-marginalization --output-dir /tmp/smoke
```

If the smoke run completes and produces a CSV with the expected parameter columns, the patch is live and the corresponding session scripts will work.
