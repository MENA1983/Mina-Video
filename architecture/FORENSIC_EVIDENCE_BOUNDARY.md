# Mina-Video Forensic Evidence Boundary

Mina-Video can execute bounded media-plane evidence collection requested by
Factory Cleanup/Forensics, including media-quality checks, render diagnostics,
provider experiments, and provenance evidence.

It does not become a control plane. Evidence assignments require a case ID,
an expiry condition, and an explicit evidence requirement.

The Factory remains responsible for:
- policy and approval;
- canonical ownership;
- credentials and governance;
- final publication activation;
- evidence reconciliation.

Mina returns media-plane evidence; Factory decides how that evidence affects
routing, research, or release state.
