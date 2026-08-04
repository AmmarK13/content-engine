# YouTube API Audit Status

## Summary

Real YouTube uploads remain blocked pending Google's audit/review decision for sensitive scope access. The pipeline supports authenticated OAuth and a real upload adapter in code, but production upload must remain disabled until approval is confirmed.

## Current Status

- Status: Pending external review
- Blocking area: YouTube Data API scope verification/audit
- Scope requested: `https://www.googleapis.com/auth/youtube.upload`
- Last updated: 2026-08-03

## Submission Details

- Google Cloud project ID: content-engine-youtube-504414
- Submission date: Not yet submitted — blocked on landing page deployment (PR merged, pending ownership transfer to shehryarR and Netlify deploy)
- Google reference/case number: Not yet issued — assigned after submission

## Evidence In Repo

- OAuth flow script: `scripts/youtube_auth.py`
- Upload adapter: `providers/youtube_upload.py`
- Dependency present: `google-auth-oauthlib` in `pyproject.toml`

## Operational Rule Until Approval

- Keep S100 in dry-run mode only.
- Do not enable real upload paths in production runs.

## Update Checklist

When audit metadata is available, update this file with:

1. Google Cloud project ID.
2. Exact submission date (YYYY-MM-DD).
3. Google-issued case/reference number.
4. Current review state (pending, additional info requested, approved, rejected).
5. Any required remediation actions and owner.
