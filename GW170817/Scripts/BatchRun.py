#!/usr/bin/env python3
"""
BatchRun.py

Run GW170817 analysis scripts across all data source × PSD source × phase
marginalization combinations.

Data sources:
  - local:    GWOSC HDF5 files from EventData/GWOSC/GW170817/ (no internet)
  - fetch:    GWOSC via gwpy (requires internet)
  - kazewong: Pre-processed bilby fd_strain from EventData/GWOSC/GW170817/kazewong/

PSD sources:
  - bilby:    Bilby PSD files from EventData/GWOSC/GW170817/Bilby/
  - gwtc1:    Official BayesWave PSDs from GWTC1_GW170817_PSDs.dat (LIGO-P1900011)
  - kazewong: Kazewong PSD files from EventData/GWOSC/GW170817/kazewong/

Phase marginalization:
  --phase-marginalization: Analytically marginalize phase_c (14D)
  (omitted):              Sample phase_c as uniform [0, 2pi] (15D)

Usage:
  python GW170817/Scripts/BatchRun.py                                    # list all commands
  python GW170817/Scripts/BatchRun.py --execute                           # run all heterodyned
  python GW170817/Scripts/BatchRun.py --execute --group heterodyned --phase-marg yes
  python GW170817/Scripts/BatchRun.py --execute --group all --psd bilby --waveform TaylorF2
"""
import argparse
import subprocess
import sys

# ---------------------------------------------------------------------------
# Helper: generate command variants with and without --phase-marginalization
# ---------------------------------------------------------------------------
def _with_phase_marg(base_cmds):
    """For each base command, produce only the --phase-marginalization variant."""
    out = []
    for cmd in base_cmds:
        out.append(cmd + " --phase-marginalization")
    return out

# ---------------------------------------------------------------------------
# Heterodyned runs: GWOSC data (local preferred, fetch fallback)
# ---------------------------------------------------------------------------
_HETERODYNED_GWOSC_BASE = [
    # heterodyned_2: flat-in-z prior (_flatZ suffix)
    "python GW170817/Scripts/GW170817_heterodyned_2.py --data-source local --psd-source gwtc1 --waveform IMRPhenomD_NRTidalv2 --output-dir Results/gwtc1_phasemarg",
    "python GW170817/Scripts/GW170817_heterodyned_2.py --data-source local --psd-source gwtc1 --waveform TaylorF2 --output-dir Results/gwtc1_phasemarg",
    # heterodyned_3: wider v_p = 250 km/s (_vp250 suffix)
    "python GW170817/Scripts/GW170817_heterodyned_3.py --data-source local --psd-source gwtc1 --waveform IMRPhenomD_NRTidalv2 --output-dir Results/gwtc1_phasemarg",
    "python GW170817/Scripts/GW170817_heterodyned_3.py --data-source local --psd-source gwtc1 --waveform TaylorF2 --output-dir Results/gwtc1_phasemarg",
    # heterodyned_1: baseline Beta(3,1) prior (_baseline suffix)
    "python GW170817/Scripts/GW170817_heterodyned_1.py --data-source local --psd-source gwtc1 --waveform IMRPhenomD_NRTidalv2 --output-dir Results/gwtc1_phasemarg",
    "python GW170817/Scripts/GW170817_heterodyned_1.py --data-source local --psd-source gwtc1 --waveform TaylorF2 --output-dir Results/gwtc1_phasemarg",
]
HETERODYNED_GWOSC = _with_phase_marg(_HETERODYNED_GWOSC_BASE)

# ---------------------------------------------------------------------------
# Heterodyned runs: Kazewong data + various PSDs
# ---------------------------------------------------------------------------
_HETERODYNED_KAZEWONG_BASE = [
    "python GW170817/Scripts/GW170817_heterodyned_kazewong.py --psd-source kazewong --waveform IMRPhenomD_NRTidalv2",
    #"python GW170817/Scripts/GW170817_heterodyned_kazewong.py --psd-source bilby    --waveform IMRPhenomD_NRTidalv2",
    #"python GW170817/Scripts/GW170817_heterodyned_kazewong.py --psd-source gwtc1    --waveform IMRPhenomD_NRTidalv2",
    "python GW170817/Scripts/GW170817_heterodyned_kazewong.py --psd-source kazewong --waveform TaylorF2",
    #"python GW170817/Scripts/GW170817_heterodyned_kazewong.py --psd-source bilby    --waveform TaylorF2",
    #"python GW170817/Scripts/GW170817_heterodyned_kazewong.py --psd-source gwtc1    --waveform TaylorF2",
]
HETERODYNED_KAZEWONG = _with_phase_marg(_HETERODYNED_KAZEWONG_BASE)

# ---------------------------------------------------------------------------
# Unheterodyned runs (reference — much slower)
# ---------------------------------------------------------------------------
_UNHETERODYNED_GWOSC_BASE = [
    "python GW170817/Scripts/GW170817_unheterodyned_1.py --data-source local --psd-source gwtc1 --waveform IMRPhenomD_NRTidalv2 --output-dir Results/gwtc1_phasemarg",
    "python GW170817/Scripts/GW170817_unheterodyned_1.py --data-source local --psd-source gwtc1 --waveform TaylorF2 --output-dir Results/gwtc1_phasemarg",
]
UNHETERODYNED_GWOSC = _with_phase_marg(_UNHETERODYNED_GWOSC_BASE)

