# MFDataService Implementation Plan

## Executive Summary

Build a **centralized MFDataService** following the proven **EquityDataService** pattern to establish a single source of truth for all mutual fund data across AntiGravity (CMS) and ForwardExternal (ForwardNBFC, ForwardInsights) modules.

**Key Principles:**
- ISIN-keyed identifier (matching EquityDataService pattern)
- Centralized data ingestion and validation
- Stateless REST API with API-key authentication
- Consumer-agnostic design (all downstream modules consume via dedicated client SDK)
- Single-source-of-truth policy: MF data lives ONLY in MFDataService

---

## Current State Analysis

### Existing Data Sources
Your `/Users/jpsinha/Documents/MFDataService` contains **73 data files** (listed in workspace):
- **Scheme Masters**: `Scheme_master.txt`, `Scheme_details.txt`, `Scheme_objective.txt`
- **Financial Data**: `scheme_aum.txt`, `Scheme_paum.txt`, `Currentnav.txt`, `Navhist_*.txt`
- **Fund Manager Data**: `Fundmanager_mst.txt`, `DailyFundmanager.txt`
- **Classification Masters**: `Sclass_mst.txt`, `Type_mst.txt`, `Plan_mst.txt`, `Loadtype_mst.txt`
- **Risk/Performance Data**: `Avg_maturity.txt`, `BM_AbsoluteReturn.txt`, `Mf_return.txt`, `Mf_ratio.txt`
- **Product Data**: `Mf_portfolio.txt`, `Portfolio_inout.txt`, `Scheme_eq_details.txt`, `Scheme_index_part.txt`
- **AMC Masters**: `Amc_mst_new.txt`, `Amc_keypersons.txt`, `Amc_paum.txt`, `Amc_paum.txt`

### Current Consumer Patterns

**ForwardNBFC Backend** (`/ForwardNBFC/Backend/app/seeds/security_master.py`):
- Hard-coded hand-curated MF universe with ISIN identifiers
- Per-record fields: ISIN, name, NAV, LTV ratio, eligibility flags
- Seeded directly into MongoDB during app startup
- No dynamic updates or single source of truth

**ForwardInsights** (`/ForwardInsights/src/components/mf-analysis/*`):
- Embedded mock/hardcoded scheme data (SCHEME, FUND_UNIVERSE constants)
- Uses mf_nav folder with CSV downloads
- Scheme details page consumes from `/mf_nav/_all_schemes_combined.csv`

### Debt in Current State
1. **Data Inconsistency** — Different MF universes in ForwardNBFC vs ForwardInsights
2. **Duplicate Maintenance** — Scheme details maintained in multiple places
3. **Static Data** — No automatic updates for NAV, AUM, fund manager changes
4. **Demo Seeding** — Hand-curated entries in security_master.py are for demo only
5. **No Central API** — Consumers query local files/databases instead of a unified endpoint

---

## Proposed Solution Architecture

### Phase 1: Core Infrastructure (Week 1-2)

#### 1.1 MFDataService Structure
```
mf_data_service/                    ← new FastAPI microservice
├── app/
│   ├── main.py                     # FastAPI entry point
│   ├── core/
│   │   ├── config.py               # .env-driven settings
│   │   ├── database.py             # Motor MongoDB client
│   │   └── collections.py          # MF dataset registry (see below)
│   ├── api/
│   │   └── v1/
│   │       ├── schemes.py          # GET /schemes, /schemes/{isin}
│   │       ├── fund_managers.py    # GET /fund-managers, /fund-managers/{id}
│   │       ├── nav_history.py      # GET /nav-history/{isin}?from=&to=
│   │       ├── portfolio.py        # GET /portfolio/{isin}
│   │       ├── performance.py      # GET /performance/{isin}?metric=returns&period=1Y
│   │       ├── amc.py              # GET /amcs, /amcs/{amc_code}
│   │       ├── lookup.py           # GET /lookup/by-isin, /lookup/by-name, /lookup/resolve
│   │       ├── admin.py            # POST /admin/load-datadump, /admin/sync
│   │       └── router.py
│   ├── services/
│   │   ├── datadump_loader.py      # Load .txt files → MongoDB
│   │   ├── mf_client.py            # Vendor data ingestion (if applicable)
│   │   └── validation.py
│   ├── models/
│   │   ├── scheme.py
│   │   ├── fund_manager.py
│   │   ├── nav.py
│   │   └── portfolio.py
│   ├── schemas/
│   │   ├── responses.py
│   │   └── requests.py
│   └── utils/
│       ├── serialization.py
│       └── formatters.py
├── mf_data_client/                 ← new Python SDK (pip-installable)
│   ├── src/mf_data_client/
│   │   ├── client.py               # MFDataClient class
│   │   ├── models.py
│   │   ├── endpoints/
│   │   │   ├── schemes.py
│   │   │   ├── fund_managers.py
│   │   │   ├── nav_history.py
│   │   │   └── portfolio.py
│   │   └── async_client.py
│   └── tests/
├── scripts/
│   ├── load_datadump.py            # One-time bulk loader
│   └── sync_mf_data.py             # Daily incremental sync (future)
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   ├── GETTING_STARTED.md
│   └── DATA_MAPPING.md
├── tests/
├── requirements.txt
├── .env.example
└── run.sh
```

