"""
Dataset registry: maps source .txt files to MongoDB collections.
Each entry defines which file(s) feed which collection and the key columns.
"""

DATASET_REGISTRY = {
    # --- Scheme Masters ---
    "scheme_master": {
        "collection": "scheme_master",
        "source_file": "Scheme_master.txt",
        "key_columns": ["schemecode"],
        "description": "Core scheme metadata (name, AMC, color, flag)",
    },
    "scheme_details": {
        "collection": "scheme_master",
        "source_file": "Scheme_details.txt",
        "key_columns": ["schemecode"],
        "merge_strategy": "upsert_by_key",
        "description": "Extended scheme details (ISIN, plan, type, fund managers, etc.)",
    },
    "scheme_isin": {
        "collection": "scheme_isin",
        "source_file": "schemeisinmaster.txt",
        "key_columns": ["ISIN"],
        "description": "ISIN-to-schemecode mapping master",
    },
    "scheme_objective": {
        "collection": "scheme_objective",
        "source_file": "Scheme_objective.txt",
        "key_columns": ["schemecode"],
        "description": "Scheme investment objectives",
    },
    "scheme_name_change": {
        "collection": "scheme_name_change",
        "source_file": "Scheme_Name_Change.txt",
        "key_columns": ["schemecode"],
        "description": "Historical scheme name changes",
    },
    "merged_schemes": {
        "collection": "merged_schemes",
        "source_file": "Mergedschemes.txt",
        "key_columns": ["schemecode"],
        "description": "Merged scheme mappings",
    },

    # --- NAV & Pricing ---
    "current_nav": {
        "collection": "current_nav",
        "source_file": "Currentnav.txt",
        "key_columns": ["schemecode"],
        "description": "Latest NAV for each scheme",
    },
    "nav_history": {
        "collection": "scheme_nav",
        "source_files": [f"Navhist_{i:02d}.txt" for i in range(1, 16)] + ["Navhist_HL.txt"],
        "key_columns": ["schemecode", "navdate"],
        "description": "Historical NAV data (multi-file)",
    },

    # --- AUM ---
    "scheme_aum": {
        "collection": "scheme_aum",
        "source_file": "scheme_aum.txt",
        "key_columns": ["schemecode", "date"],
        "description": "Scheme-level AUM data",
    },
    "scheme_paum": {
        "collection": "scheme_paum",
        "source_file": "Scheme_paum.txt",
        "key_columns": ["schemecode"],
        "description": "Scheme plan-level AUM",
    },
    "amc_aum": {
        "collection": "amc_aum",
        "source_file": "amc_aum.txt",
        "key_columns": ["amc_code"],
        "description": "AMC-level AUM",
    },
    "avg_scheme_aum": {
        "collection": "avg_scheme_aum",
        "source_file": "Avg_scheme_aum.txt",
        "key_columns": ["schemecode"],
        "description": "Average scheme AUM",
    },

    # --- Fund Management ---
    "fund_manager_master": {
        "collection": "fund_manager",
        "source_file": "Fundmanager_mst.txt",
        "key_columns": ["id"],
        "description": "Fund manager master data",
    },
    "daily_fund_manager": {
        "collection": "daily_fund_manager",
        "source_file": "DailyFundmanager.txt",
        "key_columns": ["schemecode"],
        "description": "Daily fund manager assignments",
    },

    # --- AMC ---
    "amc_master": {
        "collection": "amc_master",
        "source_file": "Amc_mst_new.txt",
        "key_columns": ["amc_code"],
        "description": "Asset Management Company master",
    },
    "amc_keypersons": {
        "collection": "amc_keypersons",
        "source_file": "Amc_keypersons.txt",
        "key_columns": ["amc_code"],
        "description": "AMC key personnel",
    },
    "amc_paum": {
        "collection": "amc_paum",
        "source_file": "Amc_paum.txt",
        "key_columns": ["amc_code"],
        "description": "AMC plan-level AUM",
    },

    # --- Classification Masters ---
    "type_master": {
        "collection": "type_master",
        "source_file": "Type_mst.txt",
        "key_columns": ["type_code"],
        "description": "Scheme type master (Open/Close ended)",
    },
    "sclass_master": {
        "collection": "sclass_master",
        "source_file": "Sclass_mst.txt",
        "key_columns": ["classcode"],
        "description": "Scheme classification master (category/sub-category)",
    },
    "plan_master": {
        "collection": "plan_master",
        "source_file": "Plan_mst.txt",
        "key_columns": ["plan"],
        "description": "Plan type master",
    },
    "option_master": {
        "collection": "option_master",
        "source_file": "Option_mst.txt",
        "key_columns": ["opt_code"],
        "description": "Option type master",
    },
    "loadtype_master": {
        "collection": "loadtype_master",
        "source_file": "Loadtype_mst.txt",
        "key_columns": ["loadtype_code"],
        "description": "Load type master",
    },
    "rt_master": {
        "collection": "rt_master",
        "source_file": "Rt_mst.txt",
        "key_columns": ["rt_code"],
        "description": "RT master",
    },
    "custodian_master": {
        "collection": "custodian_master",
        "source_file": "Cust_mst.txt",
        "key_columns": ["cust_code"],
        "description": "Custodian master",
    },

    # --- Performance & Returns ---
    "scheme_returns": {
        "collection": "scheme_performance",
        "source_file": "Mf_return.txt",
        "key_columns": ["schemecode"],
        "description": "Scheme return data (1D to inception)",
    },
    "scheme_ratios": {
        "collection": "scheme_ratio",
        "source_file": "Mf_ratio.txt",
        "key_columns": ["schemecode"],
        "description": "Risk/performance ratios (Sharpe, Beta, etc.)",
    },
    "expense_ratio": {
        "collection": "expense_ratio",
        "source_file": "Expenceratio.txt",
        "key_columns": ["schemecode", "date"],
        "description": "Expense ratio data",
    },
    "benchmark_absolute_return": {
        "collection": "benchmark_abs_return",
        "source_file": "BM_AbsoluteReturn.txt",
        "key_columns": ["schemecode"],
        "description": "Benchmark absolute returns",
    },
    "benchmark_annualised_return": {
        "collection": "benchmark_ann_return",
        "source_file": "BM_AnnualisedReturn.txt",
        "key_columns": ["schemecode"],
        "description": "Benchmark annualised returns",
    },
    "mf_abs_return": {
        "collection": "mf_abs_return",
        "source_file": "Mf_abs_return.txt",
        "key_columns": ["schemecode"],
        "description": "MF absolute returns",
    },
    "mf_ans_return": {
        "collection": "mf_ans_return",
        "source_file": "Mf_ans_return.txt",
        "key_columns": ["schemecode"],
        "description": "MF annualised returns",
    },
    "classwise_return": {
        "collection": "classwise_return",
        "source_file": "ClassWiseReturn.txt",
        "key_columns": ["classcode"],
        "description": "Class-wise return data",
    },

    # --- Portfolio & Holdings ---
    "scheme_portfolio": {
        "collection": "scheme_portfolio",
        "source_file": "Mf_portfolio.txt",
        "key_columns": ["schemecode", "invdate", "srno"],
        "description": "Scheme portfolio holdings",
    },
    "portfolio_inout": {
        "collection": "portfolio_inout",
        "source_file": "Portfolio_inout.txt",
        "key_columns": ["schemecode"],
        "description": "Portfolio additions/deletions",
    },
    "scheme_eq_details": {
        "collection": "scheme_eq_details",
        "source_file": "Scheme_eq_details.txt",
        "key_columns": ["schemecode"],
        "description": "Scheme equity allocation details",
    },
    "scheme_asset_alloc": {
        "collection": "scheme_asset_alloc",
        "source_file": "Scheme_assetalloc.txt",
        "key_columns": ["schemecode"],
        "description": "Scheme asset allocation",
    },
    "scheme_index_part": {
        "collection": "scheme_index_part",
        "source_file": "Scheme_index_part.txt",
        "key_columns": ["schemecode"],
        "description": "Scheme index participation",
    },
    "avg_maturity": {
        "collection": "avg_maturity",
        "source_file": "Avg_maturity.txt",
        "key_columns": ["schemecode"],
        "description": "Average maturity data (debt funds)",
    },

    # --- Company & Industry ---
    "company_master": {
        "collection": "company_master",
        "source_file": "Companymaster.txt",
        "key_columns": ["fincode"],
        "description": "Company master data",
    },
    "company_mcap": {
        "collection": "company_mcap",
        "source_file": "CompanyMcap.txt",
        "key_columns": ["fincode"],
        "description": "Company market cap data",
    },
    "industry_master": {
        "collection": "industry_master",
        "source_file": "Industry_mst.txt",
        "key_columns": ["industry_code"],
        "description": "Industry classification master",
    },
    "index_master": {
        "collection": "index_master",
        "source_file": "Index_mst.txt",
        "key_columns": ["index_code"],
        "description": "Index master data",
    },
    "asset_sector_master": {
        "collection": "asset_sector_master",
        "source_file": "Asect_mst.txt",
        "key_columns": ["asect_code"],
        "description": "Asset sector master",
    },

    # --- Product Features ---
    "scheme_sip": {
        "collection": "scheme_sip",
        "source_file": "Mf_sip.txt",
        "key_columns": ["schemecode"],
        "description": "SIP details",
    },
    "scheme_stp": {
        "collection": "scheme_stp",
        "source_file": "Mf_stp.txt",
        "key_columns": ["schemecode"],
        "description": "STP details",
    },
    "scheme_swp": {
        "collection": "scheme_swp",
        "source_file": "Mf_swp.txt",
        "key_columns": ["schemecode"],
        "description": "SWP details",
    },
    "scheme_load": {
        "collection": "scheme_load",
        "source_file": "Schemeload.txt",
        "key_columns": ["schemecode"],
        "description": "Scheme load structure (entry/exit)",
    },
    "scheme_rtcode": {
        "collection": "scheme_rtcode",
        "source_file": "Scheme_rtcode.txt",
        "key_columns": ["schemecode"],
        "description": "Scheme RT codes",
    },

    # --- Dividends ---
    "dividend_master": {
        "collection": "dividend_master",
        "source_file": "Div_mst.txt",
        "key_columns": ["schemecode"],
        "description": "Dividend master",
    },
    "dividend_details": {
        "collection": "dividend_details",
        "source_file": "Divdetails.txt",
        "key_columns": ["schemecode"],
        "description": "Dividend payout details",
    },

    # --- Miscellaneous ---
    "fv_change": {
        "collection": "fv_change",
        "source_file": "Fvchange.txt",
        "key_columns": ["schemecode"],
        "description": "Face value change history",
    },
    "mf_ratios_default_bm": {
        "collection": "mf_ratios_default_bm",
        "source_file": "MF_Ratios_DefaultBM.txt",
        "key_columns": ["schemecode"],
        "description": "MF ratios with default benchmark",
    },
    "mf_bulk_deals": {
        "collection": "mf_bulk_deals",
        "source_file": "MFBULKDEALS.txt",
        "key_columns": ["schemecode"],
        "description": "MF bulk deal data",
    },
    "scheme_rgess": {
        "collection": "scheme_rgess",
        "source_file": "Scheme_rgess.txt",
        "key_columns": ["schemecode"],
        "description": "RGESS eligible scheme data",
    },
    "fmp_yield_details": {
        "collection": "fmp_yield_details",
        "source_file": "fmp_yielddetails.txt",
        "key_columns": ["schemecode"],
        "description": "FMP yield details",
    },
}
