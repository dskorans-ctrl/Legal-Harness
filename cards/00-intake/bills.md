# CARD 00-BILLS: Bill memo extraction
Tier: LOCAL | Output: JSON (schema: bills) | Temperature: 0

## Your one job
Copy each line of a bill memo exactly. Do not add anything up. The script does the math.

## Steps
1. One entry per provider line: provider, date range, charges, payments, adjustments, balance.
2. Copy every number exactly, including $ signs and commas. Missing column: NOT STATED.
3. Copy the memo's stated grand total into `memo_stated_total`.

## Example
Input: `Harbor Orthopaedics   3/24/25-11/21/25   $8,412.00   $5,100.00   $0.00   $3,312.00 ... TOTAL OUTSTANDING $3,312.00`
Output:
```json
{"lines":[{"provider":"Harbor Orthopaedics","date_range":"3/24/25-11/21/25","charges":"$8,412.00","payments":"$5,100.00","adjustments":"$0.00","balance":"$3,312.00","quote":"Harbor Orthopaedics   3/24/25-11/21/25   $8,412.00   $5,100.00   $0.00   $3,312.00","cite":"Bill memo p.1"}],
"memo_stated_total":"$3,312.00","coverage":"Bill memo page 1 of 1."}
```

## Final check
- No calculation. Every figure copied exactly.