#### 1.2 MongoDB Schema

**Collections to Create:**

```javascript
// 1. scheme_master — Core scheme metadata
{
  _id: ObjectId,
  isin: "INF846K01EW2",                    // Unique identifier
  amc_code: "AXFL",                        // AMC reference
  scheme_code: "1234567",                  // Scheme internal code
  scheme_name: "Axis Small Cap Fund - Regular Growth",
  short_name: "Axis Small Cap",
  scheme_type: "Open Ended",               // "Open Ended" / "Close Ended"
  category: "Equity",                      // "Equity" / "Debt" / "Hybrid" / "Liquid" / "FoF"
  sub_category: "Small Cap",
  launch_date: ISODate("2014-05-29"),
  closure_date: null,
  status: "Active",                        // "Active" / "Closed" / "Merged"
  reinvestment_options: ["Growth", "Dividend", "Dividend Reinvestment"],
  plan_types: ["Regular", "Direct"],
  benchmark_name: "NIFTY Smallcap 50",
  benchmark_isin: "INE240A01024",
  fund_manager_ids: ["FM000001", "FM000002"],
  custodian: "Deutsche Bank",
  rta: "CAMS",                             // RTA code
  first_nav_date: ISODate("2014-05-29"),
  nav_frequency: "Daily",
  contact_details: {
    website: "https://axisassetmanagement.co.in/",
    email: "investor.relationss@axisasset.com",
    phone: "+91-22-4241-4444"
  },
  metadata: {
    data_source: "AASL",                   // Data source code
    last_updated: ISODate("2026-04-10T15:30:00Z"),
    version: 1
  }
}

// 2. scheme_nav — Historical NAV data
{
  _id: ObjectId,
  isin: "INF846K01EW2",
  scheme_code: "1234567",
  nav_date: ISODate("2026-04-10"),
  nav: 456.78,
  aum_cr: 2500.50,                        // AUM in Indian Crores
  units_outstanding: 547894000,
  metadata: {
    last_updated: ISODate("2026-04-10T15:30:00Z")
  }
}

// Index: UNIQUE (isin, nav_date)

// 3. scheme_portfolio — Holdings/portfolio composition
{
  _id: ObjectId,
  isin: "INF846K01EW2",
  report_date: ISODate("2026-03-31"),
  portfolio_items: [
    {
      equity_isin: "INE614J01011",         // Security ISIN (can cross-ref EquityDataService)
      security_name: "Amara Raja Battery",
      holding_value_cr: 125.50,
      holding_percentage: 5.25,
      shares_held: 1250000,      
      security_type: "Equity"
    },
    // ... more holdings
  ],
  cash_equivalent_cr: 50.25,
  cash_percentage: 2.10,
  total_portfolio_value_cr: 2548.75,
  metadata: {
    last_updated: ISODate("2026-04-10T15:30:00Z"),
    data_quality: "Complete"
  }
}

// 4. fund_manager — Fund manager master
{
  _id: "FM000001",
  manager_code: "FM000001",
  manager_name: "John Doe",
  amc_code: "AXFL",
  designation: "Senior Fund Manager",
  expertise: ["Equity", "Small Cap"],
  qualification: "B.Tech, MBA",
  start_date: ISODate("2012-01-15"),
  end_date: null,
  status: "Active",
  managed_schemes: ["INF846K01EW2", "INF846K01EW1"],
  contact: {
    email: "john.doe@axisasset.com"
  },
  metadata: {
    last_updated: ISODate("2026-04-10T15:30:00Z")
  }
}

// Index: UNIQUE (manager_code, amc_code)

// 5. amc_master — Asset Management Company master
{
  _id: "AXFL",
  amc_code: "AXFL",
  amc_name: "Axis Asset Management Company Limited",
  short_name: "Axis AMC",
  registration_number: "123456",
  contact: {
    address: "Bombay Dyeing Centre, Floor 1 & 2, Pandurang Budhkar Marg, ...",
    city: "Mumbai",
    state: "Maharashtra",
    pincode: "400025",
    phone: "+91-22-4241-4444",
    email: "queriesamczs@axisasset.com",
    website: "https://www.axisassetmanagement.co.in/"
  },
  fund_count: 45,
  aum_total_cr: 250000.00,
  metadata: {
    last_updated: ISODate("2026-04-10T15:30:00Z")
  }
}

// 6. scheme_performance — Returns and performance metrics
{
  _id: ObjectId,
  isin: "INF846K01EW2",
  as_of_date: ISODate("2026-04-10"),
  returns: {
    "1M": { scheme: 2.45, benchmark: 1.95, category: 2.20 },
    "3M": { scheme: 5.12, benchmark: 4.80, category: 5.05 },
    "6M": { scheme: 8.75, benchmark: 7.95, category: 8.50 },
    "1Y": { scheme: 12.30, benchmark: 11.50, category: 12.00 },
    "3Y": { scheme: 14.20, benchmark: 13.80, category: 14.00 },
    "5Y": { scheme: 16.50, benchmark: 15.90, category: 16.20 },
    "10Y": { scheme: 18.75, benchmark: 17.50, category: 18.40 },
    "SI": { scheme: 19.20, benchmark: 18.60, category: 18.90 }
  },
  expense_ratio: 0.68,
  turnover_ratio: 85.20,
  metadata: {
    last_updated: ISODate("2026-04-10T15:30:00Z")
  }
}

// 7. mf_lookup — Fast lookup index (name → ISIN)
{
  _id: ObjectId,
  isin: "INF846K01EW2",
  scheme_name: "Axis Small Cap Fund - Regular Growth",
  short_name: "Axis Small Cap",
  name_lower: "axis small cap fund - regular growth",
  keywords: ["Axis", "Small", "Cap", "Equity"],
  amc_name: "Axis Asset Management",
  metadata: {
    last_updated: ISODate("2026-04-10T15:30:00Z")
  }
}
```

