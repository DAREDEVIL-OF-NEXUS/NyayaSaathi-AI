import os
import hashlib

def write_statute(filepath, content):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    h = hashlib.sha256(content.strip().encode("utf-8")).hexdigest()
    print(f"Authored {filepath} ({len(content)} chars, SHA256: {h[:12]}...)")

cpa_2019_text = """THE CONSUMER PROTECTION ACT, 2019
(ACT NO. 35 OF 2019)
[9th August, 2019]

An Act to provide for protection of the interests of consumers and for the said purpose, to establish authorities for timely and effective administration and settlement of consumers' disputes and for matters connected therewith or incidental thereto.

CHAPTER I - PRELIMINARY

Section 1. Short title, extent, commencement and application.
(1) This Act may be called the Consumer Protection Act, 2019.
(2) It extends to the whole of India.
(3) It shall come into force on such date as the Central Government may appoint.
(4) This Act shall apply to all goods and services.

Section 2. Definitions.
In this Act, unless the context otherwise requires,—
(1) "advertisement" means any audio or visual publicity, representation, endorsement or pronouncement made by means of light, sound, smoke, gas, print, electronic media, internet or website and includes any notice, circular, label, wrapper, invoice or such other documents;
(5) "complainant" means a consumer, any voluntary consumer association, Central or State Government, Central Authority, or legal heir;
(6) "complaint" means any allegation in writing made by a complainant to obtain relief under this Act for unfair contract, unfair trade practice, restrictive trade practice, defect in goods, deficiency in services, overcharging beyond MRP or agreed price, offering hazardous goods/services, or product liability claim;
(7) "consumer" means any person who buys any goods or hires/avails any services for a consideration which has been paid or promised or partly paid and partly promised, or under any deferred payment system, including online transactions through electronic means, but does not include a person who obtains goods for resale or commercial purpose (except exclusively for earning livelihood by self-employment);
(9) "consumer rights" includes right to safety against hazardous goods/services, right to be informed about quality, quantity, potency, purity, standard and price, right to be assured access to variety of goods/services at competitive prices, right to be heard, right to seek redressal against unfair trade practice, and right to consumer awareness;
(10) "defect" means any fault, imperfection or shortcoming in quality, quantity, potency, purity or standard required by law or contract or claimed by the trader;
(11) "deficiency" means any fault, imperfection, shortcoming or inadequacy in quality, nature and manner of performance required by law or contract, including any act of negligence or deliberate withholding of relevant information;
(16) "e-commerce" means buying or selling of goods or services including digital products over digital or electronic network;
(28) "misleading advertisement" means an advertisement which falsely describes product/service, gives false guarantee, conveys unfair representation, or deliberately conceals important information;
(34) "product liability" means responsibility of product manufacturer or seller to compensate for harm caused by defective product or deficient service;
(46) "unfair contract" means contract causing significant change in consumer rights including excessive security deposit, disproportionate penalty, refusal of early repayment, or unilateral termination;
(47) "unfair trade practice" includes false representations regarding standard, quality, grade, style, model, newness, sponsorship, warranty; bait advertising; refusal after selling goods/services to take back defective goods or refund consideration within 30 days; and unauthorized disclosure of personal confidential consumer data.
"""
write_statute("data/raw/cpa_2019_act.txt", cpa_2019_text)
cpa_2019_part2 = """
CHAPTER III - CENTRAL CONSUMER PROTECTION AUTHORITY
Section 10. Establishment of Central Consumer Protection Authority (CCPA) to regulate violation of consumer rights, unfair trade practices and false or misleading advertisements prejudicial to consumers as a class.
Section 17. Complaints to authorities may be forwarded in writing or electronic mode to District Collector, Commissioner of regional office, or Central Authority.
Section 18. CCPA powers to protect, promote and enforce rights of consumers as a class, prevent unfair trade practices, and issue recalls of dangerous goods.
Section 21. CCPA powers to direct discontinuance of false/misleading advertisements and impose penalties up to ten lakh rupees (up to fifty lakh rupees for subsequent contravention) on manufacturers/endorsers, and ban endorsements up to 1 year (up to 3 years for subsequent contravention).

CHAPTER IV - CONSUMER DISPUTES REDRESSAL COMMISSION
Section 28. Establishment of District Consumer Disputes Redressal Commission in each district.
Section 34. Jurisdiction of District Commission: entertaining complaints where consideration paid does not exceed prescribed limits (originally one crore rupees, amended by 2021 Rules to fifty lakh rupees). Complaint filed where opposite party resides/carries on business, cause of action arises wholly or in part, or where complainant resides or works for gain.
Section 35. Manner in which complaint shall be made: by consumer, registered consumer association, or one or more consumers having same interest. May be filed electronically (e-Daakhil).
Section 36. Proceedings: admissibility ordinarily decided within 21 days from filing.
Section 37. Reference to mediation: at first hearing or later stage, Commission may direct parties to consent to mediation within 5 days.
Section 38. Procedure: opposite party directed to give version within 30 days (extendable by 15 days).
Section 39. Findings of District Commission: orders to remove defects, replace goods, refund price with interest, pay compensation for injury/loss, pay punitive damages, discontinue unfair trade practice, recall hazardous goods, and award costs.
Section 40. Review: District Commission may review order for error apparent on face of record within 30 days.
Section 41. Appeal to State Commission: within 45 days from order, subject to deposit of 50% of awarded amount.
Section 47. Jurisdiction of State Commission: consideration exceeding fifty lakh rupees up to two crore rupees (under 2021 Rules), complaints against unfair contracts, and appeals from District Commissions.
Section 51. Appeal to National Commission: within 30 days, subject to deposit of 50% of awarded amount.
Section 58. Jurisdiction of National Commission (NCDRC): consideration exceeding two crore rupees, appeals from State Commissions, and appeals from Central Authority orders.
Section 67. Appeal to Supreme Court of India: within 30 days from National Commission order, subject to 50% deposit.
Section 69. Limitation period: complaints must be filed within two years from date on which cause of action arose. Delay may be condoned if sufficient cause is shown with recorded reasons.

CHAPTER V - MEDIATION
Section 74. Consumer mediation cell established attached to District, State, and National Commissions.
Section 79. Procedure for mediation: held in mediation cell within prescribed time.
Section 80. Settlement report signed by parties submitted to Commission for passing appropriate order.

CHAPTER VI - PRODUCT LIABILITY
Section 82. Application to every action for harm caused by defective product manufactured/sold or deficient service.
Section 83. Product liability action against product manufacturer, service provider or seller.
Section 84. Liability of product manufacturer: manufacturing defect, design defect, deviation from specifications, non-conformance to express warranty, failure to give adequate warning/instructions. Strict liability applies even without negligence or fraud.
Section 85. Liability of product service provider: faulty, deficient, imperfect service, negligence, withholding information, failure to give warnings, or non-conformance to warranty.
Section 86. Liability of product seller: substantial control over design/testing/packaging, alteration causing harm, independent express warranty that failed, unidentified manufacturer, or failure to exercise reasonable care/pass on warnings.
Section 87. Exceptions: product misuse, alteration, workplace employer warnings, or complainant under unauthorized alcohol/drug influence.

CHAPTER VII - OFFENCES AND PENALTIES
Section 88. Penalty for non-compliance with Central Authority directions: imprisonment up to six months or fine up to twenty lakh rupees or both.
Section 89. Punishment for false or misleading advertisement: imprisonment up to two years and fine up to ten lakh rupees (subsequent: up to 5 years and fifty lakh rupees).
"""
with open("data/raw/cpa_2019_act.txt", "a", encoding="utf-8") as f:
    f.write(cpa_2019_part2.strip() + "\n")
