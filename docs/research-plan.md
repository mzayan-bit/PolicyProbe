# PolicyProbe research plan

Working title: Change-Conditioned Regression Testing for Policy-Grounded Agents.

Revised November 27, 2026. This research plan supersedes release-driven priorities. Existing experiments establish scripted harness behavior. Publication claims require actual target-agent executions and independent labels.

## Question and experimental unit

Can policy-change semantics find incorrect action transitions at lower total selection and execution cost than strong simple selectors?

A test is a customer case executed against the same agent configuration under old and new policy snapshots. Reset the environment separately for each execution. Record both tool traces and resulting state, policy/index hashes, model identity, prompt version, seed where supported, usage, latency, and errors. Policy version is the controlled intervention.

Store permitted outcome sets for each snapshot, with action arguments and state predicates. Label expected transitions as change, preserve, or clarify. Preserve means both versions satisfy their respective oracle; repeating an incorrect action is a failure. Track old-correct/new-wrong separately from persistent errors and old-wrong/new-correct. A changed action can be correct. Clarification cases include a specified missing fact and allowed follow-up; generic abstention does not automatically pass. Unsupported or conflicting policies go to manual adjudication.

## Dataset

Keep v1 as a smoke-test artifact. Create v2 with 30 independently authored policy-version pairs across returns, cancellation, and booking modification, initially ten per domain. Target 20 customer cases per pair, including changed and unchanged outcomes, boundaries, exceptions, clause interactions, and selected clarification cases. Verify realistic constraints and document exact temporal semantics.

Use structured rules to create expected state predicates, then independently review the prose and labels. The selector receives the policies and customer inputs, never the ground-truth transition group or expected actions. When using a policy parser, its inferred groups remain predictions. Include an oracle-information ablation separately.

Start with three development pairs and one real model before authoring all 30. For the pilot, reserve complete pairs before tuning. For final generalization, partition by policy family and change mechanism and perform leave-one-domain-out evaluation where sample counts support it. Specify these splits before collecting final results. Date/window substitutions of the same template do not establish unseen-family generalization.

## Selectors and comparisons

Use a common fixed candidate pool first. Compare random order, semantic similarity to the diff, category/diversity sampling, and semantic similarity plus explicit boundary-case selection. Add historical-failure ranking under an equally available history condition. Reproduce applicable black-box methods and document CASPER adaptation after reviewing its artifact and assumptions.

The candidate method infers changed conditions, exceptions, relevant tool actions, and expected transition groups, then prioritizes boundaries and interacting clauses while reserving coverage for predicted unaffected cases. Select allocation and scoring weights on development data only. Add adaptive reranking only after a fixed ranking demonstrates a useful signal.

Ablate transition prediction, exception retrieval, unchanged-case coverage, and adaptation. Match target model, prompts, environments, candidate pools, history access, and operational budgets. Report missing prerequisites for comparisons rather than substituting a weaker method under the same name.

## Measurements and cost

Primary curves show confirmed incorrect transitions discovered versus total execution count and versus total selection plus execution cost. Report discovery in expected-change and expected-preserve groups separately, time/cost to first confirmed failure, missed unaffected failures, and stochastic false alarms.

Deduplicate seeded defects by injected cause. For natural failures report unique failing cases and manually adjudicated mechanism clusters separately; count uncertainty explicitly. Use policy pairs as the resampling unit for confidence intervals.

Every old-policy execution, new-policy execution, confirmation repeat, failed attempt, selector call, embedding, and history acquisition has a recorded cost. Compare fresh runs and amortized reuse of old traces as separate settings. Include timeouts and censored runs in reports. A seed does not guarantee determinism.

Use full-pool repeated target runs as a reference on the small pilot to estimate detection recall. Allocate pilot repeats before final evaluation and measure stochastic error with identical-policy controls. Separate offline ranking over cached outcomes from prospective adaptive runs. Extend to at least two target models before broad model-generalization claims.

## Sequence and decision gates

1. Review the four related papers and available artifacts. Write a comparison matrix covering change type, oracle, history, prioritization, and cost. Lock the paired-run protocol.
2. Implement paired snapshots, action/state outcomes, and identical-policy controls. Verify refund, cancellation, and booking environments with deterministic fixtures.
3. Run one real model on three development pairs, approximately ten cases per pair, three repeats of each old/new execution: 180 agent episodes before selector and clarification costs. Measure actual resource use.
4. Implement strong simple selectors. Decide whether the proposed method warrants further development based on cost-adjusted failure discovery.
5. Expand to 30 pairs, review labels, freeze splits, and run evaluation. Compute the final budget from measured pilot costs before committing resources.
6. Publish code, dataset provenance, prompts, traces permitted for release, cost accounting, failure analysis, and a manuscript with claims limited to the results.

If semantic similarity plus boundary selection matches the method after total cost accounting, simplify the method claim. Consider a benchmark and empirical study only if its independent contribution is supported. Paper acceptance and novelty are unresolved.

## Constraints and continuity

The user confirmed free/local execution on November 27. Actual model availability is a pilot dependency. No paid calls are automatically authorized by this plan. The user confirmed solo work for now. Label checks will use independently implemented rule evaluators, blinded second-pass review, and disagreement logs. Independent human review remains a limitation to disclose.

Daily implementation continues with meaningful lowercase commits and actual dates. Preserve the existing installation, CLI, replay, adapters, and CI. Integration priorities now follow this research protocol; the remaining work can exceed 104 commits. Keep v0.1 release status separate from research completion.

## Initial sources

- TDAD, https://arxiv.org/abs/2603.08806
- CASPER, https://arxiv.org/abs/2608.00378
- Evaluating More with Less, https://arxiv.org/abs/2611.34617
- When Knowledge Changes, https://arxiv.org/abs/2607.26843

Their abstracts and the CASPER and black-box-selection HTML pages were consulted during this revision. Full artifact reproduction and comprehensive novelty review remain work items.
