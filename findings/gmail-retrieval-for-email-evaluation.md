# Gmail retrieval for the private email evaluation

## Question

Should recent Gmail messages be retrieved directly through the Gmail API for the analysis, or synchronised into a local Maildir and indexed for mu4e so that Emacs can read and pass them to the models?

## Proposed operationalisation

Compare the two routes on reproducible retrieval, Emacs access, preservation of Gmail thread and label semantics, OAuth or IMAP credential handling, offline inspection, private snapshotting, implementation effort, and the ability to keep raw message content outside Git. The analysis needs read-only access; it will not modify Gmail or apply mailbox actions.

## In-scope claims

- Whether the Gmail API can list and fetch messages from a fixed recent window, including raw MIME and thread identifiers.
- Which OAuth scopes and personal-project constraints apply.
- What mu4e itself stores and which synchronisation tool is required to create a local Maildir.
- Whether Gmail IMAP preserves the identifiers and labels needed for reproducible sampling.
- Which route best supports reading in Emacs and running the private evaluation.

## Unknowns

- Whether the user's Emacs already has mu4e, notmuch, or an IMAP synchroniser configured.
- Whether browser-based Gmail reading is acceptable during labelling.
- The eligible message and thread count in the chosen observation window.

## Evidence method

The inquiry inspected official Gmail API, OAuth, Gmail IMAP, mu, mu4e, and isync/mbsync documentation on 21 September 2026. It also inspected the local machine for installed commands and the active literate Doom configuration. No mailbox credentials or messages were accessed.

## Findings

### The Gmail API can retrieve a bounded recent corpus

**Claim.** The Gmail API can enumerate messages in an exact time window, preserve Gmail message and thread identity, and fetch the raw MIME needed for a private frozen corpus.

**Operationalisation.** The extractor must list every eligible message with pagination, retain immutable Gmail message and thread IDs, fetch raw MIME, and record the retrieval parameters and time.

**Evidence.** [`users.messages.list`](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list) accepts Gmail-style queries, label filters, and pagination with up to 500 results per page; list entries contain message and thread IDs. [`users.messages.get`](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get) with `format=raw` returns base64url-encoded RFC message content. The [message resource](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages) records immutable IDs, thread IDs, labels, and Gmail's internal timestamp. [Filtering documentation](https://developers.google.com/workspace/gmail/api/guides/filtering) states that date strings use midnight Pacific time, so exact epoch-second boundaries are required for the Europe/Berlin window.

**Not searched or run.** No Cloud project, OAuth client, query, or mailbox extraction was created.

**Uncertainty and failure modes.** API search does not expand account aliases in the same way as the Gmail interface, and its query behaviour is message-scoped rather than thread-wide. Eligibility must explicitly recognise every personal address and group selected messages by `threadId` before retrieving context.

**Verdict.** Settled: the API supports the bounded extraction required by this study.

### A Gmail query is not a durable snapshot

**Claim.** Re-running the same Gmail query later is insufficient evidence that the same corpus was evaluated.

**Operationalisation.** A reproducible extraction freezes selected raw bytes and their hashes rather than relying on a future live mailbox query.

