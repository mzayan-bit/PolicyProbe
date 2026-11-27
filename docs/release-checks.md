# Release checks

The scheduled November 27 release remains pending. Complete these checks against the final commit before tagging v0.1.0.

- Install from a clean checkout and run all tests.
- Verify GitHub policy-review artifacts and normal CI.
- Record an end-to-end terminal demo including a finding and its replay.
- Publish measured results and identify scripted and model-backed runs.
- Verify the version and remote tag only after required checks pass.

Current limitations include fixed demo rules, a small synthetic benchmark, unverified actual local-model inference, and no mid-investigation checkpoint resume. The policy workflow reports document edits alongside a fixed regression smoke test. End-to-end automatic interpretation of arbitrary policy edits is unfinished.

The original November 25 batch was missed. Its seven commits were completed on November 27 with actual dates. The remaining release work continues after the original deadline.
