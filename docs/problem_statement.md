# Problem statement

> **Evidence status:** every number in this repo comes from a **simulated** dataset (10,000 visitors per cohort). Statements marked **[HYPOTHESIS]** need validation with real data. Nothing here is a **[VALIDATED]** finding.

## Problem
Six in ten applicants who create an account never reach a funded balance. The biggest loss in the simulated baseline sits between *account created* and *documents submitted* (about 30% lost), and about a third of first submissions are rejected for fixable reasons (blurry photo, name mismatch, expired ID, old address proof). Applicants wait roughly a day to learn the outcome. **[HYPOTHESIS]**

## Who is affected
- First-time applicants, most of them on mobile (62% of simulated traffic), who must photograph ID, take a selfie and upload address proof.
- Ops and support teams who handle rejections and "where is my application?" contacts.

## Why it matters
Each lost applicant carries acquisition cost with no revenue. Rejections also add manual-review load and delay.

## Goals
1. Raise visit-to-funded conversion from ~16.4% to 25% or higher within two quarters.
2. Cut first-submission document rejections by more than half (34% to 15% or lower).
3. Make verification status visible so applicants stop contacting support to ask.

## Out of scope
New verification vendors or changes to risk rules; business accounts and joint applications.

## Key assumptions to validate
| # | Assumption | Status |
|---|---|---|
| A1 | Most rejections are preventable at capture time | **[HYPOTHESIS]** |
| A2 | Waiting time after submission drives drop-off before verification | **[HYPOTHESIS]** |
| A3 | Capture-quality checks will not block good images on older phones | **[HYPOTHESIS]** |
| A4 | Faster approvals will not raise fraud | **[HYPOTHESIS]**, guardrail metric |
