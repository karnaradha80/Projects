"""
Generates 1000 gas escape records with supporting dimension data.
Writes CSV files to sample_data/ ready for SQL bulk insert.

Referential structure:
  fct_gas_escapes_v
    dwor_id_root            -> dim_work_orders (root WOs, ids 1-1000)
    dwor_id_gas_prevented   -> dim_work_orders (prev WOs, ids 1001-2000)
    dorg_id_root            -> dim_organisation (ids 1-20)
    dadr_id_root            -> dim_addresses    (ids 1-50)
    dcal_id_gas_prevented_date -> dim_calendar  (dates 2026-04-01 to 2026-05-13)
    dtim_id_gas_prevented_time -> dim_time      (24 hourly slots)
"""

import csv
import os
import random
from datetime import date, datetime, timedelta

random.seed(42)

OUT = os.path.join(os.path.dirname(__file__), "..", "sample_data")

NETWORKS   = ["Network_A", "Network_B", "Network_C"]
LDZ_MAP    = {"Network_A": ["LDZ_01", "LDZ_02"], "Network_B": ["LDZ_03", "LDZ_04"], "Network_C": ["LDZ_05"]}
DEPOTS     = [f"DEPOT_{chr(65+i)}" for i in range(20)]   # DEPOT_A … DEPOT_T
JOB_TYPES  = ["JOB_TYPE_A", "JOB_TYPE_B", "JOB_TYPE_C"]
TOWNS      = [f"Town_{chr(65+i)}" for i in range(26)]


# ── dim_organisation (20 rows) ─────────────────────────────────────────────────
orgs = []
depot_idx = 0
for i in range(20):
    net = NETWORKS[i % len(NETWORKS)]
    ldz = LDZ_MAP[net][i % len(LDZ_MAP[net])]
    depot = DEPOTS[depot_idx % len(DEPOTS)]
    depot_idx += 1
    orgs.append({"id": i + 1, "network": net, "ldz": ldz, "depot_work_group": depot})

with open(os.path.join(OUT, "dim_organisation.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["id", "network", "ldz", "depot_work_group"])
    w.writeheader(); w.writerows(orgs)
print(f"dim_organisation: {len(orgs)} rows")


# ── dim_addresses (50 rows) ────────────────────────────────────────────────────
addresses = []
for i in range(50):
    town = TOWNS[i % len(TOWNS)]
    postcode_letter = chr(65 + (i % 26))
    n = (i % 9) + 1
    addresses.append({
        "id": i + 1,
        "display_address": f"{i+1} Sample Street, {town}, {postcode_letter}{postcode_letter}{n} {n}{postcode_letter}{postcode_letter}"
    })

with open(os.path.join(OUT, "dim_addresses.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["id", "display_address"])
    w.writeheader(); w.writerows(addresses)
print(f"dim_addresses: {len(addresses)} rows")


# ── dim_calendar (43 dates: 2026-04-01 to 2026-05-13 inclusive) ───────────────
start_date = date(2026, 4, 1)
end_date   = date(2026, 5, 13)
cal_rows = []
d = start_date
while d <= end_date:
    cal_rows.append({
        "id": len(cal_rows) + 1,
        "date_disp_1": d.strftime("%d/%m/%Y"),
        "date_oracle": d.isoformat()
    })
    d += timedelta(days=1)

with open(os.path.join(OUT, "dim_calendar.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["id", "date_disp_1", "date_oracle"])
    w.writeheader(); w.writerows(cal_rows)
print(f"dim_calendar: {len(cal_rows)} rows")


# ── dim_time (24 hourly slots) ────────────────────────────────────────────────
time_rows = [{"id": h + 1, "hour_24_minute": f"{h:02d}:00:00"} for h in range(24)]

with open(os.path.join(OUT, "dim_time.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["id", "hour_24_minute"])
    w.writeheader(); w.writerows(time_rows)
print(f"dim_time: {len(time_rows)} rows")


# ── dim_work_orders (2000 rows: 1-1000 root, 1001-2000 gas-prevented) ─────────
wo_rows = []
base_dt = datetime(2026, 3, 1, 6, 0, 0)
for i in range(2000):
    offset_hours = random.randint(0, 60 * 24 * 40)   # spread over ~40 days
    dt = base_dt + timedelta(hours=offset_hours)
    wo_rows.append({
        "id": i + 1,
        "work_order_number": f"WO-{i+1:05d}",
        "reported_date_time": dt.strftime("%Y-%m-%d %H:%M:%S"),
        "job_type": random.choice(JOB_TYPES)
    })

with open(os.path.join(OUT, "dim_work_orders.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["id", "work_order_number", "reported_date_time", "job_type"])
    w.writeheader(); w.writerows(wo_rows)
print(f"dim_work_orders: {len(wo_rows)} rows")


# ── fct_gas_escapes_v (1000 rows) ─────────────────────────────────────────────
fct_rows = []
for i in range(1000):
    fct_rows.append({
        "id":                         i + 1,
        "dwor_id_root":               i + 1,           # root WO ids 1-1000
        "dwor_id_gas_prevented":      i + 1001,        # prev WO ids 1001-2000
        "dorg_id_root":               random.randint(1, len(orgs)),
        "dadr_id_root":               random.randint(1, len(addresses)),
        "dcal_id_gas_prevented_date": random.randint(1, len(cal_rows)),
        "dtim_id_gas_prevented_time": random.randint(1, len(time_rows)),
        "latest":                     "Y"
    })

with open(os.path.join(OUT, "fct_gas_escapes_v.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=[
        "id", "dwor_id_root", "dwor_id_gas_prevented",
        "dorg_id_root", "dadr_id_root",
        "dcal_id_gas_prevented_date", "dtim_id_gas_prevented_time", "latest"
    ])
    w.writeheader(); w.writerows(fct_rows)
print(f"fct_gas_escapes_v: {len(fct_rows)} rows")

print("\nAll sample data files written to sample_data/")
