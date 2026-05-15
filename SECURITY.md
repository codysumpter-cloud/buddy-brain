# Security Policy

## Supported surface

Security fixes should target the current default branch and any actively used runtime or automation paths.

## Reporting a vulnerability

Please do **not** open a public issue for a credential leak, auth bypass, command-execution issue, or other sensitive vulnerability.

Instead:

1. gather the minimum reproducible details
2. include affected file paths, commit hashes, and impact
3. send the report privately to the maintainer through the preferred private contact path

If you are unsure whether something is security-sensitive, treat it as sensitive first.

## Secrets and sensitive material

Never commit:

- API tokens
- `.env` files with live secrets
- private bridge endpoints with credentials
- local machine paths that expose personal data
- raw incident logs containing secrets or personal identifiers

## Safe contribution defaults

- use placeholders in docs and examples
- redact secrets in screenshots and logs
- prefer least-privilege tokens for automation
- rotate any secret immediately if it may have been exposed
