# Meta models used (hosted API only — no open weights in this build)

Base URL `https://api.meta.ai/v1`, auth `MODEL_API_KEY`. IDs verified
against https://dev.meta.ai/docs/overview on 2026-11-05.

| Job | Model | ID | Endpoint |
|---|---|---|---|
| Every robot vote + action decision | Muse Spark 1.3 | `muse-spark-1.3` | `POST /v1/responses` |
| Day-7 plan debate (optional, budget allows) | Muse Wonder | `muse-wonder-1.0` | `POST /v1/responses` |
| 6 portraits + daily world snapshot (creative prize) | Muse Image | `muse-image-1.0` | `POST /v1/images/generations`, `/v1/images/edits` |
| Creator backstory speech-to-text | Muse Voice Transcribe | `muse-voice-transcribe-1.0` | `POST /v1/asr/transcribe`, `wss://api.meta.ai/v1/asr/realtime` |
| Robot cutout for selection outline | SAM 3.1 | `sam-3.1` | `POST /v1/files` + `POST /v1/responses` (shape conditional on media-segmentation guide — verify live) |

Mock mode replaces all five with deterministic labeled stand-ins so the
demo runs with no key. Nothing mock is ever presented as a model result.
Built with Muse Code, Meta's agentic coding agent.