print("Appended CPA 2019 Chapter III-VII.")
ecom_text = """CONSUMER PROTECTION (E-COMMERCE) RULES, 2020
MINISTRY OF CONSUMER AFFAIRS, FOOD AND PUBLIC DISTRIBUTION
NOTIFICATION, New Delhi, 23rd July, 2020 (G.S.R. 452(E))

Rule 1. Short title and commencement: Consumer Protection (E-Commerce) Rules, 2020.
Rule 2. Scope and applicability: applies to all goods and services bought/sold over digital network, all e-commerce models (marketplace and inventory), single and multi-channel retailers, and overseas entities systematically offering goods/services to Indian consumers.
Rule 3. Definitions: e-commerce entity, marketplace e-commerce entity, inventory e-commerce entity, user.
Rule 4. Mandatory duties of e-commerce entities:
(1) Incorporated company or registered entity with resident nodal contact person.
(2) Prominent display of legal name, principal address, website, and customer care / grievance officer contact details.
(4) Establish adequate grievance redressal mechanism and appoint Grievance Officer with details published on website/app.
(5) Grievance Officer must acknowledge consumer complaint within 48 hours and resolve/redress within 1 month (30 days).
(6) No cancellation charges on consumers cancelling after purchase order unless equal charges are borne by entity for unilateral cancellation.
(7) No price manipulation or deceptive pricing practices.
(8) Absolute prohibition on unfair trade practices across all platforms.

Rule 5. Liabilities of marketplace e-commerce entities:
(1) Section 79 IT Act safe harbor conditioned upon compliance with intermediary guidelines.
(2) Require sellers to display: legal name, address, customer contact, country of origin, total single-figure price with itemized delivery and tax breakdown, return/refund terms, warranty/guarantee, and grievance officer details.
(3) Provide tracking ticket number for every registered consumer complaint.
(4) Transparently explain ranking parameters and search algorithm determinants.

Rule 6. Duties of sellers on marketplace:
(1) No unfair trade practices on marketplace platforms.
(2) Prohibition against posting fake consumer reviews or impersonating genuine consumers.
(3) Mandatory acceptance of returns and refunds: no seller shall refuse to take back goods, discontinue services, or refuse to refund consideration if goods/services are defective, deficient, spurious, or delivered beyond agreed schedule.
(4) Written contract with marketplace entity, appointment of Grievance Officer (48 hr acknowledgment, 1 month redressal).

Rule 7. Duties and liabilities of inventory e-commerce entities:
(1) Display total price, delivery terms, country of origin, return/refund policy.
(4) Prohibition against refusal of returns and refunds for defective, deficient, or non-conforming goods.
(5) Grievance officer with 48 hour acknowledgment and 1 month redressal SLA.

Rule 8. Contravention: provisions of Consumer Protection Act, 2019 apply for all violations.
"""
write_statute("data/raw/cpa_ecommerce_rules_2020.txt", ecom_text)

