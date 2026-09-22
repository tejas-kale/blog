# Personal Email Model Evaluation

This context defines the language used to compare typed-decision models on the owner's personal email triage judgements.

## Language

**Triage Action**:
The single reference choice for an Evaluated Email. `keep unread` makes no change; `mark read` clears the unread flag while retaining the inbox label; `archive` clears the unread flag and removes the inbox label while retaining the message in Gmail.
_Avoid_: Classification, disposition, action label

**Reply Requirement**:
The binary reference judgement that the owner needs to send a reply to an evaluated email.
_Avoid_: Engagement, response class, reply score

**Reference Decision**:
A Triage Action or Reply Requirement assigned by the owner before any model result is inspected.
_Avoid_: Ground truth, true label, gold label

**Evaluated Email**:
The latest inbound message selected from a conversation thread, together with eligible earlier thread text used as context. At most one Evaluated Email is selected from each thread.
_Avoid_: Sample row, document, email thread

**Target Inbox Population**:
Eligible inbound messages received from 1 January 2026 through the recorded extraction freeze time, including newsletters, receipts, notifications, and personal mail regardless of current read or archive state. Spam, trash, drafts, sent mail, and messages from the owner are outside the population.
_Avoid_: All email, mailbox data, inbox sample

**Uncertain Decision**:
A Reference Decision that the owner cannot assign confidently during hand-labelling. It remains flagged through repeat labelling and adjudication.
_Avoid_: Bad label, ambiguous email

**Evaluation ID**:
An opaque identifier used in the publishable Org analysis to refer to an Evaluated Email without exposing mailbox identifiers or content.
_Avoid_: Message-ID, email ID, row number

**Private Manifest**:
A Git-ignored local record that maps each Evaluation ID to its source message, content hash, sampling position, and retrieval metadata.
_Avoid_: Label table, public manifest, dataset

**Sampling Order**:
The reproducible seeded random order of eligible threads from which the first 100, 200, or 300 Evaluated Emails are taken under the predeclared expansion rule.
_Avoid_: Random sample, shuffled inbox

**Live Mail Store**:
The continuing local Maildir synchronised with Gmail and indexed by mu for daily use through mu4e. It is a changing source and is not the durable evaluation input.
_Avoid_: Evaluation corpus, mu database, Gmail backup

**Frozen Email Corpus**:
The private, Git-ignored copy of selected raw messages and thread context whose hashes define the durable evaluation input.
_Avoid_: Live Mail Store, inbox mirror, public dataset

**Canonical Email State**:
The deterministic plain-text representation of an Evaluated Email supplied unchanged to every model. It contains approved metadata, the current message, and as much recent earlier thread text as fits every model under the common truncation rule.
_Avoid_: Prompt, cleaned email, model-specific input

**Unsupported Input**:
An Evaluated Email for which the approved text-only conversion cannot supply the evidence needed for a decision, such as encrypted or attachment-only content. It reduces end-to-end coverage even when excluded from conditional model-quality scores.
_Avoid_: Parser error, excluded email, missing value

**High-Cost Error**:
A model result that clears an email whose Reference Decision is `keep unread`, or says no reply is required when the Reference Decision says a reply is required.
_Avoid_: Critical error, false negative, severe mistake

**Simulated Action Policy**:
The fixed probability rules that assign either `mark read`, `archive`, or defer without changing Gmail. It accepts `archive` at probability at least 0.99, accepts `mark read` at probability at least 0.95, requires Reply Requirement probability at most 0.05 for either action, and defers otherwise. It is evaluated only as evidence for whether a later limited automation trial merits separate consideration.
_Avoid_: Automation, classifier threshold, live policy

**Accepted Set**:
The Evaluated Emails for which the Simulated Action Policy selects `mark read` or `archive` instead of deferring. Its size and error rate are always reported together.
_Avoid_: Confidence region, confident emails, automated set

**Coverage**:
The size of the Accepted Set divided by the number of eligible Evaluated Emails. Unsupported Inputs remain in the denominator for end-to-end Coverage.
_Avoid_: Accuracy, acceptance rate, confidence
