---
name: pdf-redact
description: Truly redact a PDF (names, companies, bank/account info, addresses) with the pdf-redact CLI. Always asks the user what to redact and shows a preview before writing. Use when the user asks to redact, black out or anonymize a PDF.
---
# pdf-redact

CLI: `pdf-redact` (~/projects/pdf-redact/pdf_redact.py, PyMuPDF via uv). Real redaction: removes text/image data under boxes, clears metadata, verifies.

Steps — never skip the asks:
1. `pdf-redact scan IN.pdf` and `pdf-redact text IN.pdf -p 1 2` to see what's sensitive. Note scanned-page and image warnings (text in images isn't caught; tell the user).
2. ASK the user what to redact. Offer a checklist of candidates you found grouped as: people's names, companies, bank/account/loan numbers, addresses, phones/emails, money amounts. Include name variants (e.g. "EXAMPLE", "Alex Example", "Example, Alex"). Wait for answer.
3. `pdf-redact preview IN.pdf [--signatures] -t "term" ... [-r 'regex'] -o <scratchpad>/preview`. Report hit counts and NOT FOUND terms; Read 1-3 preview PNGs to sanity-check; tell the user where previews are. ASK for confirmation / changes.
4. Only after a yes: `pdf-redact apply IN.pdf OUT.pdf <same flags>`. OUT always goes in ~/projects/pdf-redact/out/ as `<name>-REDACTED.pdf`; never overwrite the input. Report VERIFY result. `-b PAGES:x0,y0,x1,y1` blanks fixed areas (logos, text inside images). `--fill white` leaves blank space instead of black boxes.