#### 1.3 Data Mapping (TXT → MongoDB)

Document how each .txt file maps to MongoDB collections:

```python
# app/core/collections.py

DATASET_REGISTRY = {
    "scheme_master": {
        "collection": "scheme_master",
        "source_file": "$DATADUMP_ROOT/Scheme_master.txt",
        "key_columns": ["ISIN"],
        "transform": SchemeTransformer,
        "sample_rows": 5000,
        "description": "Core scheme metadata from AASL"
    },
    "scheme_details": {
        "collection": "scheme_master",  # Multiple files merge to one collection
        "source_file": "$DATADUMP_ROOT/Scheme_details.txt",
        "key_columns": ["ISIN"],
        "transform": SchemeDetailsTransformer,
        "merge_strategy": "upsert_by_isin",
        "description": "Additional scheme details"
    },
    "nav_history": {
        "collection": "scheme_nav",
        "source_file": "$DATADUMP_ROOT/Navhist_*.txt",  # Multiple files
        "key_columns": ["ISIN", "nav_date"],
        "transform": NavTransformer,
        "unique_index": ["ISIN", "nav_date"],
        "description": "Historical NAV data (multi-file)"
    },
    "fund_manager_master": {
        "collection": "fund_manager",
        "source_file": "$DATADUMP_ROOT/Fundmanager_mst.txt",
        "key_columns": ["manager_code"],
        "transform": FundManagerTransformer,
        "description": "Fund manager master data"
    },
    "amc_master": {
        "collection": "amc_master",
        "source_file": "$DATADUMP_ROOT/Amc_mst_new.txt",
        "key_columns": ["amc_code"],
        "transform": AMCTransformer,
        "description": "Asset Management Company master"
    },
    # ... more datasets
}
```

