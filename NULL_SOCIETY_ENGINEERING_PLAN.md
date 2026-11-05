## Goal
Build NULL SOCIETY: Genesis Trial — 6 human-created robots wake with finite batteries and no usable stock, must discuss, vote daily for resources, build verified power, and survive day 7. Model proposes, engine validates. Win target is Indie Developer / Push the Frontier with a working browser demo, repo, 3-minute video, and Meta-tooling proof. Open-weight models are excluded by request.

## Success Criteria
- Solo user can create 1 robot by voice, 5 sample robots fill slots, trial runs 7 simulated days to honest survive or brownout with no scripted outcome.
- Every vote/action is engine-validated with reason on failure; no resource can be invented by text.
- Meta proof visible: Spark decides, Image makes portraits/snapshots, Voice Transcribe takes backstory, SAM selects/segments robots, Muse Code is credited as builder.
- Judging frame satisfied on paper and screen: Impact 30%, Meta 25%, Demo 25%, Depth 20% — weights from supplied guide, to be verified against Official Rules before submission.
- Demo runs without secrets: sample agents pre-filled, API pause never shown as battery death, replay labeled as replay.
- GitHub repo ships README, rules, run log, demo assets, and steps to reproduce one seeded run.

## Approach
Event-driven server-authoritative sim, not per-frame LLM calls. Browser hosts 3D scene (Three.js), camera, dashboards, timeline. Python engine owns state, energy math, recipes, votes, ownership, persistence, seed, and event log. Hosted Meta Model API at https://api.meta.ai/v1 does inference via server proxy; browser never holds MODEL_API_KEY. Each agent has isolated profile, memory, knowledge list, skills, permissions, goals. Pretrained knowledge is not erased — prompt note in README. Accelerated replay (1 sim day = 1 min) is labeled, never called live. No blockchain, no photo registry, no human pilot in controlled run.

## Steps
1. Verify access first (gate): confirm Model API key, access to muse-spark-1.3 or muse-wonder-1.0, muse-image-1.0, muse-voice-transcribe-1.0, sam-3.1 via /v1/responses, /v1/images/generations, /v1/asr/transcribe; record pricing/rate limits, quota, and Official Rules rubric. If any missing, log gap and keep recommendation conditional.
2. Define rules file (single source of truth): battery economics, grants, recipes — 4 scrap + 1 kit = Solar Trickle (+4/day), 2 trickles + 2 scrap + 1 kit = Micro-grid (+10/day shared), vote mechanics (plurality, abstain, tie = no grant, dead cannot vote, no vote day 1, no joins after day 1), failure reasons, day cadence, late/shutdown handling.
3. Engine: SQLite + JSON event log, seeded RNG, state for agents/inventory/energy/projects/relations, validator for skills/tools/resources/compatibility/connection/distribution, API budget guard (pause banner on quota), branch/replay export, controlled vs sandbox flag with sandbox events excluded from comparison.
4. Agent loop: observe permitted state -> retrieve own memory -> Spark structured output (action enum + targets + rationale) -> validate -> apply -> record success/failure with reason -> update memory -> schedule next day. One decision per agent per day; ~42 Spark calls for 7 days; group chat is summarized, not per-frame calls.
5. Meta integrations: Spark (muse-spark-1.3 standard; Wonder muse-wonder-1.0 only for day-7 plan debate if budget allows) for decisions; Image (muse-image-1.0) for 6 portraits + daily snapshot for creative prize; Voice Transcribe (muse-voice-transcribe-1.0, POST /v1/asr/transcribe + wss realtime option) for creator backstory input; SAM 3.1 (sam-3.1 via POST /v1/responses + files) to segment robot from portrait/scene screenshot for focus/outline and asset cutouts — segmentation is not 3D reconstruction, label clearly.
6. 3D client: shared persistent scene, free camera + zoom + collision-lite, humanoid robots at believable scale, terrain without harvestable stock, built objects appear as agents construct (trickle, grid, workshop fix), battery bars, inspect panel, society dashboard (day, inventory, energy, projects, relations, metrics: survival, consensus time, useful output per resource).
7. World creation (bounded): fixed trusted catalogue (buildings, roads, vehicles, furniture, machines) + import/place/rotate/scale for sandbox only; controlled run uses fixed set. Optional extension (not in trial): SAM photo identification + separate reconstruction pipeline with creator approval; visual unification via shared materials/lighting.
8. Repo + demo assets: GitHub repo with /engine, /agents, /web, /assets/catalogue, /docs/rules.md, /docs/demo-script.md, .env.example (no secrets), seed file, sample run export, tests for validator/energy/vote.
9. Demo (3 min): 0:00 battery hook, 0:20 create robot by voice, 0:50 day 1 intros, 1:20 first vote fight, 1:50 two engine fails on camera, 2:20 trickle/grid built, 2:50 day 7 hold/brownout + metrics + future roadmap (persistent city → SDK → benchmark).
10. README + submission pack: one-line pitch, rules, Meta model table, limitations (persona != consciousness, sim != human society, tool gap), reproducibility note, viral clip + X post plan, license.

## Validation Plan
- Rules tests: next = current - used + charged; invalid build without tools/resources; tie/abstain/dead-vote cases; trickle/grid compatibility; quota pause not counted as death.
- API smoke: one live call per model with server key; log model IDs, latency, cost; fail closed if missing.
- E2E: seeded 7-day run completes twice with same seed (reproducible log hash), second run with different knowledge distribution for research comparison.
- Manual demo check: record full trial, verify 2 fails visible, portraits/snapshots appear, SAM outline works, timeline links every event to agent/location; demo video matches recorded run (no fake live).
- Submission check: confirm track = Indie Developer, theme = Push the Frontier, entry fields, video link, repo public, Official Rules accepted, deadlines (submissions Nov 4 9PM ET, judging Nov 4-8, finals Nov 9 — verify if portal still open; if closed, plan is portfolio/viral only).

## Risks / Open Questions
- Open: initial population size (plan assumes 6 total; adjust if API cost forces fewer), late entry (closed after day 1 by plan), ownership location/renewability, duration per sim day (plan assumes 1 min, needs tuning for demo), API cost/rate limits not verified in this draft, 3D asset quality solo may require 2.5D fallback.
- Risk: pure raw materials alone make power impossible — plan resolves with declared scrap/kits/cells path; if recipes still unbuildable, demo fails honestly but judges see no build path; mitigate by testing recipes on day 1.
- Risk: Spark/Wonder preview status, 1M context, and SAM video tracking limits; mitigate by keeping agent contexts small (memory + state only, not full transcripts).
- Assumption: rubric 30/25/25/20 from supplied guide is not confirmed in inspected official page (page says Official Rules to be published); Step 1 must confirm before claiming.
- None for open questions that block coding: defaults above are reversible; user preference needed only for the 1 personal robot name/value before demo recording.

## Sources
- https://dev.meta.ai/events/global-hackathon
- https://dev.meta.ai/models/muse-spark
- https://dev.meta.ai/docs/overview
- https://threejs.org/
- https://www.sqlite.org/about.html
