These files are repository ruleset templates for the NRV branch promotion flow.

They are based on GitHub's repository ruleset JSON body shape:
- `target`, `enforcement`, `bypass_actors`, `conditions`, `rules`
- `bypass_actors[].actor_type` can be `Integration`, `Team`, or `RepositoryRole`
- `bypass_actors[].bypass_mode` can be `always`, `pull_request`, or `exempt`

Before importing:
- Replace `__BYPASS_ACTOR_ID__` with the numeric ID of your GitHub App or Team.
- If you use a Team instead of a GitHub App, change `"actor_type": "Integration"` to `"actor_type": "Team"`.
- Review the required status check names after one PR run. In this repo they are expected to be `lint`, `unit`, `e2e`, and `docs_latest`, but GitHub may expose a slightly different check context depending on your workflow layout.

Recommended setup for this repository:
- `dev`: one ruleset with full PR+review+lint requirements, but the bot has `always` bypass so it can push the version bump commit directly after lint passes.
- `staging`: split into two rulesets.
- `staging-core`: PR required plus required checks, no bypass actor.
- `staging-approval`: approval requirement only, bot gets `pull_request` bypass.
- `master`: split into two rulesets.
- `master-core`: PR required, plus deletion/force-push protection.
- `master-approval`: approval requirement only, bot gets `pull_request` bypass.

Why the split matters:
- If you put required checks and required approvals in the same ruleset, a bypass actor can skip both.
- By splitting them, the bot can bypass the approval-only ruleset while GitHub still enforces the non-bypass checks ruleset.

Import path in GitHub:
`Settings -> Rules -> Rulesets -> New ruleset -> Import a ruleset`

Sources:
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/managing-rulesets-for-a-repository
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository
- https://docs.github.com/en/rest/repos/rules?apiVersion=2022-11-28
