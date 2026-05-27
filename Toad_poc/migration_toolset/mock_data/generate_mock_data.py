"""
generate_mock_data.py
Generates large mock CSV files for all 4 reports.
Counts: BIMIO_267=5200, BIMIO_523=7800, BIMIO_494=9100, BIMIO_384=6400
Run: python generate_mock_data.py
"""

import csv
import os
import random
from datetime import datetime, timedelta

REPORT_DATE = "27.05.2026"
BASE_DATE   = datetime(2026, 5, 27)
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))

# ── helpers ──────────────────────────────────────────────────────────────────

def rand_dt(base: datetime, day_offset_range=(-30, 0), hour_range=(0, 23)) -> datetime:
    d = base + timedelta(days=random.randint(*day_offset_range),
                         hours=random.randint(*hour_range),
                         minutes=random.randint(0, 59))
    return d

def fmt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def write_csv(folder: str, filename: str, headers: list, rows):
    path = os.path.join(SCRIPT_DIR, folder, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    print(f"  Wrote {len(rows):,} rows -> {path}")

# ─────────────────────────────────────────────────────────────────────────────
# Report 1 — Daily_BIMIO_267   (5 200 rows)
# ─────────────────────────────────────────────────────────────────────────────
def gen_267(n=5200):
    headers = ["Network","ldz","Depot","Work Order","Root Work Order",
               "Emergency Date","Gas Prevented","Time Difference",
               "Address","MTD","Less 12","Great 12","Count"]

    networks = ["EG"]
    ldz_depot = {
        "EA": ["CAMBRIDGE","IPSWICH","NORWICH","PETERBOROUGH","BEDFORD"],
        "NE": ["NEWCASTLE","SUNDERLAND","MIDDLESBROUGH","GATESHEAD","DURHAM"],
        "NW": ["MANCHESTER","WARRINGTON","LIVERPOOL","BLACKBURN","BOLTON",
               "WIGAN","STOCKPORT","SALFORD"],
        "SC": ["GLASGOW","PAISLEY","EDINBURGH","DUNDEE","ABERDEEN",
               "INVERNESS","PERTH","STIRLING"],
        "SE": ["CROYDON","HORSHAM","MAIDSTONE","GUILDFORD","BRIGHTON",
               "EASTBOURNE","TUNBRIDGE WELLS"],
        "WM": ["BIRMINGHAM","COVENTRY","WOLVERHAMPTON","WALSALL","DUDLEY"],
        "SO": ["SOUTHAMPTON","PORTSMOUTH","BOURNEMOUTH","SALISBURY","BASINGSTOKE"],
        "NT": ["NOTTINGHAM","DERBY","LEICESTER","LINCOLN","MANSFIELD"],
    }
    street_types = ["HIGH STREET","MILL ROAD","KING STREET","CHURCH LANE",
                    "BRIDGE ROAD","STATION ROAD","PARK AVENUE","VICTORIA ROAD",
                    "NEW STREET","MARKET SQUARE","BROAD STREET","CASTLE STREET"]
    postcodes_sfx = ["1AA","2LT","3JE","4EQ","5JZ","1LA","2EE","3AB","4AH","5RX",
                     "1GF","2DU","3BU","4BH","5EE"]

    rows = []
    wo_base = 1045000
    for i in range(n):
        ldz  = random.choice(list(ldz_depot.keys()))
        depot = random.choice(ldz_depot[ldz])
        wo  = f"W{wo_base + i}"
        rwo = f"W{wo_base + i - random.randint(1,5)}"
        em_dt = rand_dt(BASE_DATE, (-1, 0), (0, 23))
        gas_dt = em_dt + timedelta(hours=random.uniform(4.0, 15.0))
        diff = round((gas_dt - em_dt).total_seconds() / 3600, 2)
        street_no = random.randint(1, 200)
        street = random.choice(street_types)
        town_code = depot.replace(" ", "_")
        pcode_area = ldz[:2] if len(ldz) >= 2 else "XX"
        pcode_sfx  = random.choice(postcodes_sfx)
        address = f"{street_no} {street} {depot} {pcode_area}{random.randint(1,9)} {pcode_sfx}"
        mtd  = random.randint(0, 1)
        l12  = 1 if diff <= 12 else 0
        g12  = 1 if diff > 12  else 0
        rows.append([
            "EG", ldz, depot, wo, rwo,
            fmt(em_dt), fmt(gas_dt), diff,
            address, mtd, l12, g12, 1
        ])
    write_csv("Daily_BIMIO_267",
              f"Daily_BIMIO_267_{REPORT_DATE}.csv",
              headers, rows)

# ─────────────────────────────────────────────────────────────────────────────
# Report 2 — Daily_BIMIO_523   (7 800 rows)
# ─────────────────────────────────────────────────────────────────────────────
def gen_523(n=7800):
    headers = [
        "Work_Order","Root_Work_Order","wo_depot","asset_depot","Asset",
        "description","Comment on WO SiteReport","priority","job_type",
        "Gas in Property","Component","Corrective Action",
        "Repairs","Corrosion","Fracture","Failure","Interference","Other",
        "status","status_date","scheduled_start","actual_finish",
        "Location","principal_street","post_town","out_code","in_code",
        "Lead_Id","Lead_Name","Material","Diameter"
    ]

    depots = ["GLASGOW","PAISLEY","EDINBURGH","DUNDEE","ABERDEEN",
              "INVERNESS","STIRLING","PERTH","MOTHERWELL","AYR"]
    descriptions = [
        "Service pipe leak repair","Main repair following excavation",
        "Emergency service connection","Pressure drop investigation",
        "Meter bypass repair","Service riser inspection",
        "Routine repair WO","Corrosion repair on main",
        "Joint failure investigation","Valve replacement",
        "PE pipe section renewal","Gas smell report investigation",
    ]
    comments = [
        "Leak found at joint under pavement","Root damage identified",
        "Customer reported smell","No visible defect found on main",
        "Bypass valve faulty","Corrosion on steel riser above ground",
        "PE joint failure on low pressure","Excavation required",
        "Temporary clamp applied","Isolation required",
    ]
    priorities = [1,2,3,4]
    job_types  = ["EM","MR","ME","IR"]
    components = ["SERVICE PIPE","MAIN","METER","RISER","VALVE","JOINT"]
    actions    = ["Pipe section renewed","Section replaced with PE",
                  "Temporary repair applied","Monitor and review",
                  "Valve replaced","Riser section replaced",
                  "PE joint re-made","Isolation applied","Clamp fitted"]
    statuses   = ["COMP","CLOSE","OPEN","PEND"]
    materials  = ["PE","ST","CI","AC"]
    diameters  = [25,32,63,100,150,200,250]
    streets    = ["BUCHANAN STREET","HIGH STREET","PRINCES STREET",
                  "UNION STREET","ARGYLE STREET","CHURCH STREET",
                  "VICTORIA ROAD","KING STREET","MARKET STREET","MAIN STREET"]
    loc_prefix = ["GLW","PSL","EDI","DND","ABD","INV","STL","PRT","MTH","AYR"]

    engineers = [
        ("ENG001","John MacDonald"),("ENG002","Alistair Fraser"),
        ("ENG003","Catriona Stewart"),("ENG004","Douglas Reid"),
        ("ENG005","Fiona Cameron"),("ENG006","Kevin McAllister"),
        ("ENG007","Morag Henderson"),("ENG008","Craig Burns"),
        ("ENG009","Lorna Mitchell"),("ENG010","Brian Thomson"),
        ("ENG011","Sandra Gillies"),("ENG012","Neil Forsyth"),
        ("ENG013","Lynn Murray"),("ENG014","Ross Campbell"),
        ("ENG015","Diane Kerr"),
    ]

    rows = []
    wo_base = 2300000
    for i in range(n):
        depot = random.choice(depots)
        idx   = depots.index(depot)
        loc   = loc_prefix[idx]
        wo    = f"W{wo_base + i}"
        rwo   = f"W{wo_base + i - random.randint(1,10)}"
        asset = f"ASSET-{random.randint(1, 9999):04d}"
        desc  = random.choice(descriptions)
        cmt   = random.choice(comments)
        pri   = random.choice(priorities)
        jtype = random.choice(job_types)
        gip   = random.choice(["YES","NO","NO  [Root WO: Gas in Property = NO]",
                                "NO  [Root WO: Gas in Property = YES]"])
        comp  = random.choice(components)
        act   = random.choice(actions)
        cor,frac,fail,interf,oth = 0,0,0,0,0
        cause_idx = random.randint(0,4)
        if cause_idx==0: cor=1
        elif cause_idx==1: frac=1
        elif cause_idx==2: fail=1
        elif cause_idx==3: interf=1
        else: oth=1
        repairs = random.choice(["Y","N"])
        status  = random.choice(statuses)
        sched   = rand_dt(BASE_DATE, (-1, 0), (6, 13))
        actual  = sched + timedelta(hours=random.uniform(2, 9))
        status_d= actual
        street  = random.choice(streets)
        mat     = random.choice(materials)
        dia     = random.choice(diameters)
        eng_id, eng_name = random.choice(engineers)
        postcode_out = f"{loc[:2]}{random.randint(1,9)}"
        postcode_in  = f"{random.randint(1,9)}{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ',k=2))}"
        loc_ref = f"LOC-{loc}-{random.randint(1,999):03d}"
        rows.append([
            wo, rwo, depot, depot, asset,
            desc, cmt, pri, jtype,
            gip, comp, act,
            repairs, cor, frac, fail, interf, oth,
            status, fmt(status_d), fmt(sched), fmt(actual),
            loc_ref, street, depot, postcode_out, postcode_in,
            eng_id, eng_name, mat, dia
        ])
    write_csv("Daily_BIMIO_523",
              f"Daily_BIMIO_523_{REPORT_DATE}.csv",
              headers, rows)

# ─────────────────────────────────────────────────────────────────────────────
# Report 3 — Monthly_BIMIO_494   (9 100 rows)
# ─────────────────────────────────────────────────────────────────────────────
def gen_494(n=9100):
    headers = ["Workorder","Job Type","ID","Name","Reported Date",
               "Job Priority","REPORTEDBY","Reported By Group"]

    job_types  = ["EMERGENCY","METERING","REPAIR","INSPECTION","ROUTINE"]
    priorities = ["E1","E2","M1","M2","R1","R2"]
    groups     = ["CRM-SOUTH","CRM-NORTH","CRM-EAST","CRM-WEST",
                  "CRM-SCOTLAND","CRM-MIDLANDS","CRM-CENTRAL"]
    employees = [
        ("EMP001","James Thornton"),("EMP002","Sarah Williamson"),
        ("EMP003","Robert Higgins"),("EMP004","Claire Donaldson"),
        ("EMP005","Andrew Patterson"),("EMP006","Linda Crawford"),
        ("EMP007","Michael Lawson"),("EMP008","Gillian Mackay"),
        ("EMP009","Thomas Russell"),("EMP010","Fiona Sinclair"),
        ("EMP011","Neil Forsyth"),("EMP012","Helen Baxter"),
        ("EMP013","David Kerr"),("EMP014","Susan Reid"),
        ("EMP015","Paul Hogan"),("EMP016","Karen Bell"),
        ("EMP017","Derek Thomson"),("EMP018","Jacqueline Park"),
        ("EMP019","Colin Murray"),("EMP020","Patricia Gray"),
        ("EMP021","Gordon Black"),("EMP022","Alison White"),
        ("EMP023","Stuart Forbes"),("EMP024","Lesley Duncan"),
        ("EMP025","Ian Henderson"),
    ]

    rows = []
    wo_base = 3400000
    # Spread dates across the reporting month
    month_start = datetime(2026, 5, 1)
    for i in range(n):
        wo   = f"W{wo_base + i}"
        jtype = random.choice(job_types)
        emp_id, emp_name = random.choice(employees)
        rep_date = month_start + timedelta(days=random.randint(0, 26))
        pri  = random.choice(priorities)
        grp  = random.choice(groups)
        rows.append([
            wo, jtype, emp_id, emp_name,
            rep_date.strftime("%Y-%m-%d"),
            pri, emp_id, grp
        ])
    write_csv("Monthly_BIMIO_494",
              f"Monthly_BIMIO_494_{REPORT_DATE}.csv",
              headers, rows)

# ─────────────────────────────────────────────────────────────────────────────
# Report 4 — Weekly__BIMIO_384   (6 400 rows)
# ─────────────────────────────────────────────────────────────────────────────
def gen_384(n=6400):
    headers = [
        "LDZ","Depot","Workstream","Engineer","Engineer Name",
        "Team Manager Name","Workorder No.","Job Type","Job Priority",
        "Actual Start","Actual Finish","Time On Site (HH:MM:SS)","Duration (Hours)"
    ]

    ldz_depot = {
        "SC": ["GLASGOW","PAISLEY","EDINBURGH","DUNDEE","ABERDEEN","INVERNESS","PERTH","STIRLING"],
        "NW": ["MANCHESTER","WARRINGTON","LIVERPOOL","BLACKBURN","BOLTON","WIGAN","STOCKPORT"],
        "EA": ["CAMBRIDGE","IPSWICH","NORWICH","PETERBOROUGH","BEDFORD","LUTON"],
        "SE": ["CROYDON","HORSHAM","MAIDSTONE","GUILDFORD","BRIGHTON","EASTBOURNE"],
        "WM": ["BIRMINGHAM","COVENTRY","WOLVERHAMPTON","WALSALL","DUDLEY","STOKE"],
        "SO": ["SOUTHAMPTON","PORTSMOUTH","BOURNEMOUTH","SALISBURY","BASINGSTOKE"],
        "NT": ["NOTTINGHAM","DERBY","LEICESTER","LINCOLN","MANSFIELD"],
        "NE": ["NEWCASTLE","SUNDERLAND","MIDDLESBROUGH","GATESHEAD","DURHAM"],
    }
    workstreams = ["EMERGENCY","REPAIR","METERING","INSPECTION","ROUTINE"]
    job_types   = ["EM","MR","ME","IR","RO"]
    priorities  = ["E1","E2","M1","M2","R1","R2"]

    engineers_by_ldz = {
        "SC": [("ENG001","John MacDonald","Steven Leckie"),
               ("ENG002","Alistair Fraser","Steven Leckie"),
               ("ENG003","Catriona Stewart","Graham Loan"),
               ("ENG004","Douglas Reid","Graham Loan"),
               ("ENG005","Fiona Cameron","Gordon Shaw"),
               ("ENG006","Kevin McAllister","Gordon Shaw")],
        "NW": [("ENG010","Paul Dawson","Gary Williams"),
               ("ENG011","Karen Simmons","Gary Williams"),
               ("ENG012","Brian Cook","Gary Williams"),
               ("ENG013","Helen Morris","Dave Clarke"),
               ("ENG014","Alan Sharp","Dave Clarke")],
        "EA": [("ENG020","Mark Holloway","Mark Booker"),
               ("ENG021","Rachel Davies","Mark Booker"),
               ("ENG022","Peter Wong","Mark Booker"),
               ("ENG023","Sharon King","Anne Foster")],
        "SE": [("ENG030","Stuart Porter","Ray Ingram"),
               ("ENG031","Tracey McIntyre","Ray Ingram"),
               ("ENG032","Colin James","Pat Nolan"),
               ("ENG033","Julie Price","Pat Nolan")],
        "WM": [("ENG040","Wayne Edwards","Mark Reygate"),
               ("ENG041","Una Cowling","Mark Reygate"),
               ("ENG042","Steve Frost","Mark Reygate"),
               ("ENG043","Diane Hunt","Tom Avery")],
        "SO": [("ENG050","Phil Hodgkins","Phil Russell"),
               ("ENG051","Wendy Nash","Phil Russell"),
               ("ENG052","Chris Lamb","Phil Russell")],
        "NT": [("ENG060","Barry Noon","Sue Holt"),
               ("ENG061","Cathy Dean","Sue Holt"),
               ("ENG062","Fred Archer","Sue Holt")],
        "NE": [("ENG070","Janet Robb","Bill Tyne"),
               ("ENG071","Alan Shaw","Bill Tyne"),
               ("ENG072","Liz Cooke","Bill Tyne")],
    }

    # Weekly window: Mon 25 May → Sun 31 May 2026
    week_start = datetime(2026, 5, 21)

    rows = []
    wo_base = 5600000
    for i in range(n):
        ldz   = random.choice(list(ldz_depot.keys()))
        depot = random.choice(ldz_depot[ldz])
        ws    = random.choice(workstreams)
        eng_id, eng_name, mgr = random.choice(engineers_by_ldz[ldz])
        wo    = f"W{wo_base + i}"
        jtype = random.choice(job_types)
        pri   = random.choice(priorities)

        day_offset  = random.randint(0, 6)
        start_hour  = random.randint(6, 11)
        start_min   = random.randint(0, 59)
        start_dt    = week_start + timedelta(days=day_offset,
                                             hours=start_hour, minutes=start_min)
        duration_hrs = round(random.uniform(2.0, 16.0), 1)
        finish_dt   = start_dt + timedelta(hours=duration_hrs)

        tos_total_secs = int(duration_hrs * 3600)
        tos_h = tos_total_secs // 3600
        tos_m = (tos_total_secs % 3600) // 60
        tos_s = tos_total_secs % 60
        tos   = f"{tos_h:02d}:{tos_m:02d}:{tos_s:02d}"

        rows.append([
            ldz, depot, ws, eng_id, eng_name, mgr,
            wo, jtype, pri,
            fmt(start_dt), fmt(finish_dt), tos, duration_hrs
        ])
    write_csv("Weekly__BIMIO_384",
              f"Weekly__BIMIO_384_{REPORT_DATE}.csv",
              headers, rows)

# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    random.seed(42)          # reproducible
    print("Generating mock data ...")
    gen_267(5_200)
    gen_523(7_800)
    gen_494(9_100)
    gen_384(6_400)
    print("Done.")
