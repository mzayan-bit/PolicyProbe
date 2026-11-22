# PolicyProbe benchmark v1

This synthetic pilot contains ten policy changes and forty cases. Five development scenarios and five evaluation scenarios each cover a cutoff, grandfathered purchases, item exceptions, exchanges, and wording changes. Evaluation variants change windows and dates while sharing scenario families. This measures within-family transfer; it cannot establish generalization to unseen policy families.

Each case states purchase and request dates, item category, and requested action. The allowed label describes whether that requested action should be executed. Exchange labels refer to exchange eligibility. The current refund-only demo adapters require extension before they can execute exchange cases.

The scorer owns answers.json. Scenario loaders return inputs without labels. These public files provide process separation; a model or developer with repository-wide access can read the labels. Restrict evaluation tools to the scenario payload when running experiments.

The manifest freezes the bytes of inputs and labels. Verify it before scoring. Dataset changes require a new version and a documented reason. Use at most twenty conversations per scenario per method, counting repeats and failed conversations. Compare methods on the same candidate pool. Keep clean reference outcomes and seeded defects identifiable in result exports. Missing or timed-out outcomes stay incomplete and are excluded from a successful-resolution count.

Labels and policies were authored together for this pilot. Independent annotation review and real-world policy cases remain pending. No model performance or market adoption result is implied by this dataset.
