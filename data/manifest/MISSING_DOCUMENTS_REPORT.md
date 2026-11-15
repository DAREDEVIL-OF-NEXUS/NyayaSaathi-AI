# Official Legal Knowledge Base — Missing & Partial Documents Inventory

Last Updated: 2026-11-15T14:00:00Z

This inventory records the verification status of all ingested materials, identifies remaining knowledge gaps across the four legal categories, and provides exact instructions for completing the knowledge base.

---

## 1. Category Status Overview

| Category | Ingested & Verified | Incomplete / Summary | Missing Gaps |
|---|---|---|---|
| **1. Statutory Legislation** | None (Awaiting full 107-section Act) | cpa_2019_act.txt (25 sections summary) | Complete Act No. 35 of 2019 PDF |
| **2. Regulatory & CCPA** | cpa_ecommerce_rules_2020.pdf<br>cpa_jurisdiction_rules_2021.pdf | ccpa_misleading_ads_2022.txt (excerpts) | cpa_mediation_rules_2020.pdf<br>cpa_commission_rules_2020.pdf<br>ccpa_misleading_ads_2022.pdf (full) |
| **3. NCH Procedures** | 
ch_sop_and_faq.html (Complete live SOPs) | None | None |
| **4. e-Jagriti & Commissions** | None | None | ejagriti_edaakhil_manual.pdf<br>Official fee schedule & scrutiny SOP |

---

## 2. Priority Documents Needed for Complete Coverage

### Document 1: The Consumer Protection Act, 2019 (Full 107-Section Act)
- **Status**: The knowledge base currently contains data/raw/1_statutory/cpa_2019_act.txt, which is a **reconstructed summary of 25 core sections**. To provide 100% statutory coverage, the full 107-section enactment is needed.
- **Official Source**: Ministry of Law and Justice (Legislative Department)
- **Official Link**: [https://legislative.gov.in/act-no-35-of-2019-consumer-protection-act-2019](https://legislative.gov.in/act-no-35-of-2019-consumer-protection-act-2019)
- **Alternative Mirror**: [India Code Portal (when accessible)](https://www.indiacode.nic.in/handle/123456789/15256)
- **Expected Filename**: cpa_2019_act.pdf
- **Target Destination**: data/raw/1_statutory/cpa_2019_act.pdf

### Document 2: Consumer Protection (Mediation) Rules, 2020
- **Status**: Missing
- **Official Source**: Department of Consumer Affairs (DoCA)
- **Official Link**: [https://consumeraffairs.gov.in/pages/consumer-protection-acts](https://consumeraffairs.gov.in/pages/consumer-protection-acts)
- **Expected Filename**: cpa_mediation_rules_2020.pdf
- **Target Destination**: data/raw/2_regulatory_ccpa/cpa_mediation_rules_2020.pdf

### Document 3: Guidelines for Prevention of Misleading Advertisements, 2022 (Full Gazette)
- **Status**: Only partial excerpts are present (ccpa_misleading_ads_2022.txt)
- **Official Source**: Central Consumer Protection Authority (CCPA)
- **Official Link**: [https://ccpa.doca.gov.in/act-and-rules.php](https://ccpa.doca.gov.in/act-and-rules.php)
- **Expected Filename**: ccpa_misleading_ads_2022.pdf
- **Target Destination**: data/raw/2_regulatory_ccpa/ccpa_misleading_ads_2022.pdf

### Document 4: e-Daakhil / e-Jagriti Online Filing Citizen User Manual
- **Status**: Missing
- **Official Source**: National Informatics Centre (NIC) / NCDRC
- **Official Link**: [https://edaakhil.nic.in/edaakhil/help/CitizenManual.pdf](https://edaakhil.nic.in/edaakhil/help/CitizenManual.pdf)
- **Expected Filename**: ejagriti_edaakhil_manual.pdf
- **Target Destination**: data/raw/4_ejagriti_commissions/ejagriti_edaakhil_manual.pdf

---

## 3. Incremental Ingestion Instructions

Whenever you place any of these files into their respective folders:
`ash
uv run python scripts/ingest_data.py
`
The ingestion engine automatically detects new files by SHA-256 hash, extracts provisions, generates embeddings, and updates the legal knowledge graph without re-indexing untouched documents.