---

### Phase 2: API & Client SDK (Week 2-3)

#### 2.1 Core Endpoints

**REST API Design** (following EquityDataService pattern):

```
# Lookup & Discovery
GET    /api/v1/lookup/by-isin/{isin}           → Validate ISIN
GET    /api/v1/lookup/by-name/{scheme_name}   → Search by scheme name
GET    /api/v1/lookup/resolve                  → Bulk resolve (POST request)

# Schemes — CRUD
GET    /api/v1/schemes?q=axis&category=Equity&page=1   → Search paginated
GET    /api/v1/schemes/{isin}                  → Get one scheme
GET    /api/v1/schemes/{isin}/master           → Scheme metadata only
POST   /api/v1/schemes/bulk                    → Get many (POST request)

# NAV & Pricing
GET    /api/v1/nav-history/{isin}?from=2026-01-01&to=2026-04-10
GET    /api/v1/nav-history/{isin}/latest       → Current NAV
GET    /api/v1/nav-history/bulk                → Many isins at once (POST)

# Portfolio & Holdings
GET    /api/v1/portfolio/{isin}?as_of_date=2026-03-31
GET    /api/v1/portfolio/{isin}/equity-holdings  → Filter to equity holdings only
GET    /api/v1/portfolio/bulk                   → Many schemes (POST)

# Performance & Returns
GET    /api/v1/performance/{isin}?as_of_date=2026-04-10
GET    /api/v1/performance/{isin}/timeseries?metric=returns&period=1Y
GET    /api/v1/performance/compare?isins=ISIN1,ISIN2&metric=returns

# Fund Managers
GET    /api/v1/fund-managers?amc_code=AXFL&page=1
GET    /api/v1/fund-managers/{manager_id}
GET    /api/v1/fund-managers/{manager_id}/schemes  → Schemes managed

# AMC Master
GET    /api/v1/amcs                             → List all AMCs
GET    /api/v1/amcs/{amc_code}                  → One AMC details
GET    /api/v1/amcs/{amc_code}/schemes          → All schemes by AMC

# Composites (like EquityDataService snapshots)
GET    /api/v1/scheme-snapshot/{isin}          → Master + latest NAV + performance
POST   /api/v1/scheme-snapshot/bulk             → Many schemes composite

# Admin (operational)
POST   /api/v1/admin/load-datadump             → Trigger one-time load
POST   /api/v1/admin/sync                       → Trigger incremental sync
GET    /api/v1/admin/sync-log                   → View recent sync runs
POST   /api/v1/admin/validate                   → Data quality checks

# Health
GET    /api/v1/health                           → Liveness check
GET    /api/v1/health/ready                     → Readiness check
```

#### 2.2 Client SDK (mf-data-client)

```python
# mf_data_client/src/mf_data_client/__init__.py

from mf_data_client import MFDataClient

# Synchronous usage
with MFDataClient.from_env() as mf:
    # Lookup
    scheme = mf.lookup.by_isin("INF846K01EW2")
    
    # Get scheme details
    scheme_data = mf.schemes.get("INF846K01EW2")
    print(scheme_data["scheme_name"])
    print(scheme_data["aum_cr"])
    
    # Get NAV history
    navs = mf.nav_history.get(
        "INF846K01EW2",
        from_date="2026-01-01",
        to_date="2026-04-10"
    )
    print(f"Latest NAV: ₹{navs[-1]['nav']}")
    
    # Get portfolio
    portfolio = mf.portfolio.get("INF846K01EW2", as_of_date="2026-03-31")
    print(f"Top holding: {portfolio['items'][0']['security_name']}")
    
    # Get performance
    perf = mf.performance.get("INF846K01EW2")
    print(f"1Y Return: {perf['returns']['1Y']['scheme']}%")
    
    # Search
    results = mf.schemes.search("axis small cap", category="Equity")
    
    # Bulk operations
    snapshots = mf.schemes.bulk([
        "INF846K01EW2",
        "INF109K01BQ0",
        "INF209K01YN0"
    ])

# Async usage (for high-concurrency scenarios)
async with MFDataClient.async_from_env() as mf:
    nav = await mf.nav_history.get_latest("INF846K01EW2")
    schemes = await mf.schemes.search("axis")
```

#### 2.3 Environment Configuration

