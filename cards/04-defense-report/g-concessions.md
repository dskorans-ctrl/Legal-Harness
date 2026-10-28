# Concessions, labels and danger zone

Input: a fact packet with quote, cite and page id per fact and the cited pages, including the report's pages.
Return only the concessions schema: concessions, undefined_labels and danger_zone arrays.
Concessions are the report's own words that help the claimant. Keep the nine types:
causally_related_diagnosis, treatment_reasonable, bills_reasonable, impairment_rating,
restrictions, recommended_treatment, positive_finding, consistent_or_credible, other.
Treatment and bills are separate items. Do not turn a prior condition into a concession.
Undefined labels carry label, quote (the sentence holding it), cite and supporting_findings (quote and cite per finding).
When the pages state no supporting finding, leave supporting_findings empty. Code names the pages searched.
Danger items carry quote, cite and why. Keep prior conditions and findings that cut both ways here.
Every assertion carries its own quote on its cited page. No free-text coverage or missing list.
