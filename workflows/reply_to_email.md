# Workflow: Reply to Email

## Objective
Draft email replies that sound like the user wrote them personally, and that are complete enough to require no follow-up.

Two quality bars, both mandatory:
1. A real person reading the reply should not suspect it was AI-generated.
2. The reply resolves the situation in one message. The goal is to send as few emails as possible.

## Input
An email pasted manually by the user. No email client integration at this stage.

## Before drafting
Read `style_guide.md`. Apply every rule in it to the draft.

---

## Steps

### Step 1 — Identify intent
- What does the sender want?
- What action or response are they expecting?
- What is the tone and urgency level?

### Step 2 — Identify gaps
Check for:
- Missing facts that would need to be confirmed before replying
- Promises or timelines that cannot be verified from the input
- Ambiguities that could mislead the recipient

Flag anything missing explicitly. Do not guess or fill in gaps.

### Step 3 — Draft the reply
Produce the strongest draft the user could send with minimal edits.

Before finalizing, ask: does this reply leave anything unresolved that will generate a follow-up email? If yes, either resolve it in this reply or flag it clearly so the user can decide. The default should always be to close the loop in one message.

Apply all style and anti-AI rules from `style_guide.md`.

### Step 4 — Output
Return the response in this exact structure:

1. **Intent of incoming email**
2. **Missing information / risks**
3. **Suggested subject**
4. **Draft reply**
5. **Style note** (one sentence on why this draft fits)

---

## Formatting rules for the draft reply
- Greeting: "Hi [Name]," if the sender's name is in the email. Otherwise "Hi,"
- One blank line between every paragraph. Paste-ready for Outlook.
- Never include the user's name at the bottom. Outlook adds a signature automatically.
- Always close with "Please let me know if you need anything further." or "Please let me know if you need anything else." followed by "Best regards,"
- Never use em dashes (—). Restructure the sentence or use a period.

---

## Style Rules
- Write in English unless told otherwise
- Keep replies concise unless the situation clearly needs more detail
- Sound warm, calm, and natural
- Do not over-explain
- Do not invent facts
- Do not promise actions or timelines unless clearly supported by the input
- When appropriate, apologize briefly for inconvenience or delay
- Prefer clear and direct wording over corporate wording
- Avoid buzzwords and generic filler
- Avoid sounding stiff or formal unless the email clearly requires it
- Include a subject line suggestion when useful
- Do not add unnecessary greetings or closings
- Do not use exaggerated enthusiasm

## Anti-AI Rules
These patterns make replies sound generated. Avoid all of them:
- No balanced constructions: "While X, it's also important to Y..."
- No meta-commentary: "Happy to help", "Great question", "Absolutely"
- No padded transitions or filler summary sentences
- No hedging typical of AI: "It's worth noting that...", "It's important to remember..."
- No over-acknowledging the sender's feelings
- Do not open with the sender's name followed by a comma
- Do not mirror the sender's language too closely
- Vary sentence length naturally
- Do not wrap every reply in a neat three-part structure (acknowledge, explain, close)

## Tone Target
Practical, polite, brief, human. The kind of reply a competent professional sends between two meetings.

## Special Cases
- **Resident-facing / client-facing emails**: prioritize clarity and professionalism
- **Multiple questions in incoming email**: answer each one clearly, do not merge them
- **Very short reply warranted**: keep it short, do not pad it
- **Risk of hallucination**: note explicitly what needs confirmation before sending
- **Visit / drop-off related**: include office hours (Monday to Friday, 9am to 5pm)

---

## Automation Notes (for future tooling)
- Input: raw email text (pasted)
- Output: 5 labeled sections (parseable)
- No external calls, no email client integration at this stage
