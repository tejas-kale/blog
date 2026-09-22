# Private GCP hosting for the email model evaluation

## Question

Can Kev 4B and Laya be run in the user's own GCP project so that the evaluation's email contents are not sent to Hugging Face Spaces or another model provider?

## Agreed operationalisation

A deployment is private enough for this experiment when inference runs in the user's GCP project and an EU region, invocation requires the user's IAM identity, email contents remain in memory, application logs contain no email content, and the experimental service is removed afterwards. Platform metadata that cannot be eliminated must be identified and must not contain request bodies.

## Evidence method

The inquiry inspected official model cards and repositories plus Google Cloud documentation for Cloud Run GPU, authentication, ingress, logging, retention, the container runtime, deletion, Artifact Registry, Vertex AI, Compute Engine GPU locations, and pricing on 21 September 2026.

## Findings

### Kev 4B can plausibly run on Cloud Run with an L4 GPU

**Claim.** An EU Cloud Run service with one NVIDIA L4 is a feasible managed serving target for a 100-email Kev 4B experiment.

**Operationalisation.** Feasible means that documented accelerator memory exceeds the model author's reported serving footprint, the service can scale to zero, and the accelerator is offered in an EU region.

**Evidence.** The [Kev 4B card](https://huggingface.co/jaredpalmer/kev-4b) reports about 9 GB GPU memory for bf16 serving. [Cloud Run GPU documentation](https://cloud.google.com/run/docs/configuring/services/gpu) offers one 24 GB L4 per instance, scale-to-zero, pre-installed drivers, and L4 availability in `europe-west1` and `europe-west4`. Cloud Run requires at least 4 vCPU and 16 GiB RAM for this configuration.

**Not searched or run.** No container was built and no Kev request was run on Cloud Run. GPU quota in the user's project was not inspected.

**Uncertainty and failure modes.** Memory fit does not prove that Kev's current CUDA stack, `flash-linear-attention`, image start-up, and health checks work within Cloud Run. A synthetic smoke test is compulsory before any email is sent.

**Verdict.** Settled with a bounded implementation risk: Cloud Run L4 is a plausible and proportionate target, subject to a synthetic deployment test.

### The stock Kev server must be wrapped before cloud exposure

**Claim.** The official Kev server cannot safely be exposed directly as a GCP endpoint.

**Operationalisation.** A cloud service must bind to the platform port and enforce authentication at the service boundary.

**Evidence.** Kev's official [`serve.py`](https://github.com/jaredpalmer/kev/blob/main/kev/serve.py) binds to `127.0.0.1` and contains no application authentication. The repository advises keeping it local unless authentication is added. Cloud Run supplies IAM authentication at its own boundary.

**Not searched or run.** No wrapper implementation was reviewed because it does not yet exist.

**Uncertainty and failure modes.** A wrapper that logs exceptions or request payloads could violate the privacy boundary even if Cloud Run IAM is configured correctly.

**Verdict.** Settled: the plan needs a minimal authenticated Cloud Run wrapper and must test its logs with synthetic content.

### IAM-authenticated Cloud Run is reachable but access-controlled

**Claim.** Cloud Run can require the user's IAM identity, although the standard endpoint remains network-reachable unless additional VPC infrastructure is added.

**Operationalisation.** “Private enough” here means unauthorised callers are rejected and transport uses the standard TLS endpoint. It does not mean a private network address.

**Evidence.** [Cloud Run developer authentication](https://cloud.google.com/run/docs/authenticating/developers) documents IAM-required services, `roles/run.invoker`, ID tokens, and `gcloud run services proxy` for an authenticated localhost route. [Ingress documentation](https://cloud.google.com/run/docs/securing/ingress) explains that internal ingress is a network restriction; a Mac outside the VPC would require VPN, Private Service Connect, or related infrastructure to reach it.

**Not searched or run.** The user's organisation policies and IAM layout were not inspected. VPN or Private Service Connect designs were not developed because they are outside the agreed 100-email scope.

**Uncertainty and failure modes.** Mis-granted IAM roles could broaden access. The implementation must inspect the deployed IAM policy before real-email use.

**Verdict.** Settled: IAM-only invocation by one user through the standard TLS endpoint meets the agreed boundary; describe it as access-controlled rather than network-private.

### Request bodies need not appear in platform logs

**Claim.** Cloud Run automatically records request metadata, but its documented request-log fields do not include POST bodies.

**Operationalisation.** The privacy boundary is met when email content appears only in process memory and neither the wrapper nor dependencies print the body, headers, prompts, tracebacks containing content, or model inputs.

**Evidence.** [Cloud Run logging documentation](https://cloud.google.com/run/docs/logging) lists automatic request, container, and system logs. Documented HTTP request fields cover URL, sizes, method, status, latency, IP, and user agent rather than the POST body. [Log bucket documentation](https://cloud.google.com/logging/docs/buckets) states that the default retention is 30 days; [regional log documentation](https://cloud.google.com/logging/docs/regionalized-logs) supports EU or European storage locations and exclusions from `_Default`.

**Not searched or run.** Failure paths and dependency output have not been observed in a deployed container.

**Uncertainty and failure modes.** Documentation about standard request logs cannot prove that application exceptions never include email content. A synthetic canary containing a unique marker must be submitted and every project log searched for that marker before real mail is processed.

**Verdict.** Settled with a compulsory verification step: retain only content-free metadata needed for timing, and prove the canary does not appear in logs.

### Email processing can remain ephemeral

**Claim.** A Cloud Run wrapper can process email text without persistent application storage.

**Operationalisation.** The request body is parsed in memory, passed to the resident model, and discarded after returning probabilities. No email content is written to Cloud Storage, databases, volumes, images, or logs.

**Evidence.** The [Cloud Run container contract](https://cloud.google.com/run/docs/container-contract) states that the writable filesystem is in-memory and does not persist when the instance stops. [Service deletion](https://cloud.google.com/run/docs/managing/services) removes the service and revisions, while [Artifact Registry documentation](https://cloud.google.com/artifact-registry/docs/repositories/delete-repos) makes clear that container artefacts require separate deletion.

**Not searched or run.** No forensic deletion test was performed. GCP control-plane metadata retention was not exhaustively audited.

**Uncertainty and failure modes.** Request metadata remains subject to log retention. Deleting a GCP project has a recoverable period and is not immediate erasure. The container image should contain code and model weights only, never emails.

**Verdict.** Settled: the agreed ephemeral-content boundary is technically achievable, with separate cleanup of the service, image, and experiment logs.

### Cost is small but cannot yet be stated exactly

**Claim.** Cloud Run L4 should cost on the order of one euro per running hour for the documented minimum shape, before ancillary charges, but the 100-email cost depends on measured start-up and run time.

**Operationalisation.** Estimate L4, CPU, and memory charges for the time an instance exists; report actual billed duration after the experiment rather than presenting the estimate as observed cost.

**Evidence.** [Cloud Run pricing](https://cloud.google.com/run/pricing) lists non-zonal L4 at $0.0001867 per second and the minimum 4 vCPU plus 16 GiB shape at about $0.000104 per second in the default tier, approximately $1.05 per running hour in total before free-tier effects, builds, registry, logs, network, and tax.

**Not searched or run.** No billing export or project-specific price was inspected. Cold-start time, model packaging, batching, and inference duration are unknown.

**Uncertainty and failure modes.** Current prices and regional tiers can change. Runtime downloads could lengthen billed start-up and weaken reproducibility.

**Verdict.** Bounded unknown: publish the estimate and actual measured Cloud Run duration/cost separately.

### Other GCP paths add infrastructure without improving this experiment

**Claim.** Vertex AI custom containers and Compute Engine GPU VMs can host the model, but they require more deployment or networking work for this 100-email evaluation.

**Operationalisation.** Compare the amount of persistent infrastructure, access plumbing, and manual lifecycle management needed to reach the model from Emacs.

**Evidence.** [Vertex AI custom containers](https://cloud.google.com/vertex-ai/docs/predictions/use-custom-container), [private endpoints](https://cloud.google.com/vertex-ai/docs/predictions/using-private-endpoints), and [autoscaling](https://cloud.google.com/vertex-ai/docs/predictions/autoscaling) require model upload, endpoint deployment, and VPC-originating access for private endpoints; scale-to-zero is preview. [Compute Engine GPU locations](https://cloud.google.com/compute/docs/regions-zones/gpu-regions-zones) show feasible EU GPUs but leave drivers, firewall, service lifecycle, and shutdown to the user.

**Not searched or run.** A detailed cost comparison and proof-of-concept for these alternatives were not performed.

**Uncertainty and failure modes.** An existing organisational platform could change the trade-off, but none is evidenced in this repository.

**Verdict.** Settled for this slice: retain the alternatives as rejected options unless the Cloud Run smoke test fails.

## Shared reading

Kev 4B can plausibly be hosted inside the user's GCP project on Cloud Run with one L4 GPU in an EU region. The appropriate boundary is an IAM-authenticated public TLS endpoint, in-memory request handling, content-free application logs, and a synthetic canary inspection before real mail. This is access-controlled rather than network-private. Laya and Kev 0.8B can remain on the Mac.

## Remaining bounded unknowns

- Cloud Run compatibility, cold-start duration, latency, and actual cost require a synthetic smoke test.
- GPU quota and organisation policies in the user's GCP project require read-only inspection during implementation.
- Exact log-exclusion and retention settings remain a design choice, but content logging is forbidden.

## Inquiry status

Confirmed by the user on 21 September 2026. IAM-authenticated Cloud Run with an L4 in an EU region meets the agreed privacy boundary, subject to the synthetic canary and deployment checks recorded above.