jurisdiction_text = """CONSUMER PROTECTION (JURISDICTION OF THE DISTRICT COMMISSION, THE STATE COMMISSION AND THE NATIONAL COMMISSION) RULES, 2021
MINISTRY OF CONSUMER AFFAIRS, FOOD AND PUBLIC DISTRIBUTION
NOTIFICATION, New Delhi, 30th December, 2021 (G.S.R. 896(E))

Rule 1. Short title and commencement: Consumer Protection (Jurisdiction of the District Commission, the State Commission and the National Commission) Rules, 2021.
Rule 2. Pecuniary jurisdiction of Consumer Commissions:
(1) District Commission: jurisdiction to entertain consumer complaints where the value of goods or services paid as consideration does not exceed fifty lakh rupees (up to Rs. 50,00,000).
(2) State Commission: jurisdiction to entertain consumer complaints where the value of goods or services paid as consideration exceeds fifty lakh rupees but does not exceed two crore rupees (Rs. 50,00,001 to Rs. 2,00,00,000).
(3) National Commission (NCDRC): jurisdiction to entertain consumer complaints where the value of goods or services paid as consideration exceeds two crore rupees (above Rs. 2,00,00,000).

Explanation: The value of goods or services paid as consideration shall be the actual consideration paid by the complainant consumer, and not the total aggregate claim including compensation.
"""
write_statute("data/raw/cpa_jurisdiction_rules_2021.txt", jurisdiction_text)

misleading_ads_text = """GUIDELINES FOR PREVENTION OF MISLEADING ADVERTISEMENTS AND ENDORSEMENTS FOR MISLEADING ADVERTISEMENTS, 2022
CENTRAL CONSUMER PROTECTION AUTHORITY (CCPA)
NOTIFICATION, New Delhi, 9th June, 2022 (F. No. J-25/4/2020-CCPA)

Guideline 1. Title and application: applies to all advertisements across print, TV, radio, internet, digital, and social media.
Guideline 4. Valid and non-misleading advertisement criteria: truthful representation, no exaggeration of capability, no misleading omissions.
Guideline 5. Bait advertisements prohibited: goods must be reasonably available at advertised prices; bait-and-switch tactics strictly barred.
Guideline 6. Surrogate advertising prohibited: brand extensions of restricted/prohibited products (e.g., alcohol, tobacco) strictly barred.
Guideline 7. Free claims: cannot describe product/service as "free" if consumer has to pay anything beyond unavoidable direct delivery cost.
Guideline 12. Endorser due diligence: celebrity endorsers and influencers must exercise due diligence verifying claims; mandatory disclosure of material connection with brand or trader.
"""
write_statute("data/raw/ccpa_misleading_ads_2022.txt", misleading_ads_text)
print("Statute seeding script fully prepared.")
