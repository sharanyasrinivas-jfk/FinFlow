# Product requirements: onboarding v2

> Targets and effects are **[HYPOTHESIS]**. Simulated results appear only in `metrics_and_experiment_plan.md` and are labelled as such.

## Problem
See `problem_statement.md`.

## Goals
- Raise visit-to-funded conversion from 16.4% to 25% within two quarters.
- Cut document rejections by more than half by catching problems before submission.
- Make verification status visible so applicants stop contacting support to ask.

## Not in this release
New verification vendors or changes to risk rules. Business accounts and joint applications.

## Requirements
| ID | Requirement | Acceptance test |
|---|---|---|
| R1 | The camera screen checks sharpness, glare, corners and expiry before capture is accepted. | Blurry test images are blocked at least 95% of the time. |
| R2 | Every document step shows what is accepted, with a good and a bad example. | Checklist appears before the camera on first attempt. |
| R3 | Each rejection names the reason and offers a one-tap retry with documents kept. | No error uses a generic message; retry needs no re-entry. |
| R4 | A status page shows four stages with an estimate and sends SMS and email on change. | Status is accurate within 1 minute of the backend state. |
| R5 | Reviewer flags can be resolved by the applicant inside the app. | Median flag resolution under 2 hours of applicant response. |
| R6 | All events are logged per stage for the funnel dashboard. | Stage counts reconcile with backend within 0.5%. |

## Prioritization framework
Score = reach % x impact (1-3) x confidence % / effort (person-weeks). Inputs are product judgement. Top three are "Do now"; ranks 4-6 "Next"; the rest "Later". Implemented in `src/recommendations.py`.

| Rank | Feature | Score | Decision |
|---|---|---|---|
| 1 | Guided checklist with examples | 54.0 | Do now |
| 2 | Live photo-quality check on capture | 40.8 | Do now |
| 3 | Real-time status tracker with SMS updates | 26.7 | Do now |
| 4 | Progressive profile (defer optional fields) | 26.7 | Next |
| 5 | Fix errors in place, no restart | 20.4 | Next |
| 6 | Save and resume across devices | 10.5 | Next |
| 7 | Government e-KYC fetch | 8.8 | Later |
| 8 | Name-mismatch auto-reconcile | 3.3 | Later |
| 9 | Stuck-user support escalation | 2.4 | Later |

Note: ranks 3 and 4 tie on score; the tracker wins on list order. Treat them as equal and decide on dependencies. Impact and confidence are subjective, so sensitivity-test them before committing. e-KYC scores low mainly because of its 12-week effort and 50% confidence; its upside is the largest.

## Rollout
- Weeks 1-2: instrument events, confirm baseline.
- Weeks 3-6: quality check and checklist to 10%, then 50%.
- Weeks 7-10: status tracker and in-place fixes.
- Week 11: full rollout if guardrails hold for two weeks.

## Risks
- Strict photo checks may block good images on older phones. Mitigation: allow manual submit after two blocked tries.
- Faster approvals could raise fraud pressure. Mitigation: watch the false-accept guardrail weekly.
- Status promises set expectations. Mitigation: show ranges, not exact times.