```bash
# .env.example for mf_data_service

# Service
APP_NAME=MFDataService
APP_ENV=development
DEBUG=False
UVICORN_LOG_LEVEL=info

# MongoDB
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=MFData
MONGODB_COLLECTION_PREFIX=mf_

# Data Loading
DATADUMP_ROOT=/Users/jpsinha/Documents/MFDataService
ENABLE_AUTO_LOAD=False

# API
API_KEYS=svc-mf-prod-XXXXXXXX,svc-cms-prod-XXXXXXXX,svc-fwnbfc-prod-XXXXXXXX,svc-fwinsights-prod-XXXXXXXX
API_VERSION=v1

# Scheduler (for future daily sync)
ENABLE_SCHEDULER=False
DAILY_SYNC_CRON_HOUR=02
DAILY_SYNC_CRON_MINUTE=00

# Vendor Integration (future)
VENDOR_USERNAME=
VENDOR_PASSWORD=
VENDOR_API_URL=
```

---

### Phase 3: Migration & Consumer Integration (Week 3-4)

#### 3.1 ForwardNBFC Backend Migration

**Current (`/ForwardNBFC/Backend/app/seeds/security_master.py`):**
```python
# DEPRECATED pattern — hand-curated MUTUAL_FUNDS list hard-coded in code
MUTUAL_FUNDS = [
    {
        "_id": _id("mf_hdfc_balanced"),
        "isin": "INF209K01YN0",
        "name": "HDFC Balanced Advantage Fund - Growth",
        # ... 15 more hard-coded fields
    },
    # ... 40 more schemes
]
```

**New (`@refactored`):**
```python
# app/seeds/security_master.py — REFACTORED

"""Seed data for security_master collection (reduced).

Per the no-local-data policy (mf_data_service/POLICY.md):
  * ISIN-keyed mutual fund data is fetched LIVE from MFDataService via the
    ``mf_data_client`` SDK (no local copy).
  * The ``security_master`` collection only stores ForwardNBFC's OWN risk-overlay
    fields (ltv_ratio, eligible_for_lamf, eligible_for_las, etc.).
  * Display fields (name, nav, aum) are fetched from MFDataService at read-time,
    NOT cached here.
"""

from mf_data_client import MFDataClient

async def seed_mf_security_overlay(db) -> None:
    """Seed ForwardNBFC's risk overlays for the approved MF universe.
    
    The approved ISIN list is fetched from MFDataService; only the risk-policy
    fields are added/updated locally.
    """
    mf_client = MFDataClient.from_env()
    
    # Get the approved list from MFDataService
    approved_schemes = mf_client.schemes.search(
        category="Equity",          # Filter to equity schemes only
        status="Active"
    )
    
    overlay_docs = []
    for scheme in approved_schemes:
        isin = scheme["isin"]
        overlay_docs.append({
            "isin": isin,
            "asset_class": "mutual_fund",
            "ltv_ratio": 0.62,                  # ForwardNBFC risk policy
            "eligible_for_lamf": True,
            "eligible_for_las": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        })
    
    if overlay_docs:
        await db["security_master"].insert_many(overlay_docs, ordered=False)
        print(f"  ✓ Seeded risk overlays for {len(overlay_docs)} MF schemes")

async def get_scheme_display_data(isin: str) -> dict | None:
    """Get display fields for a scheme.
    
    Fetches from MFDataService instead of local storage. Caches briefly
    to avoid rate-limiting on high-traffic endpoints.
    """
    mf_client = MFDataClient.from_env()
    try:
        scheme = await mf_client.schemes.get(isin)
        return {
            "isin": scheme["isin"],
            "name": scheme["scheme_name"],
            "nav": scheme.get("current_nav"),     # From latest NAV doc
            "aum": scheme.get("aum_cr"),
            "amc": scheme.get("amc_name"),
            "created_at": datetime.utcnow(),
        }
    except Exception as e:
        logger.warning(f"Failed to fetch scheme {isin} from MFDataService: {e}")
        return None
```

