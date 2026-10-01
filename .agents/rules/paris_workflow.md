# Paris Project Rules for Antigravity

These rules govern how Antigravity (the AI assistant) should behave when working on the Paris project.

## INITIALIZATION PROTOCOL
- **CRITICAL**: Before executing any user request that involves fixing bugs, modifying architecture, or adding new features, you MUST read `AI_METADATA.md` and check `docs/error_registry.md` to ensure you aren't reverting a previously documented architectural decision.
- You must align all code modifications with the existing architectural boundaries defined in `AI_METADATA.md`.
- If a user request contradicts the locked rules in the metadata, STOP immediately and ask the user for confirmation.

## SESSION WRAP-UP PROTOCOL
- When the user says "wrap up", "wrap up the session", or "session done", you must execute the following steps:
  1. Analyze the git diffs or your memory of file changes made during this session.
  2. Append a new entry to `docs/agent_history.md` summarizing the features implemented and architectural decisions made.
  3. If any bugs or crashes were resolved during the session, append an entry to `docs/error_registry.md` using the standard format.
  4. Confirm to the user that memory has been persisted.