**Evidence.** Gmail documents pagination but no snapshot or as-of token on `messages.list`. Its [synchronisation guide](https://developers.google.com/workspace/gmail/api/guides/sync) describes `history.list` as a short-lived incremental change feed whose old history IDs can expire and return 404. This cannot recreate an arbitrary past mailbox state.

**Not searched or run.** Snapshot consistency was not tested under concurrent delivery or label changes.

**Uncertainty and failure modes.** Messages can arrive or labels can change during multi-page enumeration. The extractor must finish promptly, record retrieval start and end, freeze selected raw MIME immediately, and preserve hashes in the Private Manifest.

**Verdict.** Settled: the private frozen corpus, not the Gmail query, is the durable input.

### Read-only API access requires a restricted OAuth scope

**Claim.** Reading Gmail bodies through the API requires `gmail.readonly`, which Google classifies as restricted, but a personal-use project does not require full verification.

**Operationalisation.** One named user authorises a local desktop client; credentials and tokens remain outside Git and grant no modification scope.

**Evidence.** Google's [scope reference](https://developers.google.com/workspace/gmail/api/auth/scopes) classifies `gmail.readonly` as restricted. The [Python quickstart](https://developers.google.com/workspace/gmail/api/quickstart/python) uses a desktop browser flow and local credential and token files. Google's [verification exception](https://support.google.com/cloud/answer/13464323) permits personal-use apps with fewer than 100 users to continue through the unverified-app warning. [Testing-audience documentation](https://support.google.com/cloud/answer/15549945) says test-user authorisations expire after seven days while a project remains in Testing.

**Not searched or run.** The user's existing GCP OAuth consent configuration was not inspected.

**Uncertainty and failure modes.** An unverified personal project presents a warning and remains subject to user limits. Token-file permissions and revocation must be verified during implementation.

**Verdict.** Settled: API retrieval is feasible for one personal account, with explicit token handling and read-only scope.

### mu4e requires a separate Maildir synchronisation route

**Claim.** mu4e does not fetch Gmail itself; it reads and indexes messages already present in a local Maildir.

**Operationalisation.** A mu4e route requires an external synchroniser, Maildir storage, `mu init`, indexing, and Doom module configuration.

**Evidence.** The official [mu4e manual](https://github.com/djcb/mu/blob/master/mu4e/mu4e.texi) states that mu4e is an Emacs client over `mu`, requires one-file-per-message Maildir storage, and delegates server retrieval and write-back to tools such as isync/mbsync. The [mbsync manual](https://isync.sourceforge.io/mbsync.html) documents IMAP-to-Maildir synchronisation, local state, mailbox patterns, and directional operations. On this Mac, `/opt/homebrew/bin/mu` and `/opt/homebrew/bin/mbsync` are installed, Emacs is 31.1, and the literate Doom `init.el` contains a disabled `(mu4e +org +gmail)` module.

**Not searched or run.** No Maildir, mu index, Gmail authentication, or mu4e session was created. The complete Doom configuration will be inventoried before any eventual edit, as required by the local configuration workflow.

**Uncertainty and failure modes.** The generic mbsync documentation does not supply a currently endorsed Gmail XOAUTH2 recipe. Default bidirectional synchronisation could change server state; any experimental mirror would need pull-only behaviour and a synthetic account or harmless folder test.

**Verdict.** Settled: the local prerequisites are mostly present, but mu4e adds synchronisation and indexing machinery beyond a bounded API extraction.

### Gmail labels complicate a Maildir mirror

**Claim.** Gmail's many-to-many labels can cause one logical message to appear in several synchronised Maildir folders unless the design deduplicates it.

**Operationalisation.** The sampling unit must be the Gmail message and thread identity rather than a Maildir pathname.

**Evidence.** Gmail's [IMAP extensions](https://developers.google.com/workspace/gmail/imap/imap-extensions) expose `X-GM-MSGID`, `X-GM-THRID`, and `X-GM-LABELS`. Gmail's [label guide](https://developers.google.com/workspace/gmail/api/guides/labels) distinguishes labels from folders and permits multiple labels on one message.

**Not searched or run.** No local Gmail label layout was synchronised or counted.

**Uncertainty and failure modes.** Mirroring multiple Gmail label-folders without Gmail IDs in the manifest can oversample duplicated messages and corrupt cardinality checks.

**Verdict.** Settled: API IDs provide the cleaner sampling key; any Maildir view must preserve or map them.

### A hybrid route is technically possible

**Claim.** A bounded API extractor can freeze selected raw messages into a private Maildir which `mu` indexes for read-only viewing in mu4e.

**Operationalisation.** The Gmail API owns selection and snapshotting. The resulting RFC messages are written with valid Maildir layout and opaque filenames outside Git; mu4e provides the Emacs review interface over that frozen corpus.

**Evidence.** The API supplies raw RFC content, while mu4e requires ordinary Maildir files and treats its Xapian database as a rebuildable cache. These interfaces compose without requiring a full ongoing Gmail IMAP mirror.

**Not searched or run.** No exporter or mu4e view was prototyped. Valid Maildir naming, Gmail metadata preservation, and the Emacs labelling interaction require implementation checks.

**Uncertainty and failure modes.** This route introduces a small exporter. If it changes MIME bytes, loses thread metadata, or writes unsafe filenames, reproducibility fails; raw-byte hashes and micro-fixtures must catch those faults.

**Verdict.** Settled as feasible: the hybrid preserves bounded API retrieval and Emacs reading while avoiding a bidirectional mailbox mirror.

## Shared reading

Both routes can supply the experiment. The Gmail API is the cleaner authoritative extractor for a fixed 100/200/300-message corpus because it exposes stable Gmail IDs, thread IDs, labels, precise filtering, and raw MIME. A full mbsync plus mu4e setup is more appropriate for a lasting Emacs email client. For this bounded study, an API-to-private-Maildir hybrid can give Emacs reading and hand-labelling without making a live IMAP mirror part of the evidence path.

## Remaining bounded unknowns

- The chosen month may contain fewer than 300 eligible unique threads.
- The Gmail API does not promise snapshot-consistent pagination; retrieval reconciliation is required.
- OAuth consent and token persistence must be smoke-tested in the user's project.
- The API-to-Maildir exporter and mu4e labelling flow have not been prototyped.

## Inquiry status

Confirmed by the user on 22 September 2026. A continuing mbsync Gmail mirror and mu4e will be the authoritative retrieval and daily email interface because the user also intends to operate Gmail from Emacs. The selected evaluation corpus will still be frozen and hashed separately from the live synchronised Maildir. The study population is all eligible inbound email received from 1 January 2026 through the recorded extraction freeze time; the earlier one-month proposal was superseded.

The user also confirmed that the structural census must contain up to 300 unique eligible threads under the documented filters. If fewer exist, all eligible 2026 threads are used and the precision limitation is reported rather than extending into 2025 or sampling repeated messages from a thread. The mu-index census must reconcile with an independently implemented Maildir-header census before the Sampling Order is generated.
