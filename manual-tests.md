# ResolveX Phase 1 Manual Test Checklist

Use this checklist during the final handover. A result may be **PASS** only
after the exact check has been performed. Record a short note or a safe file
path under `evidence/phase1-final/` for each completed check.

Do not store passwords, session tokens, `.env` files, or database credentials
in the evidence folder.

| ID | Check | Result | Evidence / notes |
| --- | --- | --- | --- |
| CK01 | Customer A can sign in. | NOT RUN | |
| CK02 | Customer A can submit a new ticket and receives a reference. | NOT RUN | |
| CK03 | The new ticket appears in Customer A's My Requests list. | NOT RUN | |
| CK04 | Customer A can open the new ticket and read its original message. | NOT RUN | |
| CK05 | Customer A can send a follow-up on their own ticket. | NOT RUN | |
| CK06 | Customer A cannot see internal notes in the ticket screen. | NOT RUN | |
| CK07 | Customer B can sign in. | NOT RUN | |
| CK08 | Customer B cannot open Customer A's ticket in the UI. | NOT RUN | |
| CK09 | Customer B's direct API lookup of Customer A's ticket is denied or not found. | NOT RUN | |
| CK10 | Customer-facing ticket/message responses contain no private-note data. | NOT RUN | |
| CK11 | Manager/Admin can sign in. | NOT RUN | |
| CK12 | Manager can find the new ticket in All Tickets. | NOT RUN | |
| CK13 | Manager can open the ticket in focused Ticket Oversight. | NOT RUN | |
| CK14 | Ticket Oversight shows subject, original message, status, priority, and assignee. | NOT RUN | |
| CK15 | Manager can assign Agent A to the new ticket. | NOT RUN | |
| CK16 | Assignment change is shown in ticket activity/history. | NOT RUN | |
| CK17 | Manager can change ticket priority and status. | NOT RUN | |
| CK18 | Manager overview reflects current ticket and workload data. | NOT RUN | |
| CK19 | Agent A can sign in. | NOT RUN | |
| CK20 | The assigned ticket appears in Agent A's My Queue. | NOT RUN | |
| CK21 | Agent A can open the ticket workspace and read the original customer issue. | NOT RUN | |
| CK22 | Agent A can send a public reply to the customer. | NOT RUN | |
| CK23 | Agent A can add an internal note. | NOT RUN | |
| CK24 | Customer A can see Agent A's public reply. | NOT RUN | |
| CK25 | Customer A cannot see Agent A's internal note, author, timestamp, or private activity. | NOT RUN | |
| CK26 | Agent A can see Customer A's follow-up message. | NOT RUN | |
| CK27 | Agent A can send a final public reply and resolve the ticket. | NOT RUN | |
| CK28 | Manager can confirm final assignment, status, and activity. | NOT RUN | |
| CK29 | Ticket activity records assignment, status, priority, public-message, and internal-note events as applicable. | NOT RUN | |
| CK30 | Manager reassigns a ticket from Agent A to Agent B. | NOT RUN | |
| CK31 | Former assignee Agent A cannot reply, add a private note, or change protected ticket data after reassignment. | NOT RUN | |
| CK32 | New assignee Agent B can open and work the reassigned ticket. | NOT RUN | |
| CK33 | Manager can view and manage knowledge documents. | NOT RUN | |
| CK34 | Agent can view the approved knowledge library. | NOT RUN | |
| CK35 | Manager can view system status and sensible error handling. | NOT RUN | |
| CK36 | AI Assistant and AI Review screens remain disabled Phase 2 placeholders. | NOT RUN | |
| CK37 | Normal `docker compose down` then `up -d` preserves application data. | NOT RUN | |
| CK38 | Backup is restored to a separate database and restored records are readable. | NOT RUN | |
| CK39 | A fresh reviewer can start the project using only README instructions. | NOT RUN | |
| CK40 | Iffat explains the architecture, one relationship, a transaction, version conflict, persistence, backup vs recovery, and Phase 1 scope. | NOT RUN | |

## Suggested demonstration ticket

Use a new fictional ticket so the final demo is easy to identify.

```text
Subject: Refund has not arrived
Message: I returned my order last week but have not received my refund. Please help.
```

Suggested public reply:

```text
Please provide your return tracking reference so that we can check the refund status.
```

Suggested internal note:

```text
Need to verify the returned item before promising a refund date.
```

Suggested customer follow-up:

```text
The return tracking number is DEMO-12345.
```