**Consumer Read Pattern (in endpoints):**
```python
# Example: ForwardNBFC loan origination endpoint

@router.get("/pledges/{pledge_id}")
async def get_pledge(pledge_id: str, db = Depends(get_db)):
    """Get pledge details including scheme data."""
    from mf_data_client import MFDataClient
    
    pledge_doc = await db["pledges"].find_one({"_id": ObjectId(pledge_id)})
    
    # Enrich with live scheme data from MFDataService
    mf_client = MFDataClient.from_env()
    scheme_data = await mf_client.schemes.get(pledge_doc["isin"])
    
    return {
        "pledge_id": str(pledge_doc["_id"]),
        "scheme_isin": pledge_doc["isin"],
        "scheme_name": scheme_data["scheme_name"],  # ✓ Live from MFDataService
        "nav": scheme_data["current_nav"],          # ✓ Live from MFDataService
        "aum": scheme_data["aum_cr"],               # ✓ Live from MFDataService
        # ... other pledge fields
    }
```

#### 3.2 ForwardInsights Frontend Migration

**Current (`/ForwardInsights/src/lib/mf-analysis-data.ts`):**
```typescript
// DEPRECATED pattern — hardcoded mock data
export const SCHEME = {
  exitLoad: "1% (if redeemed within 1 year)",
  minSIP: "500",
  fundAge: "12 years",
  turnoverRatio: "75%",
  totalStocks: 45,
  // ...
};

export const FUND_UNIVERSE = [
  {
    isin: "INF846K01EW2",
    name: "Axis Small Cap Fund",
    aum: 2500.50,
    // ... hardcoded for demo
  },
  // ... more hardcoded
];
```

**New Pattern (@refactored):**
```typescript
// src/lib/mf-data-service-client.ts — New client SDK wrapper

import { MFDataClient } from "mf-data-client-js";  // TypeScript version of SDK

const mfClient = MFDataClient.fromEnv({
  baseUrl: process.env.REACT_APP_MF_DATA_SERVICE_URL,
  apiKey: process.env.REACT_APP_MF_DATA_API_KEY,
});

export async function getSchemeDetails(isin: string) {
  const scheme = await mfClient.schemes.get(isin);
  return {
    exitLoad: scheme.exit_load || "N/A",
    minSIP: scheme.min_sip_amount || "500",
    fundAge: `${calculateAge(scheme.launch_date)} years`,
    turnoverRatio: scheme.turnover_ratio || "N/A",
    totalStocks: scheme.portfolio?.items?.length || 0,
  };
}

export async function getAllSchemes(filters?: {
  category?: string;
  amc_code?: string;
}) {
  const schemes = await mfClient.schemes.search({
    ...filters,
    limit: 100,
  });
  return schemes.map(s => ({
    isin: s.isin,
    name: s.scheme_name,
    aum: s.aum_cr,
    // ... map to display model
  }));
}

export async function getSchemePerformance(isin: string) {
  return await mfClient.performance.get(isin);
}

export async function getSchemePortfolio(isin: string, asOfDate?: string) {
  return await mfClient.portfolio.get(isin, { as_of_date: asOfDate });
}
```

**React Component Usage:**
```typescript
// src/components/mf-analysis/SchemeAnalysisTab.tsx — REFACTORED

import { useQuery } from "@tanstack/react-query";
import { getSchemeDetails, getSchemePerformance } from "@/lib/mf-data-service-client";

export function SchemeAnalysisTab({ schemeISIN }: { schemeISIN: string }) {
  const { data: scheme, isLoading: schemeLoading } = useQuery({
    queryKey: ["scheme", schemeISIN],
    queryFn: () => getSchemeDetails(schemeISIN),
  });

  const { data: performance, isLoading: perfLoading } = useQuery({
    queryKey: ["performance", schemeISIN],
    queryFn: () => getSchemePerformance(schemeISIN),
  });

  if (schemeLoading || perfLoading) return <div>Loading...</div>;

  return (
    <div className="scheme-analysis">
      <div className="quick-facts">
        <MetricCard label="AUM" value={`₹${scheme.aum} Cr`} />
        <MetricCard label="Exit Load" value={scheme.exitLoad} />
        <MetricCard label="Min SIP" value={`₹${scheme.minSIP}`} />
        {/* ... */}
      </div>

      <PerformanceTable returns={performance.returns} />
    </div>
  );
}
```

#### 3.3 AntiGravity CMS Migration Strategy (Future)

For CMS (if currently using local MF data):
1. Identify which CMS backend features consume MF data
2. Add `mf_data_client` as a dependency
3. Refactor read sites to fetch from MFDataService on-demand
4. Remove local MF data collections from MongoDB
5. Update any seeded data functions

