#!/usr/bin/env python3
"""
MACA v2 Seasonal Batch Downloader  •  Refactored
================================================
* Season‑preserving exports of MACAv2 climate layers
* CLI with dry‑run & status modes
* Progress tracking to resume interrupted jobs
* Cleaner Earth Engine initialization & task handling

Usage  ────────────────────────────────────────────
    python maca_seasonal_batch.py \
        --variables tasmax,tasmin,pr \
        --models GFDL-ESM2M,MIROC5 \
        --scenarios historical,rcp45 \
        --output-dir ~/MACA_runs \
        --dry-run

Requirements
────────────
    pip install earthengine-api
    earthengine authenticate            # once per machine or via service‑account
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List

import ee  # type: ignore

# ────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ────────────────────────────────────────────────────────────────────────────
# Define as coordinates, convert to ee.Geometry after initialization
BLACK_HILLS_COORDS = [-104.705, 43.480, -103.264, 44.652]
DEFAULT_VARIABLES = ['tasmax', 'tasmin', 'pr']
ALL_VARIABLES = DEFAULT_VARIABLES + ['rhsmax', 'rhsmin', 'huss', 'was', 'rsds']
DEFAULT_MODELS = ['GFDL-ESM2M']
ALL_MODELS = [
    'GFDL-ESM2M', 'MIROC5', 'CCSM4', 'CanESM2', 'CNRM-CM5', 'GFDL-ESM2G',
    'HadGEM2-CC365', 'HadGEM2-ES365', 'inmcm4', 'IPSL-CM5A-LR', 'IPSL-CM5A-MR',
    'IPSL-CM5B-LR', 'MIROC-ESM', 'MIROC-ESM-CHEM', 'MRI-CGCM3', 'NorESM1-M',
    'bcc-csm1-1', 'bcc-csm1-1-m', 'BNU-ESM', 'CSIRO-Mk3-6-0'
]

SCENARIOS = {
    'historical': {'start': 1950, 'end': 2005},
    'rcp45': {'start': 2006, 'end': 2099},
    'rcp85': {'start': 2006, 'end': 2099},
}

SEASONS = {
    'DJF': {'months': [12, 1, 2], 'name': 'Winter'},
    'MAM': {'months': [3, 4, 5], 'name': 'Spring'},
    'JJA': {'months': [6, 7, 8], 'name': 'Summer'},
    'SON': {'months': [9, 10, 11], 'name': 'Fall'},
}

EXPORT_PARAMS = {
    'scale': 4000,  # 4 km
    'maxPixels': 1_000_000_000,
    'fileFormat': 'GeoTIFF',
    'formatOptions': {'cloudOptimized': True},
}

TASK_LIMIT = 250  # reasonable concurrent‑task ceiling
PROGRESS_FILE_NAME = 'download_progress.json'

# ────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ────────────────────────────────────────────────────────────────────────────

def init_ee(dry_run: bool, project: str | None = None) -> None:
    """Initialize Earth Engine once per run (skipped on --dry-run)."""
    if dry_run:
        print("🛈 Dry‑run: skipping Earth Engine initialization")
        return
    try:
        ee.Initialize(project=project)
        print("✅ Earth Engine initialized")
    except Exception as exc:
        print(f"⛔ Earth Engine init failed: {exc}\nRun `earthengine authenticate` or supply service‑account creds.")
        sys.exit(1)


def ensure_list(x):
    """Helper to guarantee `ee.List` on the server side."""
    return x if isinstance(x, ee.computedobject.ComputedObject) else ee.List(x)

# ────────────────────────────────────────────────────────────────────────────
# DOWNLOADER CLASS
# ────────────────────────────────────────────────────────────────────────────

class MACASeasonalDownloader:
    """Batch exporter with progress tracking & throttling."""

    def __init__(self, *, output_dir: Path, region_coords=None):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Create geometry from coordinates (default to Black Hills)
        if region_coords is None:
            region_coords = BLACK_HILLS_COORDS
        self.region = ee.Geometry.Rectangle(region_coords)
        self.collection = ee.ImageCollection('IDAHO_EPSCOR/MACAv2_METDATA')
        self.progress_path = self.output_dir / PROGRESS_FILE_NAME
        self.completed_tasks: set[str] = self._load_progress()
        self.active_tasks: List[ee.batch.Task] = []

    # ───── Progress helpers ─────
    def _load_progress(self) -> set[str]:
        if self.progress_path.exists():
            return set(json.loads(self.progress_path.read_text()))
        return set()

    def _save_progress(self) -> None:
        self.progress_path.write_text(json.dumps(sorted(self.completed_tasks), indent=2))

    # ───── Task utilities ─────
    @staticmethod
    def _task_id(var: str, model: str, scen: str, yr0: int, yr1: int, season: str) -> str:
        return f"{var}_{model}_{scen}_{yr0}_{yr1}_{season}"

    # ───── Core export routine ─────
    def _start_export(self, *, variable: str, model: str, scenario: str, year0: int, year1: int, season_key: str) -> bool:
        tid = self._task_id(variable, model, scenario, year0, year1, season_key)
        if tid in self.completed_tasks:
            return True  # already done

        months = SEASONS[season_key]['months']
        start_date = f"{year0}-01-01"
        end_date = f"{year1}-12-31"

        # Filter collection
        col = (
            self.collection
            .filterDate(start_date, end_date)
            .filterBounds(self.region)
            .filter(ee.Filter.eq('model', model))
            .filter(ee.Filter.eq('scenario', scenario))
            .select(variable)
        )

        def add_month(img):
            return img.set('month', ee.Date(img.get('system:time_start')).get('month'))

        seasonal = col.map(add_month).filter(ee.Filter.inList('month', ensure_list(months)))
        if seasonal.size().getInfo() == 0:
            print(f"⚠️  No data for {tid}")
            return False

        mean_img = seasonal.mean().set({
            'variable': variable,
            'model': model,
            'scenario': scenario,
            'season': season_key,
            'season_name': SEASONS[season_key]['name'],
            'start_year': year0,
            'end_year': year1,
            'export_date': datetime.now(timezone.utc).isoformat(),
        })

        # Create hierarchical folder structure
        folder = f"MACA_Seasonal/{scenario}/{model}/{variable}"
        task = ee.batch.Export.image.toDrive(
            image=mean_img,
            description=tid,
            folder=folder,
            fileNamePrefix=tid,
            region=self.region,
            **EXPORT_PARAMS,
        )
        task.start()
        self.active_tasks.append(task)
        self.completed_tasks.add(tid)
        print(f"🚀 Queued {tid}")
        return True

    # ───── Scenario driver ─────
    def _process_scenario(self, var: str, model: str, scen: str) -> int:
        info = SCENARIOS[scen]
        tasks_started = 0
        for y0 in range(info['start'], info['end'] + 1, 3):
            y1 = min(y0 + 2, info['end'])
            for skey in SEASONS:
                if self._start_export(variable=var, model=model, scenario=scen, year0=y0, year1=y1, season_key=skey):
                    tasks_started += 1
                    self._throttle()
        return tasks_started

    # ───── Throttling ─────
    def _throttle(self):
        while len([t for t in self.active_tasks if t.active()]) >= TASK_LIMIT:
            print(f"⏳ Reached {TASK_LIMIT} active tasks – waiting 60 s…")
            time.sleep(60)

    # ───── Public API ─────
    def batch_download(self, *, variables: List[str], models: List[str], scenarios: List[str], dry_run: bool):
        total = len(variables) * len(models) * len(scenarios)
        print(f"\nPlan → {total} combinations; output → {self.output_dir}\n")
        if dry_run:
            est_tasks = 0
            for sc in scenarios:
                yrs = SCENARIOS[sc]['end'] - SCENARIOS[sc]['start'] + 1
                periods = (yrs + 2) // 3
                est_tasks += periods * 4  # 4 seasons
            est_tasks *= len(variables) * len(models)
            print(f"Dry‑run estimate: {est_tasks} export tasks")
            return

        started = 0
        t0 = time.time()
        for v in variables:
            for m in models:
                for s in scenarios:
                    print(f"▶ {v} | {m} | {s}")
                    started += self._process_scenario(v, m, s)
                    self._save_progress()
        dt = (time.time() - t0) / 60
        print(f"\n✅ Batch queued → {started} tasks in {dt:.1f} min")
        self._save_progress()

    def status(self):
        active = [t for t in self.active_tasks if t.active()]
        print(f"Active: {len(active)}  •  Completed IDs stored: {len(self.completed_tasks)}")

# ────────────────────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description='Seasonal MACA v2 downloader')
    p.add_argument('--variables', default=','.join(DEFAULT_VARIABLES))
    p.add_argument('--models', default=','.join(DEFAULT_MODELS))
    p.add_argument('--scenarios', default=','.join(SCENARIOS.keys()))
    p.add_argument('--all-variables', action='store_true')
    p.add_argument('--all-models', action='store_true')
    p.add_argument('--output-dir', default='MACA_Seasonal_Downloads')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--check-status', action='store_true')
    return p.parse_args()


def main():
    args = parse_args()

    variables = ALL_VARIABLES if args.all_variables else args.variables.split(',')
    models = ALL_MODELS if args.all_models else args.models.split(',')
    scenarios = args.scenarios.split(',')

    # Initialize EE first (unless dry run)
    init_ee(args.dry_run)

    # Create downloader only if not in pure dry-run mode or if EE is initialized
    if args.check_status and args.dry_run:
        print("Cannot check status in dry-run mode (Earth Engine not initialized)")
        return
    
    # For dry-run batch downloads, we can proceed without creating EE objects
    if args.dry_run and not args.check_status:
        # Just show the plan without initializing EE objects
        total = len(variables) * len(models) * len(scenarios)
        print(f"\nPlan → {total} combinations; output → {args.output_dir}\n")
        est_tasks = 0
        for sc in scenarios:
            yrs = SCENARIOS[sc]['end'] - SCENARIOS[sc]['start'] + 1
            periods = (yrs + 2) // 3
            est_tasks += periods * 4  # 4 seasons
        est_tasks *= len(variables) * len(models)
        print(f"Dry‑run estimate: {est_tasks} export tasks")
        print(f"Variables: {', '.join(variables)}")
        print(f"Models: {', '.join(models)}")
        print(f"Scenarios: {', '.join(scenarios)}")
        return

    # Only create downloader if EE is initialized
    dl = MACASeasonalDownloader(output_dir=Path(args.output_dir))

    if args.check_status:
        dl.status()
    else:
        dl.batch_download(variables=variables, models=models, scenarios=scenarios, dry_run=False)


if __name__ == '__main__':
    main()
