#!/usr/bin/env python3
"""
BatchRun.py

Run GW170817 analysis scripts across all data source × PSD source combinations.

Data sources:
  - local:    GWOSC HDF5 files from EventData/GWOSC/GW170817/ (no internet)
  - fetch:    GWOSC via gwpy (requires internet)
  - kazewong: Pre-processed bilby fd_strain from EventData/GWOSC/GW170817/kazewong/

PSD sources:
  - self:     Estimated from data via gwpy Welch method (only with local/fetch data)
  - bilby:    Bilby PSD files from EventData/GWOSC/GW170817/Bilby/
  - gwtc1:    Official BayesWave PSDs from GWTC1_GW170817_PSDs.dat (LIGO-P1900011)
  - kazewong: Kazewong PSD files from EventData/GWOSC/GW170817/kazewong/

Usage:
  python GW170817/Scripts/BatchRun.py                     # list all commands
  python GW170817/Scripts/BatchRun.py --execute            # run all
  python GW170817/Scripts/BatchRun.py --execute --group heterodyned  # run only heterodyned
  python GW170817/Scripts/BatchRun.py --execute --group heterodyned --psd bilby  # filter by PSD
"""
import argparse
import subprocess
import sys

# ---------------------------------------------------------------------------
# Heterodyned runs: GWOSC data (local preferred, fetch fallback)
# ---------------------------------------------------------------------------
HETERODYNED_GWOSC = [
    # Local data + various PSDs
    "python GW170817/Scripts/GW170817_heterodyned_1.py --data-source local --psd-source self    --waveform IMRPhenomD_NRTidalv2",
    "python GW170817/Scripts/GW170817_heterodyned_1.py --data-source local --psd-source bilby   --waveform IMRPhenomD_NRTidalv2",
    "python GW170817/Scripts/GW170817_heterodyned_1.py --data-source local --psd-source gwtc1   --waveform IMRPhenomD_NRTidalv2",
    "python GW170817/Scripts/GW170817_heterodyned_1.py --data-source local --psd-source kazewong --waveform IMRPhenomD_NRTidalv2",
    # Local data + TaylorF2
    "python GW170817/Scripts/GW170817_heterodyned_1.py --data-source local --psd-source self    --waveform TaylorF2",
    "python GW170817/Scripts/GW170817_heterodyned_1.py --data-source local --psd-source bilby   --waveform TaylorF2",
    "python GW170817/Scripts/GW170817_heterodyned_1.py --data-source local --psd-source gwtc1   --waveform TaylorF2",
    "python GW170817/Scripts/GW170817_heterodyned_1.py --data-source local --psd-source kazewong --waveform TaylorF2",
    # Fetched data (fallback if local unavailable)
    #"python GW170817/Scripts/GW170817_heterodyned_1.py --data-source fetch --psd-source self    --waveform IMRPhenomD_NRTidalv2",
    #"python GW170817/Scripts/GW170817_heterodyned_1.py --data-source fetch --psd-source bilby   --waveform IMRPhenomD_NRTidalv2",
    #"python GW170817/Scripts/GW170817_heterodyned_1.py --data-source fetch --psd-source gwtc1   --waveform IMRPhenomD_NRTidalv2",
]

# ---------------------------------------------------------------------------
# Heterodyned runs: Kazewong data + various PSDs
# ---------------------------------------------------------------------------
HETERODYNED_KAZEWONG = [
    "python GW170817/Scripts/GW170817_heterodyned_kazewong.py --psd-source kazewong --waveform IMRPhenomD_NRTidalv2",
    "python GW170817/Scripts/GW170817_heterodyned_kazewong.py --psd-source bilby    --waveform IMRPhenomD_NRTidalv2",
    "python GW170817/Scripts/GW170817_heterodyned_kazewong.py --psd-source gwtc1    --waveform IMRPhenomD_NRTidalv2",
    "python GW170817/Scripts/GW170817_heterodyned_kazewong.py --psd-source kazewong --waveform TaylorF2",
    "python GW170817/Scripts/GW170817_heterodyned_kazewong.py --psd-source bilby    --waveform TaylorF2",
    "python GW170817/Scripts/GW170817_heterodyned_kazewong.py --psd-source gwtc1    --waveform TaylorF2",
]

# ---------------------------------------------------------------------------
# Unheterodyned runs (reference — much slower, uncomment as needed)
# ---------------------------------------------------------------------------
UNHETERODYNED_GWOSC = [
    #"python GW170817/Scripts/GW170817_unheterodyned_1.py --data-source local --psd-source self    --waveform IMRPhenomD_NRTidalv2",
    #"python GW170817/Scripts/GW170817_unheterodyned_1.py --data-source local --psd-source bilby   --waveform IMRPhenomD_NRTidalv2",
    #"python GW170817/Scripts/GW170817_unheterodyned_1.py --data-source local --psd-source gwtc1   --waveform IMRPhenomD_NRTidalv2",
    #"python GW170817/Scripts/GW170817_unheterodyned_1.py --data-source local --psd-source kazewong --waveform IMRPhenomD_NRTidalv2",
]

UNHETERODYNED_KAZEWONG = [
    #"python GW170817/Scripts/GW170817_unheterodyned_kazewong.py --psd-source kazewong --waveform IMRPhenomD_NRTidalv2",
    #"python GW170817/Scripts/GW170817_unheterodyned_kazewong.py --psd-source bilby    --waveform IMRPhenomD_NRTidalv2",
    #"python GW170817/Scripts/GW170817_unheterodyned_kazewong.py --psd-source gwtc1    --waveform IMRPhenomD_NRTidalv2",
]

# Group mapping for --group filter
GROUPS = {
    'heterodyned': HETERODYNED_GWOSC + HETERODYNED_KAZEWONG,
    'heterodyned-gwosc': HETERODYNED_GWOSC,
    'heterodyned-kazewong': HETERODYNED_KAZEWONG,
    'unheterodyned': UNHETERODYNED_GWOSC + UNHETERODYNED_KAZEWONG,
    'all': HETERODYNED_GWOSC + HETERODYNED_KAZEWONG + UNHETERODYNED_GWOSC + UNHETERODYNED_KAZEWONG,
}


def main():
    parser = argparse.ArgumentParser(
        description="Batch run GW170817 analysis scripts across data/PSD combinations.")
    parser.add_argument("--execute", action="store_true",
                        help="Actually execute the commands (default: dry-run list).")
    parser.add_argument("--stop-on-failure", action="store_true",
                        help="Stop if a command fails.")
    parser.add_argument("--group", choices=list(GROUPS.keys()), default='heterodyned',
                        help="Which group of runs to execute (default: heterodyned).")
    parser.add_argument("--psd", choices=['self', 'bilby', 'gwtc1', 'kazewong'],
                        help="Filter to only run commands with this PSD source.")
    parser.add_argument("--waveform", choices=['IMRPhenomD_NRTidalv2', 'TaylorF2'],
                        help="Filter to only run commands with this waveform.")
    args = parser.parse_args()

    commands = [c for c in GROUPS[args.group] if not c.strip().startswith('#')]
    # Remove commented-out commands (they start with #)
    commands = [c for c in commands if c.strip()]

    # Apply filters
    if args.psd:
        commands = [c for c in commands if f'--psd-source {args.psd}' in c]
    if args.waveform:
        commands = [c for c in commands if f'--waveform {args.waveform}' in c]

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