---

### Phase 4: Testing & Deployment (Week 4)

#### 4.1 Unit & Integration Tests

```python
# tests/test_schemes_api.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def api_key():
    return "test-key-123"

def test_lookup_by_isin(api_key):
    response = client.get(
        "/api/v1/lookup/by-isin/INF846K01EW2",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["isin"] == "INF846K01EW2"

def test_scheme_search(api_key):
    response = client.get(
        "/api/v1/schemes?q=axis&category=Equity",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    assert len(response.json()["items"]) > 0

def test_nav_history(api_key):
    response = client.get(
        "/api/v1/nav-history/INF846K01EW2?from=2026-01-01&to=2026-04-10",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    navs = response.json()["data"]
    assert len(navs) > 0
    assert all("nav_date" in n and "nav" in n for n in navs)
```

#### 4.2 SDK Tests

```typescript
// mf_data_client/tests/schemes.test.ts

import { MFDataClient } from "../src/client";

describe("MFDataClient.schemes", () => {
  let client: MFDataClient;

  beforeAll(() => {
    client = MFDataClient.fromEnv();
  });

  test("should fetch scheme by ISIN", async () => {
    const scheme = await client.schemes.get("INF846K01EW2");
    expect(scheme.isin).toBe("INF846K01EW2");
    expect(scheme.scheme_name).toBeDefined();
  });

  test("should search schemes", async () => {
    const results = await client.schemes.search("axis");
    expect(results.length).toBeGreaterThan(0);
  });
});
```

#### 4.3 Deployment Checklist

- [ ] MongoDB indexes created for all key collections
- [ ] API keys generated for all consumer services (CMS, ForwardNBFC, ForwardInsights)
- [ ] Data dump loaded successfully into MongoDB
- [ ] All endpoints tested with sample ISINs
- [ ] Client SDK published to private PyPI/npm registry
- [ ] ForwardNBFC updated and tested  
- [ ] ForwardInsights updated and tested
- [ ] CMS evaluated for updates (if using MF data)
- [ ] Documentation updated
- [ ] Monitoring/alerting set up

---

## Data Quality & Maintenance

### Data Validation Rules

```python
# app/services/validation.py

class SchemeValidator:
    @staticmethod
    def validate_isin(isin: str) -> bool:
        """ISIN format: INxxxxxxxxxxxxxxx (2 country code + 12 alphanumeric)"""
        return len(isin) == 12 and isin.startswith("IN")
    
    @staticmethod
    def validate_aum(aum_cr: float) -> bool:
        """AUM should be positive"""
        return aum_cr > 0
    
    @staticmethod
    def validate_nav(nav: float, nav_date: date) -> bool:
        """NAV should be positive and not too old"""
        return nav > 0 and (date.today() - nav_date).days <= 7

class PortfolioValidator:
    @staticmethod
    def validate_holdings(items: List[Dict]) -> bool:
        """Sum of holdings should be <= 100% (accounting for cash)"""
        total_pct = sum(h.get("holding_percentage", 0) for h in items)
        return total_pct <= 100.0
```

### Manual Data Review Process

For the initial load and monthly validations:

1. **Row count validation** — Compare source .txt record count vs MongoDB collections
2. **Referential integrity** — All FK references (amc_code, manager_code) must exist
3. **Data completeness** — Check for mandatory fields (ISIN, scheme_name, launch_date)
4. **Outlier detection** — Flag NAV or AUM values 3σ outside normal range
5. **Cross-checks** — Verify that current NAV matches latest entry in nav_history

---

## Single-Source-of-Truth Policy

### Binding Contract

**All MF-related data accessed by ForwardNBFC, ForwardInsights, or AntiGravity must originate from MFDataService.**

| Data Category | Previous Location | New Location | Policy |
|---|---|---|---|
| Scheme master | ForwardNBFC hardcoded seed | MFDataService `/schemes/{isin}` | MUST fetch live |
| NAV history | CSV file in mf_nav/ | MFDataService `/nav-history/{isin}` | MUST fetch live |
| Portfolio holdings | Demo-seeded data | MFDataService `/portfolio/{isin}` | MUST fetch live |
| Performance returns | Hardcoded constants | MFDataService `/performance/{isin}` | MUST fetch live |
| Fund managers | Embedded metadata | MFDataService `/fund-managers/{id}` | MUST fetch live |
| AMC details | Static files | MFDataService `/amcs/{amc_code}` | MUST fetch live |

