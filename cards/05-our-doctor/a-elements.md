# Elements of our doctor's records

Input: a fact packet with quote, cite and page id per fact and the cited doctor's pages.
Return only elements, each with element, status (STATED or PARTIAL), quote, cite and absent_note.
The fixed order is treating_relationship, mechanism, history_prior_conditions, exam_findings,
imaging_reviewed, diagnosis, causation, treatment_reasonable_necessary_related,
bills_reasonable_related, work_status_restrictions, mmi, permanency_rating, future_treatment, records_reviewed.
STATED means the doctor wrote the element; copy the doctor's own words and leave absent_note empty.
PARTIAL means a related statement is present; quote it and state the missing part neutrally in absent_note.
Omit every element with no statement on the pages. Code computes NOT FOUND from the omitted elements.
Treatment and bills always remain separate. Preserve temporary or permanent marks and qualifiers.
Never suggest what the doctor should write. No invented negative quote and no pages_searched field.
