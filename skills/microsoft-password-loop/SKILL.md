---
name: microsoft-password-loop
description: "Fix a Microsoft / Entra ID (Azure portal, Entra, Office) sign-in loop that keeps asking to update the password after you change it. Use when a work/school account is stuck on 'Update your password' or the user says Microsoft keeps asking for a new password."
---

# Microsoft password-update loop

Symptom: signing in to portal.azure.com, entra.microsoft.com or Office keeps showing
"Update your password"; you change it, it accepts, then asks again.
Usual cause: the account's `forceChangePasswordNextSignIn` flag is stuck on.

## Account context

Use the affected organization’s work or school account. Confirm its tenant and available recovery methods with the owner; keep account names, backup locations, and recovery codes out of reports.

## Steps (stop at the first that works)

Close ALL private windows between attempts; private windows share cookies.

1. Confirm the account type: if mysignins.microsoft.com accepts it, it is a work/school
   account. Use the exact username shown top right there.
2. Change the password once at https://mysignins.microsoft.com/password (never-used
   password), then sign in at https://portal.azure.com in a fresh private window.
3. Reset via SSPR: https://passwordreset.microsoftonline.com (Global Admins are enrolled
   by default). If available, try it.
4. **Clear the forced-change flag:** Graph Explorer clears the flag even while the portal loops.
   - Open https://aka.ms/ge, sign in with the work account.
   - Sanity check: GET `https://graph.microsoft.com/v1.0/me`.
   - PATCH `https://graph.microsoft.com/v1.0/me` with body
     `{"passwordProfile":{"forceChangePasswordNextSignIn":false}}`
   - On permission error: Modify permissions → consent `User.ReadWrite.All`
     (or `Directory.AccessAsUser.All`), run again. Success = `204 No Content`.
   - Close private windows, sign in to the portal again.
5. If an admin session works anywhere (entra.microsoft.com, admin.microsoft.com):
   Users → the user → Reset password, untick "require change at next sign-in".
6. Last resort, sole admin locked out: Microsoft support admin recovery,
   https://aka.ms/supportphone, using the affected organization’s tenant domain.

## Not the cause (ruled out)

- System clock skew (checked against login.microsoftonline.com Date header).
- Needing Edge: any browser works; a separate browser profile or private window is enough.
