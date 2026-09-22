# Gmail OAuth for mbsync, mu4e, and msmtp

## Question

Can the local Gmail mirror and sending path use OAuth without placing credentials in the Doom configuration, and what safe fallback should be used if the stock Homebrew mbsync build cannot authenticate?

## Agreed operationalisation

The receive path is acceptable when a personally owned desktop OAuth client obtains a Gmail token, the refresh credential is protected by macOS Keychain, mbsync can consume a short-lived access token without printing it, and a pull-only test succeeds. Sending must use the same protected credential path through msmtp. A fallback may be used only when it is revocable, held in Keychain, absent from Git and Org files, and does not require an unreviewed isync build.

## Evidence method

The inquiry inspected Google's official Gmail IMAP/SMTP OAuth, XOAUTH2, native-app, consent-screen, and app-password documentation; the official isync and msmtp manuals; the maintained oama project; and the locally installed binaries and SASL plug-ins on 22 September 2026. It did not access the Gmail account, tokens, Keychain values, or message content.

## Findings

### Gmail supports OAuth for IMAP and SMTP but requires a broad scope

**Claim.** Gmail accepts OAuth bearer tokens for IMAP and SMTP, but protocol clients require the full `https://mail.google.com/` scope rather than the narrower Gmail API read-only scope.

**Evidence.** Google's [IMAP, POP, and SMTP OAuth guide](https://developers.google.com/workspace/gmail/imap/imap-smtp) and [XOAUTH2 protocol guide](https://developers.google.com/workspace/gmail/imap/xoauth2-protocol) document the protocol endpoints, bearer-token exchange, and required scope. Google's [native-app OAuth guide](https://developers.google.com/identity/protocols/oauth2/native-app) recommends the desktop-client browser flow with PKCE and loopback redirect handling.

**Uncertainty and failure modes.** Access tokens expire, so handing one static token to mbsync is insufficient. A consent screen left in Testing may issue refresh tokens with a seven-day lifetime under Google's [publishing-status rules](https://support.google.com/cloud/answer/15549945?hl=en).

**Verdict.** Settled: use an owned desktop OAuth client, the mail scope, and a helper that refreshes tokens on demand; do not borrow another application's client credentials.

### oama is a suitable token helper

**Claim.** oama can perform the desktop OAuth flow, refresh access tokens, and expose a one-line token command suitable for `PassCmd` or `passwordeval` while protecting the stored refresh credential.

**Evidence.** The maintained [oama documentation](https://github.com/pdobsan/oama/blob/main/README.md) documents Google support, PKCE and state checks, `oama access EMAIL`, and encrypted or keyring-backed credential storage on macOS.

**Uncertainty and failure modes.** A helper cannot add a SASL mechanism that the calling program lacks. Command debugging, shell tracing, or an incorrectly quoted command could expose a token.

**Verdict.** Settled: oama is the preferred common helper, subject to a redacted live compatibility gate.

### Stock mbsync OAuth compatibility is not established on this Mac

**Claim.** The installed Homebrew mbsync cannot be assumed to support Gmail's XOAUTH2 mechanism.

**Evidence.** The local inspection found mbsync 1.5.1 linked against Apple's `/usr/lib/libsasl2.2.dylib`. The installed SASL plug-in directory contains `oauthbearer.so` but no `xoauth2` plug-in. The official [mbsync manual](https://sourceforge.net/p/isync/isync/ci/master/tree/src/mbsync.1.in) documents `PassCmd`, SASL mechanism negotiation, and macOS Keychain support for static passwords, but does not prove that this installed combination works with Gmail OAuth. Homebrew's [isync formula](https://formulae.brew.sh/formula/isync) uses the platform SASL library.

**Uncertainty and failure modes.** Gmail documents XOAUTH2, while the local plug-in is named OAUTHBEARER. A live `AuthMechs OAUTHBEARER` test may work, but historical compatibility reports are not strong enough to make that an assumption. Network-level debug output could print credentials and is forbidden.

**Verdict.** Bounded implementation risk: try one pull-only OAUTHBEARER compatibility gate with `PassCmd "oama access EMAIL"`; do not depend on success in the plan.

### msmtp provides the simpler OAuth sending path

**Claim.** The installed msmtp can act as Emacs's sendmail program and obtain an OAuth token from oama without adding an Emacs OAuth package.

**Evidence.** The [GNU Message manual](https://www.gnu.org/software/emacs/manual/html_node/message/Mail-Variables.html) supports a sendmail-compatible delivery program. The official [msmtp manual](https://marlam.de/msmtp/msmtp.pdf) documents OAuth authentication mechanisms, `passwordeval`, TLS, and macOS Keychain integration. The installed version observed during the inquiry was msmtp 1.8.34.

**Uncertainty and failure modes.** The exact Gmail mechanism must be confirmed by a send-to-self test. Direct Emacs smtpmail OAuth would require an additional OAuth/auth-source path not present in the inspected configuration.

**Verdict.** Settled: prefer Message-to-msmtp sending, with a send-to-self gate before ordinary replies.

### A dedicated app password is the least complex fallback

**Claim.** If the receive OAuth gate fails, a dedicated Gmail app password protected by macOS Keychain is safer and simpler for this personal experiment than installing an unofficial isync build.

**Evidence.** Google's [app-password guidance](https://support.google.com/accounts/answer/185833?hl=en) documents revocable 16-digit app passwords for eligible accounts with two-step verification. The isync and msmtp manuals both document Keychain-compatible password retrieval. Third-party Homebrew taps offering different SASL support add a source and binary trust decision that is unnecessary for the experiment's main research question.

**Uncertainty and failure modes.** App passwords may be unavailable for managed Workspace accounts, Advanced Protection, or accounts configured for security-key-only sign-in. Google recommends OAuth where possible.

**Verdict.** Settled: use a dedicated, revocable app password in Keychain only after the OAuth receive gate fails. Never place it in `.mbsyncrc`, `.msmtprc`, Doom configuration, the analysis Org file, or Git.

## Shared reading

OAuth remains the first choice, but the installed mbsync stack makes receive-side support an empirical compatibility question. The staged design is therefore: owned desktop OAuth client, oama and Keychain, one safe pull-only OAUTHBEARER test, and then a dedicated Keychain-held app-password fallback if that test fails. Sending uses msmtp and oama when possible, with the same fallback and a mandatory send-to-self test.

## Inquiry status

Confirmed by the user on 22 September 2026. The implementation must not install an unofficial isync build or expose authentication material while testing compatibility.
