# OmniVoice FastAPI Fork Review

Review target:

- Repository: `https://github.com/diogod2r/OmniVoice-FastAPI`
- Reviewed revision: `930cb452437f4c4987d9b184e9a0074fbfd3bb37`
- Review date: 2026-06-02
- Scope: lightweight security and maintainability review for a Tailscale-only
  remote Hermes OmniVoice MVP.

## Summary

The project is useful as a reference for an OpenAI-compatible OmniVoice
FastAPI shape. It should not be exposed or relied on as-is for Hermes operator
traffic because the reviewed revision has no authentication middleware, binds
Docker containers to `0.0.0.0`, exposes `/docs` and `/web`, allows CORS `*`,
and accepts uploaded or base64 reference audio.

Recommendation: use it only after adding bearer-token enforcement in a fork or
placing it behind an authenticated local reverse proxy. Keep Tailscale ACLs as
the network boundary and bind the service only to the Mac Studio Tailscale
interface or loopback plus proxy.

## Findings

| Area | Finding | Impact | Required Control |
| --- | --- | --- | --- |
| Dependencies | Dockerfiles install `omnivoice`, `fastapi`, `uvicorn[standard]`, and `python-multipart` without pinned API deps. CPU image pins PyTorch CPU to 2.3.0. | Rebuilds can drift. | Pin service dependencies in a fork before production use. |
| Dockerfiles | GPU and CPU containers run `uvicorn main:app --host 0.0.0.0 --port 8880`. | Service binds all container interfaces. | Publish only on the intended Tailscale interface or behind a local auth proxy. |
| Compose | Compose maps `8880:8880` by default. | Easy LAN exposure if the host firewall permits it. | Do not use broad host-port publishing on a shared LAN. |
| Auth | No bearer-token or API-key check was present in `main.py`. | Any network peer can call TTS, clone, design, docs, and web UI. | Add auth middleware or authenticated reverse proxy before Hermes uses it. |
| Upload handling | `/v1/audio/clone` accepts file uploads and base64 audio, writes temp files, and deletes them after generation. | Upload endpoints expand attack surface and disk pressure risk. | Disable clone endpoint or gate it behind auth and request-size limits. |
| Filesystem writes | Reference audio is written to system temp; model cache uses `/app/models` volume. | Expected for model serving, but needs disk monitoring. | Bound temp and model volumes; keep them out of git/backups unless intended. |
| CORS | `allow_origins=["*"]`, all methods, all headers. | Browser-origin access is unrestricted. | Restrict CORS or disable web UI for operator deployments. |
| Logging | Logs model load, generation failures, duration, and exceptions. Request text is passed to model exceptions and could appear in traces. | Operator text may leak into logs on failures. | Review logging and avoid full request text in exception details. |
| Docs and web UI | `/docs`, `/web`, `/v1/voices`, `/v1/models`, and `/health` are unauthenticated. | Discovery and use are trivial for any reachable peer. | Require auth for all endpoints or disable docs/web in deployment. |
| API schema | `/v1/audio/speech` supports `model`, `input`, `voice`, `response_format`, `speed`, and other generation controls. | Good fit for Hermes remote wrapper. | Treat schema as reference until pinned to a fork revision. |

## Decision

Use the OpenAI-compatible `/v1/audio/speech` schema for the Hermes remote
client wrapper. Do not vendor or depend on the upstream service as-is. The
Mac Studio service must enforce bearer auth and stay reachable only through
Tailscale.

## Minimum Fork Changes

- Add bearer-token middleware for every endpoint, including `/health`, `/docs`,
  `/openapi.json`, and `/web`.
- Add request-size limits for multipart clone/design endpoints.
- Restrict CORS to operator-approved origins or disable it.
- Add a deployment option to disable `/docs` and `/web`.
- Bind to loopback or a specific Tailscale address, not broad LAN interfaces.
- Avoid logging full request text, uploaded filenames, or authorization data.
- Pin Python package dependencies and base image tags.
