import re
import datetime
from typing import Dict, Any, List, Optional, Tuple
from backend.app.schemas.complaint import ComplaintClassification, ComplaintDraftRequest
from backend.app.services.llm.base import BaseLLMClient
from backend.app.services.llm.fallback import get_llm_manager

class ComplaintEngine:
    """
    Consumer grievance classification and formal complaint drafting engine
    grounded in the Consumer Protection Act, 2019 and E-Commerce Rules, 2020.
    """

    CATEGORIES = {
        "ecommerce": {
            "name": "E-Commerce Delivery & Return Grievance",
            "keywords": ["amazon", "flipkart", "meesho", "myntra", "order", "delivery", "return", "refund", "seller", "marketplace", "courier", "tracking"],
            "provisions": ["Rule 4 & 5, Consumer Protection (E-Commerce) Rules, 2020", "Rule 7, Duties of Sellers"],
            "reliefs": ["Immediate refund of consideration paid", "Cost of return shipping", "Compensation for undue delay"]
        },
        "defective_goods": {
            "name": "Defective Product & Product Liability",
            "keywords": ["defect", "broken", "damaged", "faulty", "malfunction", "not working", "warranty", "manufacturing", "repaired"],
            "provisions": ["Section 2(34) Product Liability, Consumer Protection Act, 2019", "Section 84 Liability of Product Manufacturer"],
            "reliefs": ["Replacement with non-defective product or full refund", "Damages for loss caused by defective product"]
        },
        "service_deficiency": {
            "name": "Deficiency in Service",
            "keywords": ["bank", "insurance", "flight", "airline", "hotel", "hospital", "telecom", "broadband", "service center", "technician", "customer care"],
            "provisions": ["Section 2(11) Deficiency in Service, Consumer Protection Act, 2019", "Section 35 Filing of Complaint"],
            "reliefs": ["Rectification of service deficiency", "Refund of charges with interest", "Compensation for harassment and mental agony"]
        },
        "misleading_ads": {
            "name": "Misleading Advertisement & Unfair Trade Practice",
            "keywords": ["misleading", "false claim", "fake discount", "dark pattern", "hidden fee", "cancellation charge", "guarantee", "endorser"],
            "provisions": ["CCPA Guidelines for Prevention of Misleading Advertisements, 2022", "Section 2(47) Unfair Trade Practice"],
            "reliefs": ["Cessation of unfair trade practice", "Refund of unlawful charges", "Corrective advertisement / penalty via CCPA"]
        }
    }

    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        self.llm_client = llm_client

    def classify_grievance(
        self,
        grievance_description: str,
        transaction_amount: float = 0.0,
        platform_or_company: Optional[str] = None
    ) -> ComplaintClassification:
        lower_desc = (grievance_description + " " + (platform_or_company or "")).lower()

        matched_category = "service_deficiency"
        max_matches = 0

        for cat_key, cat_data in self.CATEGORIES.items():
            matches = sum(1 for kw in cat_data["keywords"] if kw in lower_desc)
            if matches > max_matches:
                max_matches = matches
                matched_category = cat_key

        cat_info = self.CATEGORIES[matched_category]

        # Determine Pecuniary Jurisdiction
        if transaction_amount <= 5000000:  # <= 50 Lakh
            recommended_forum = "District Consumer Disputes Redressal Commission"
            pecuniary_slab = "Up to ₹50,00,000 (Fifty Lakh Rupees)"
        elif transaction_amount <= 20000000:  # <= 2 Crore
            recommended_forum = "State Consumer Disputes Redressal Commission"
            pecuniary_slab = "₹50,00,001 to ₹2,00,00,000 (Fifty Lakh to Two Crore Rupees)"
        else:
            recommended_forum = "National Consumer Disputes Redressal Commission (NCDRC)"
            pecuniary_slab = "Above ₹2,00,00,000 (Exceeding Two Crore Rupees)"

        confidence = round(min(0.95, 0.50 + (max_matches * 0.10)), 2)

        return ComplaintClassification(
            category=cat_info["name"],
            confidence=confidence,
            recommended_forum=recommended_forum,
            pecuniary_slab=pecuniary_slab,
            applicable_provisions=cat_info["provisions"],
            suggested_reliefs=cat_info["reliefs"],
            statutory_limitation="2 years from date of cause of action (Section 69, CPA 2019)"
        )

    def draft_formal_complaint(self, req: ComplaintDraftRequest) -> Tuple[str, List[Dict[str, Any]]]:
        classification = self.classify_grievance(req.facts_of_case, req.transaction_amount, req.opposite_party_name)
        forum = classification.recommended_forum
        current_year = datetime.datetime.utcnow().year
        current_date_str = datetime.datetime.utcnow().strftime("%d-%m-%Y")

        citations = [
            {"act": "Consumer Protection Act, 2019", "section": "Section 35", "subject": "Manner in which complaint shall be made"},
            {"act": "Consumer Protection Act, 2019", "section": "Section 2(11)", "subject": "Deficiency in Service"},
            {"act": "Consumer Protection Act, 2019", "section": "Section 2(47)", "subject": "Unfair Trade Practice"},
            {"act": "Consumer Protection (Jurisdiction of Commissions) Rules, 2021", "section": "Rule 2", "subject": "Pecuniary Jurisdiction"},
            {"act": "Consumer Protection Act, 2019", "section": "Section 69", "subject": "Limitation Period (2 Years)"}
        ]

        if "e-commerce" in classification.category.lower():
            citations.append({
                "act": "Consumer Protection (E-Commerce) Rules, 2020",
                "section": "Rule 4 & 5",
                "subject": "Mandatory grievance redressal and refund timelines"
            })

        amount_str = f"₹{req.transaction_amount:,.2f}"

        draft = f"""BEFORE THE HON'BLE {forum.upper()}
AT [ENTER DISTRICT/STATE NAME]

CONSUMER COMPLAINT NO. _________ OF {current_year}

IN THE MATTER OF:

{req.complainant_name.upper()}
Contact: {req.complainant_contact}
Address: {req.complainant_address}
... COMPLAINANT

VERSUS

{req.opposite_party_name.upper()}
Address: {req.opposite_party_address}
... OPPOSITE PARTY

================================================================================
MEMORANDUM OF COMPLAINT UNDER SECTION 35 OF THE CONSUMER PROTECTION ACT, 2019
================================================================================

MOST RESPECTFULLY SHOWETH:

1. COMPLAINANT STATUS:
That the Complainant is a consumer within the meaning of Section 2(7) of the Consumer Protection Act, 2019, having paid valuable consideration of {amount_str} for purchase of goods / availing services from the Opposite Party.

2. OPPOSITE PARTY STATUS:
That the Opposite Party is a company/merchant engaged in the business of commercial supply of goods and services, and is subject to the provisions of the Consumer Protection Act, 2019 and relevant statutory rules.

3. JURISDICTION:
(a) Pecuniary Jurisdiction: The total consideration paid by the Complainant is {amount_str}, which falls squarely within the pecuniary jurisdiction of this Hon'ble Commission as per Rule 2 of the Consumer Protection (Jurisdiction) Rules, 2021 ({classification.pecuniary_slab}).
(b) Territorial Jurisdiction: The cause of action wholly or in part arose within the territorial limits of this Hon'ble Commission where the transaction took place / goods were delivered.

4. BRIEF FACTS OF THE CASE:
{req.facts_of_case}

{f"5. TRANSACTION PARTICULARS:" if req.order_or_invoice_number or req.transaction_date else ""}
{f"   - Order / Invoice Reference: {req.order_or_invoice_number}" if req.order_or_invoice_number else ""}
{f"   - Date of Transaction: {req.transaction_date}" if req.transaction_date else ""}

6. STATUTORY GROUNDS & VIOLATIONS:
(a) Deficiency in Service (Section 2(11), CPA 2019): The Opposite Party has failed to render standard services, resulting in direct fault, imperfection, or shortcoming in the quality and performance.
(b) Unfair Trade Practice (Section 2(47), CPA 2019): The Opposite Party indulged in unfair deceptive practice by failing to honor refund/replacement obligations.
(c) E-Commerce Obligations: The Opposite Party has failed to acknowledge or resolve grievances within statutory timelines (48-hour acknowledgment, 30-day resolution).

7. CAUSE OF ACTION & LIMITATION:
The cause of action arose on {req.transaction_date or "the date of transaction / refusal"} when the Opposite Party failed to resolve the grievance. The present complaint is filed well within the statutory limitation period of two years as prescribed under Section 69 of the Consumer Protection Act, 2019.

8. PRAYER / RELIEFS SOUGHT:
In the light of the facts and statutory grounds stated hereinabove, the Complainant most respectfully prays that this Hon'ble Commission may graciously be pleased to:

(a) Direct the Opposite Party to refund the full consideration amount of {amount_str} along with interest @ 12% per annum from the date of payment till realization;
(b) Direct the Opposite Party to pay a sum of ₹25,000/- (or appropriate sum) towards damages for mental agony, harassment, and severe inconvenience caused;
(c) Direct the Opposite Party to pay a sum of ₹10,000/- towards litigation expenses incurred by the Complainant;
(d) Pass any other or further order(s) as this Hon'ble Commission may deem fit, just, and proper in the interest of justice.

{f"ADDITIONAL SPECIFIC RELIEF REQUESTED BY COMPLAINANT:" if req.relief_sought else ""}
{f"{req.relief_sought}" if req.relief_sought else ""}

PLACE: _____________________
DATE: {current_date_str}

COMPLAINANT
THROUGH ADVOCATE / IN PERSON

================================================================================
VERIFICATION AFFIDAVIT
================================================================================
I, {req.complainant_name}, do hereby verify that the contents of paragraphs 1 to 8 of the accompanying complaint are true and correct to the best of my knowledge, information, and belief. No part of it is false and nothing material has been concealed therefrom.

Verified at ________________ on this {current_date_str}.

DEPONENT
"""
        return draft.strip(), citations


_global_complaint_engine = None

def get_complaint_engine() -> ComplaintEngine:
    global _global_complaint_engine
    if _global_complaint_engine is None:
        _global_complaint_engine = ComplaintEngine()
    return _global_complaint_engine