**Violation Examples** (MUST NOT DO):
- ❌ Caching scheme names in local database with stale copies
- ❌ Hard-coding ISIN↔name mappings in code
- ❌ Using separate CSV file as "reference" instead of API call
- ❌ Maintaining separate seed function that duplicates MFDataService data

**Compliance Examples** (✓ MUST DO):
- ✅ Call `mf_data_client.schemes.get(isin)` to get scheme details
- ✅ Cache responses for ≤5 minutes to avoid hammering API
- ✅ On cache miss, fetch fresh from MFDataService
- ✅ On error, gracefully degrade (show cached copy or generic message)

---

## Future Roadmap (Post-MVP)

**Phase 5 — Incremental Sync (Month 2)**
- Vendor API integration to pull daily NAV/portfolio updates
- Real-time data pipeline (Kafka/event streaming)
- Change data capture (CDC) for MongoDB

**Phase 6 — Advanced Features (Month 3)**
- Scheme comparison endpoints (similarity scoring)
- Backtesting & simulation APIs
- Historical performance analysis queries

**Phase 7 — Multi-Vendor Strategy (Month 4)**
- Support for equity ETFs (cross-integration with EquityDataService)
- International fund data (future)
- Alternative data feeds (if needed)

---

## Success Metrics

After full migration:
- ✅ Single source of truth for all MF data (0 duplicates)
- ✅ <200ms API response times (p95)
- ✅ 99.5% uptime (SLA)
- ✅ All module tests passing
- ✅ Zero hardcoded/seeded MF data in consumer modules
- ✅ Fully documented API + SDK
- ✅ All consumers using `mf_data_client` SDK exclusively

---

## Questions for Clarification

Before starting implementation:

1. **Data Freshness SLA** — How frequently do you need NAV/portfolio updates? Daily? Intra-day?
2. **Vendor Integration** — Do you have a real MF data vendor API, or are the .txt files the source for now?
3. **Risk Overlay Scope** — Are there ForwardNBFC-specific fields beyond LTV ratio and eligibility flags?
4. **CMS Scope** — Does AntiGravity CMS currently consume MF data? If yes, which specific features?
5. **Authentication Model** — Should MFDataService use the same auth pattern as EquityDataService (API keys)?
6. **Geographic Scope** — MF data only for India (ISIN = INxxxxxx)? Or future expansion to international?
7. **Audit Trail** — Any compliance requirement to log who accessed which scheme data and when?

---

## Appendix: File Reference

### Key Files to Review

- [EquityDataService README](../EquityDataService/equity_data_service/README.md) — Reference architecture
- [EquityDataService API Reference](../EquityDataService/equity_data_service/docs/API_REFERENCE.md) — Endpoint patterns
- [No-Local-Data Policy](../EquityDataService/migration/NO_LOCAL_DATA_POLICY.md) — Binding contract pattern
- [ForwardNBFC security_master.py](../ForwardExternal/ForwardNBFC/Backend/app/seeds/security_master.py) — Current MF seeding
- [ForwardInsights SchemeAnalysisTab](../ForwardExternal/ForwardInsights/src/components/mf-analysis/SchemeAnalysisTab.tsx) — Current display logic

### Data Files in MFDataService

73 data files categorized:
- **Scheme Masters** (4 files): Scheme_master, details, objective, name_change
- **NAV/Pricing** (17 files): Navhist_01-15, Navhist_HL, Currentnav
- **AUM Data** (5 files): scheme_aum, Scheme_paum, Avg_scheme_aum, amc related
- **Fund Management** (2 files): Fundmanager_mst, DailyFundmanager
- **Classification** (4 files): Type_mst, Sclass_mst, Plan_mst, Loadtype_mst
- **Financial Analysis** (15+ files): Return data, ratios, risk metrics, benchmark data
- **Holdings** (5+ files): Portfolio_inout, Scheme_eq_details, Index_part, etc.
- **Company Data** (5+ files): Company masters, indices, industries
- **Miscellaneous** (10+ files): SIP/STP/SWP, bulk deals, RGESS, ratios, etc.

