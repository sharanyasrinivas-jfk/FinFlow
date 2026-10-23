# Success metrics and A/B test plan

> **Labels:** **[SIMULATED]** = produced by `src/data_generator.py` from assumed inputs, so it only shows the pipeline works. **[HYPOTHESIS]** = expected effect to test. **[VALIDATED]** = confirmed by a real experiment (none yet).

## Metrics
| Metric | Baseline (page / simulated) | Target | Type |
|---|---|---|---|
| Visit to funded conversion | 16.4% / 16.5% | 25% or higher | Primary |
| Application completion (account -> documents submitted) | 70% / 70% | 85% | Primary |
| Document rejection rate (first submission) | 34% / 34% | 15% or lower | Primary |
| Median verification time | 26h / 25h | 10h or less | Secondary |
| Median time to first document submit | 18h / 18h | 6h or less | Secondary |
| Status-related support contacts per 1,000 applicants | 86 / 81 | 40 or fewer | Secondary |
| Fraud false-accept rate | 0.4% (assumed) / not modelled | No increase | Guardrail |
| Manual review cost per application | 1.0x (assumed) / not modelled | 0.8x or lower | Guardrail |

Definitions: *applicant* = created an account. *Rejection rate* = share of submissions rejected on first review. All timings are medians (hours between consecutive stages).

## Simulated pilot readout **[SIMULATED, not a finding]**
| Metric | Baseline | Pilot |
|---|---|---|
| Visit to funded | 16.5% | 28.8% |
| Application completion | 70% | 82% |
| Document rejection | 34% | 13% |
| Median verification (h) | 25 | 9 |
| Median first submit (h) | 18 | 5 |
| Support contacts / 1,000 | 81 | 37 |

These pilot values are built in as assumptions, so they confirm nothing. The simulated cohorts also use different weeks (before/after), which a real pilot should avoid.

## Proposed A/B test **[HYPOTHESIS]**
- **Hypothesis:** onboarding v2 (R1-R4) raises visit-to-funded conversion by at least 2 percentage points versus the current flow.
- **Unit and split:** randomise at visitor level (cookie/device ID, sticky), 50/50. Stage 1 ramp 10% -> 50% per rollout plan.
- **Primary metric:** visit to funded within 30 days of first visit. **Secondary:** completion, rejection rate, time to verify, support contacts. **Guardrails:** fraud false-accept rate, manual review cost.
- **Sample size:** 5,637 visitors per arm (about 11,300 total) to detect +2 pp from 16.4%, alpha 0.05 two-sided, power 80% (`analytics.sample_size_per_arm`). A +3 pp lift needs about 2,560 per arm.
- **Duration:** at least 2 full weeks (weekday effects) and until the sample is reached, plus a 30-day funding window for the primary metric. Do not stop early on a significant interim result.
- **Analysis:** two-proportion z-test with 95% CI (`analytics.two_proportion_ztest`); check device segments (mobile vs web) as exploratory only. Verify no sample-ratio mismatch (50/50 within chance).
- **Decision rule:** ship if the primary lift CI excludes zero and no guardrail is breached; hold if a guardrail degrades even when the primary improves; otherwise iterate.
- **Known risks:** novelty effects, seasonality, ops capacity changes during the test, and multiple comparisons across secondary metrics (treat as directional).
- **Instrumentation prerequisite:** R6, with stage counts reconciling to the backend within 0.5%, before the test starts.