_UNHETERODYNED_KAZEWONG_BASE = [
    # IMRPhenomD_NRTidalv2
    "python GW170817/Scripts/GW170817_unheterodyned_kazewong.py --psd-source kazewong --waveform IMRPhenomD_NRTidalv2",
    "python GW170817/Scripts/GW170817_unheterodyned_kazewong.py --psd-source bilby    --waveform IMRPhenomD_NRTidalv2",
    "python GW170817/Scripts/GW170817_unheterodyned_kazewong.py --psd-source gwtc1    --waveform IMRPhenomD_NRTidalv2",
    # TaylorF2
    "python GW170817/Scripts/GW170817_unheterodyned_kazewong.py --psd-source kazewong --waveform TaylorF2",
    "python GW170817/Scripts/GW170817_unheterodyned_kazewong.py --psd-source bilby    --waveform TaylorF2",
    "python GW170817/Scripts/GW170817_unheterodyned_kazewong.py --psd-source gwtc1    --waveform TaylorF2",
]
UNHETERODYNED_KAZEWONG = _with_phase_marg(_UNHETERODYNED_KAZEWONG_BASE)

# ---------------------------------------------------------------------------
# Bilby runs
# ---------------------------------------------------------------------------
_BILBY_BASE = [
    "python GW170817/Scripts/GW170817_bilby.py --mode full --waveform IMRPhenomD_NRTidalv2",
    "python GW170817/Scripts/GW170817_bilby.py --mode heterodyned --waveform IMRPhenomD_NRTidalv2",
    "python GW170817/Scripts/GW170817_bilby.py --mode full --waveform TaylorF2",
    "python GW170817/Scripts/GW170817_bilby.py --mode heterodyned --waveform TaylorF2",
]
BILBY = _with_phase_marg(_BILBY_BASE)

# Group mapping for --group filter
GROUPS = {
    'heterodyned': HETERODYNED_GWOSC + UNHETERODYNED_GWOSC,
    'heterodyned-gwosc': HETERODYNED_GWOSC,
    'heterodyned-kazewong': HETERODYNED_KAZEWONG,
    'unheterodyned': UNHETERODYNED_GWOSC + UNHETERODYNED_KAZEWONG,
    'unheterodyned-gwosc': UNHETERODYNED_GWOSC,
    'unheterodyned-kazewong': UNHETERODYNED_KAZEWONG,
    'bilby': BILBY,
    'all': (HETERODYNED_GWOSC + HETERODYNED_KAZEWONG
            + UNHETERODYNED_GWOSC + UNHETERODYNED_KAZEWONG
            + BILBY),
}


def main():
    parser = argparse.ArgumentParser(
        description="Batch run GW170817 analysis scripts across data/PSD/phase-marg combinations.")
    parser.add_argument("--execute", action="store_true",
                        help="Actually execute the commands (default: dry-run list).")
    parser.add_argument("--stop-on-failure", action="store_true",
                        help="Stop if a command fails.")
    parser.add_argument("--group", choices=list(GROUPS.keys()), default='heterodyned',
                        help="Which group of runs to execute (default: heterodyned).")
    parser.add_argument("--psd", choices=['bilby', 'gwtc1', 'kazewong'],
                        help="Filter to only run commands with this PSD source.")
    parser.add_argument("--waveform", choices=['IMRPhenomD_NRTidalv2', 'TaylorF2'],
                        help="Filter to only run commands with this waveform.")
    parser.add_argument("--phase-marg", choices=['yes', 'no'],
                        help="Filter to only phase-marginalized ('yes') or non-marginalized ('no') runs.")
    args = parser.parse_args()

    commands = [c for c in GROUPS[args.group] if not c.strip().startswith('#')]
    commands = [c for c in commands if c.strip()]

    # Apply filters
    if args.psd:
        commands = [c for c in commands if f'--psd-source {args.psd}' in c]
    if args.waveform:
        commands = [c for c in commands if f'--waveform {args.waveform}' in c]
    if args.phase_marg == 'yes':
        commands = [c for c in commands if '--phase-marginalization' in c]
    elif args.phase_marg == 'no':
        commands = [c for c in commands if '--phase-marginalization' not in c]

    if not commands:
        print("No commands match the selected filters.", file=sys.stderr)
        sys.exit(1)

    print(f"{'EXECUTE' if args.execute else 'DRY RUN'}: {len(commands)} command(s) [{args.group}]")
    print("=" * 80)

    for i, cmd in enumerate(commands, 1):
        print(f"[{i}/{len(commands)}] {cmd}")
        if not args.execute:
            continue
        try:
            ret = subprocess.run(cmd, shell=True)
            if ret.returncode != 0:
                print(f"FAILED (exit {ret.returncode}): {cmd}", file=sys.stderr)
                if args.stop_on_failure:
                    sys.exit(ret.returncode)
        except KeyboardInterrupt:
            print("\nInterrupted by user", file=sys.stderr)
            sys.exit(1)

    if not args.execute:
        print("=" * 80)
        print("Add --execute to run these commands.")


if __name__ == "__main__":
    main()
