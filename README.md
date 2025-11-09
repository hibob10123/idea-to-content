# 🚀 Content Catalyst — AI-Powered Marketing Idea Generator

Content Catalyst translates a short business description into platform-native short-form video ideas, shot lists, and editing notes — optimized for quick production and social distribution.

This README explains how to set up the project locally, configure the Anthropic (Claude) API key, run the server, and use the app (including the follow-up chat for editing help).

---

## Quickstart (Windows / PowerShell)

1. Create and activate a virtualenv, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Set your Anthropic API key (temporary for the current shell session):

```powershell
# Replace the value with your real API key
$env:ANTHROPIC_API_KEY = "sk-..."
```

To persist the key for your user account (so it remains after closing PowerShell) use `setx`:

```powershell
setx ANTHROPIC_API_KEY "sk-..."
# Close and re-open PowerShell to pick up the persistent value
```

Security note: NEVER commit your API key to git. Keep it in environment variables or a secure secrets manager.

3. Run the app:

```powershell
python app.py
# or using the venv python explicitly
.\.venv\Scripts\python.exe app.py
```

4. Open http://127.0.0.1:5000 in your browser and try the UI.

---

## Endpoints

- `POST /idea-to-content` — main endpoint used by the UI.
	- Request JSON: { "description": "Short business description..." }
	- Response JSON: { status, input, ideas: [ ... ], source }

- `POST /idea-chat` — follow-up chat endpoint for asking editing-specific questions about a chosen idea.
	- Request JSON: { "idea": { ... }, "question": "How long should each shot be?" }
	- Response JSON: { status: 'success', reply: '...' }

You can test the endpoint with PowerShell's `Invoke-RestMethod` (after starting the server):

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5000/idea-to-content -Method POST -Body (ConvertTo-Json @{ description = "Smart indoor garden for apartments" }) -ContentType 'application/json'
```

Example follow-up chat (PowerShell):

```powershell
# use idea from server response as $idea (object); here we demonstrate the shape
$idea = @{ format='Reel'; title='...'; caption='...'; script='...'; scriptFull='...'; tone='fun'; duration='30s'; apps=@('CapCut') }
Invoke-RestMethod -Uri http://127.0.0.1:5000/idea-chat -Method POST -Body (ConvertTo-Json @{ idea = $idea; question = 'What music and cuts would you suggest for a 15s version?'}) -ContentType 'application/json'
```

---

## Prompt & Output Notes

- The app is designed to ask the Claude model for one focused short-form video idea (to save tokens).
- The backend enforces a JSON schema and will attempt to generate `editingNotes` automatically if the model omits them.
- If the model returns malformed JSON, you'll see debug logs in the server terminal with `=== Raw Claude response ===`. If that happens, copy that block into an issue or here so we can adapt the prompt/parser.

---

## Troubleshooting

- "Claude API error: Invalid JSON" — the model output isn't valid JSON. Look in the server log for `=== Raw Claude response ===` to inspect the raw string. Common fixes:
	- Slightly reword the business description to be less verbose.
	- Restart the server and try again; sometimes the model output includes stray characters.
	- If errors persist, paste the raw response into an issue so the parsing rules can be adjusted.

- Server fails to start with `ANTHROPIC_API_KEY` errors:
	- Ensure the environment variable is set in the same shell used to start the app.
	- Use `$env:ANTHROPIC_API_KEY = 'sk-...'` before `python app.py` for a temporary session value.

---

## Development notes

- Prompt tuning: the system prompt lives in `app.py` in `call_claude_for_ideas()` — you can tweak tone, audience, or required fields there.
- Frontend detail chat: The UI attaches a small chat box to the idea detail page and posts follow-ups to `/idea-chat`.
- To change the default Claude model, set the `CLAUDE_MODEL` environment variable (e.g., `claude-3.0` or other supported model) before launching the app.

---

## Contributing

If you'd like help improving prompts, parser robustness, or adding more social formats, open an issue or send a PR with small, focused changes.

---

Enjoy building with Content Catalyst! If you want, I can add a short `dev.md` with common debug checks and sample raw responses to help tune the parser.
