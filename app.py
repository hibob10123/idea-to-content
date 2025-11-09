from flask import Flask, jsonify, request, render_template
from markupsafe import escape
import os
import json
from typing import List, Dict, Any
import time

try:
    import anthropic
except ImportError:
    anthropic = None

app = Flask(__name__)

# Configure Claude API from environment
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
CLAUDE_MODEL = os.environ.get('CLAUDE_MODEL', 'claude-3-haiku-20240307')

if anthropic and ANTHROPIC_API_KEY:
    claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
else:
    claude = None


def call_claude_for_ideas(business_description: str, max_ideas: int = 1, timeout: int = 25) -> List[Dict[str, Any]]:
    """Generate video content ideas using Claude API.
    
    Args:
        business_description: Text describing the business and goals
        max_ideas: Maximum number of ideas to generate
        timeout: API timeout in seconds
        
    Returns:
        List of idea dictionaries with keys: type, title, description, example, etc.
        
    Raises:
        RuntimeError: If Claude is not configured or API call fails
    """
    if not anthropic or not claude:
        raise RuntimeError("Claude API not configured - set ANTHROPIC_API_KEY")
        
    # Construct a detailed prompt that ensures JSON output tailored for modern Instagram Reels
    system = (
        "You are an expert social media strategist who specializes in modern Instagram Reels and short-form marketing aimed at young adults (18-35).\n\n"
        "Style & tone guidance:\n"
        "- Casual, witty, meme-native; playful sarcasm is ok when appropriate.\n"
        "- Immediate-action focus: strong 1-3s hook, product/demo visible within 3-5s, direct CTA.\n"
        "- Visual cues: UGC/creator-led, reaction close-ups, jump cuts, text overlays, fast pacing, 9:16 aspect ratio.\n"
        "- Keep language short, conversational, and punchy — avoid corporate phrasing.\n\n"
        "Output requirements (MUST follow exactly):\n"
        "Return ONLY a single valid JSON object using this exact schema with one idea in the ideas array. No extra text.\n"
        "{\n"
        "  \"ideas\": [\n"
        "    {\n"
        "      \"format\": \"Reel/TikTok (9:16)\",\n"
        "      \"title\": \"Short catchy title\",\n"
        "      \"caption\": \"One-line hook (<=8 words)\",\n"
        "      \"script\": \"Hook: ...\\nProblem: ...\\nSolution: ...\\nCTA: ...\",\n"
        "      \"scriptFull\": \"Shot-by-shot with timings (e.g., 0-3s hook; 3-8s demo; 8-12s CTA)\",\n"
        "      \"editingNotes\": [\"jump cuts\", \"face close-ups\", \"text overlay suggestions\"],\n"
        "      \"tone\": \"casual/witty/energetic\",\n"
        "      \"duration\": \"15s/30s/45s\",\n"
        "      \"apps\": [\"CapCut\", \"InShot\"]\n"
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Additional rules:\n"
        "1) Keep hooks visceral and attention-grabbing (reaction, surprising visual, or audio jump).\n"
        "2) Editing notes must include at least 2 concrete actionable tips (cuts, overlays, pacing, audio).\n"
        "3) Prioritize 15-30s Reels for younger audiences; allow 45-60s only if there is a clear storytelling reason.\n"
        "4) No prose outside the JSON object; do not include examples, explanations, or comments.\n"
        "5) No trailing commas or JSON comments.\n"
    )
    
    user = f"""Generate ONE short-form video idea for this business:

{business_description}

Requirements:
1. Strong hook in first 3 seconds
2. Clear problem-solution structure
3. Keep it under 60 seconds
4. Focus on key benefits
5. End with clear call-to-action

Format as clean JSON exactly matching the structure shown."""
    
    try:
        start = time.time()
        message = claude.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2000,
            temperature=0.7,
            system=system,
            messages=[
                {"role": "user", "content": user}
            ]
        )
        
        if time.time() - start > timeout:
            raise RuntimeError(f"Claude API call timed out after {timeout}s")
            
        # Claude-3 returns content as a list of content blocks
        text = message.content[0].text.strip()
        print("\n=== Raw Claude response ===\n", text, "\n===========================\n")  # More visible debug log
        
        # Clean and extract JSON
        text = text.strip()
        if not text.startswith('{'):
            print("WARNING: Response doesn't start with '{'. Raw response:", text)
            json_start = text.find('{')
            if json_start >= 0:
                text = text[json_start:]
            else:
                raise ValueError("No JSON object found in response")
                
        if not text.endswith('}'):
            json_end = text.rfind('}')
            if json_end >= 0:
                text = text[:json_end + 1]
            else:
                raise ValueError("No complete JSON object found")
                
        # Validate it's a single JSON object
        if text.count('{') != text.count('}'):
            raise ValueError("Mismatched braces in JSON")
            
        print("Extracted JSON:", text)  # Debug log
        
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            print("JSON parse error. Response:", text)  # Debug log full response
            raise ValueError(f"Invalid JSON: {str(e)}")
            
        if not isinstance(data, dict) or 'ideas' not in data:
            raise ValueError("Response missing 'ideas' array")
            
        ideas = data['ideas']
        if not isinstance(ideas, list):
            raise ValueError("'ideas' must be an array")
        print("Parsed ideas:", json.dumps(ideas, indent=2))  # Debug log
        
        if not isinstance(ideas, list):
            raise ValueError("Invalid response format - expected ideas array")
            
        # Validate and clean each idea
        clean_ideas = []
        for idea in ideas[:max_ideas]:
            if not isinstance(idea, dict):
                continue
            # Required fields
            required_fields = ['format', 'title', 'caption', 'script', 'scriptFull', 'tone', 'duration', 'apps']
            missing_fields = [f for f in required_fields if f not in idea]
            if missing_fields:
                raise ValueError(f"Idea missing required fields: {', '.join(missing_fields)}")
            
            # Validate required fields and types
            if not isinstance(idea.get('apps', []), list):
                raise ValueError("'apps' field must be an array")

            # Generate editing notes from scriptFull if not provided
            editing_notes = []
            if "time-lapse" in idea['scriptFull'].lower():
                editing_notes.append("Create time-lapse sequence")
            if "transition" in idea['scriptFull'].lower():
                editing_notes.append("Add smooth transitions between scenes")
            if "montage" in idea['scriptFull'].lower():
                editing_notes.append("Fast-paced editing for montage")
            if "CTA" in idea['scriptFull']:
                editing_notes.append("Add text overlay for call-to-action")
            editing_notes.append("Use upbeat background music")
            editing_notes.append("Add on-screen text for key points")

            # Clean and validate the idea
            clean_idea = {
                'format': str(idea['format'])[:100],
                'title': str(idea['title'])[:200],
                'caption': str(idea['caption'])[:1000],
                'script': str(idea['script'])[:1000],
                'scriptFull': str(idea['scriptFull'])[:2000],
                'editingNotes': editing_notes,
                'tone': str(idea['tone'])[:50],
                'duration': str(idea['duration'])[:20],
                'apps': [str(x)[:100] for x in idea['apps']][:5]
            }
            
            # Verify all fields have content
            empty_fields = [k for k, v in clean_idea.items() if not v]
            if empty_fields:
                raise ValueError(f"Empty required fields: {', '.join(empty_fields)}")
                
            clean_ideas.append(clean_idea)
            
        return clean_ideas
        
    except Exception as e:
        raise RuntimeError(f"Claude API error: {str(e)}")


def call_claude_followup(idea: Dict[str, Any], question: str, timeout: int = 20) -> str:
    """Ask Claude a follow-up question about a specific idea (editing, timing, assets).

    Returns a plain-text reply focusing on practical editing instructions and suggestions.
    """
    if not anthropic or not claude:
        # Simple local fallback
        return (
            "I don't have access to the AI right now. "
            "Quick tip: use jump cuts for pacing, keep hooks under 3s, add text overlays for CTAs, "
            "and choose upbeat royalty-free music. If you need a step-by-step edit, ask me what part to expand."
        )

    # Build a concise system prompt that includes the idea context
    idea_json = json.dumps(idea, ensure_ascii=False)
    system = (
        "You are an expert video editor and social media strategist. "
        "A user will ask follow-up questions about a specific video idea. "
        "Always give practical, actionable, and concise editing guidance (timings, cut type, overlays, b-roll, audio cues).\n"
        "Context idea JSON follows. Use it to reference specifics but DO NOT output the full JSON again.\n"
        f"IDEA_CONTEXT: {idea_json}\n"
    )

    try:
        message = claude.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=800,
            temperature=0.3,
            system=system,
            messages=[{"role": "user", "content": question}]
        )
        text = message.content[0].text.strip()
        return text
    except Exception as e:
        print("Claude followup error:", str(e))
        return "Sorry — I couldn't reach the AI right now. Try again in a moment."


def generate_marketing_ideas(business_description, max_ideas=6):
    """Generate a small list of content-marketing ideas from a business description.
    
    This is a simple, deterministic generator used as fallback when Claude API
    is not configured or fails.
    
    Returns a list of idea dicts with keys: type, title, description, example.
    """
    desc = (business_description or '').strip()
    short = (desc[:120] + '...') if len(desc) > 120 else desc

    # Basic heuristics: try to detect channel keywords in the description
    lower = desc.lower()
    channels = []
    if any(k in lower for k in ['instagram', 'ig', 'tiktok', 'reel']):
        channels.append('social')
    if any(k in lower for k in ['blog', 'article', 'seo']):
        channels.append('blog')
    if any(k in lower for k in ['email', 'newsletter']):
        channels.append('email')
    if not channels:
        channels = ['social', 'blog', 'email']

    ideas = []

    # 1. Social post idea
    ideas.append({
        'type': 'Social Post',
        'title': 'High-impact social carousel',
        'description': f"Create an Instagram carousel that tells a 5-step story about why customers choose you. Target: {', '.join(channels[:2])}.",
        'example': f"Slide 1: Problem. Slide 2: Your solution. Slide 3: Benefits. Slide 4: Social proof. CTA: Shop / Learn more. (Received: {escape(short)})"
    })

    # 2. Short video idea
    ideas.append({
        'type': 'Short Video',
        'title': '15s TikTok/Reel idea',
        'description': 'A fast before/after or transformation clip with upbeat music and a 1-line hook.',
        'example': "Hook: 'You won't believe this trick' -> 10s demo -> 3s CTA + brand shot"
    })

    # 3. Blog/article idea
    ideas.append({
        'type': 'Blog Post',
        'title': 'Long-form explainer or listicle',
        'description': 'Write a helpful resource (how-to or top N list) that answers common customer questions and targets SEO keywords.',
        'example': "Title: 'Top 7 ways to choose X for Y' — include product mentions and internal links."
    })

    # 4. Email idea
    ideas.append({
        'type': 'Email',
        'title': 'Short welcome series email',
        'description': '3-email sequence: welcome, benefits + social proof, limited-time offer.',
        'example': "Email 1: Welcome + brand story. Email 2: Bestsellers. Email 3: 10% off to convert."
    })

    # 5. Influencer / partnership idea
    ideas.append({
        'type': 'Influencer',
        'title': 'Micro-influencer co-create',
        'description': 'Partner with 3-5 micro-influencers for product trials and UGC collection.',
        'example': "Ask creators to show 'a day with' the product and link to a tracked discount."
    })

    # 6. Campaign idea
    ideas.append({
        'type': 'Campaign',
        'title': '7-day challenge / user-generated content campaign',
        'description': 'Encourage users to share short videos/posts using a hashtag and reward top posts.',
        'example': "Prompt: '7 days of X — share your results using #YourBrandChallenge'"
    })

    # Trim to max_ideas
    return ideas[:max_ideas]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/content-catalyst', methods=['POST'])
def content_catalyst():
    """Endpoint that behaves like a small chatbot: accepts a business idea and
    returns content-marketing ideas."""
    data = request.get_json() or {}
    # Accept either 'idea' or 'description' or 'text'
    business_description = data.get('idea') or data.get('description') or data.get('text') or ''

    if not business_description.strip():
        return jsonify({'status': 'error', 'message': 'Please provide a business idea/description.'}), 400

    # Try Claude first, fallback to local generator
    ideas = None
    error = None
    
    if ANTHROPIC_API_KEY and claude:
        try:
            ideas = call_claude_for_ideas(business_description)
        except Exception as e:
            error = str(e)
            print(f"Claude generation failed, falling back to local: {error}")
    
    # Fallback to deterministic generator
    if not ideas:
        ideas = generate_marketing_ideas(business_description)
        
    response = {
        'status': 'success',
        'input': business_description,
        'ideas': ideas,
        'source': 'claude' if ideas and not error else 'local'
    }
    if error:
        response['error'] = error
        
    return jsonify(response)


@app.route('/idea-chat', methods=['POST'])
def idea_chat():
    """Handle follow-up chat about a specific idea.

    Expects JSON: { "idea": { ... }, "question": "..." }
    Returns JSON: { status: 'success', reply: 'text' }
    """
    data = request.get_json() or {}
    idea = data.get('idea')
    question = data.get('question', '').strip()

    if not idea or not isinstance(idea, dict) or not question:
        return jsonify({'status': 'error', 'message': 'Provide an idea object and a non-empty question.'}), 400

    try:
        reply = call_claude_followup(idea, question)
    except Exception as e:
        reply = str(e)

    return jsonify({'status': 'success', 'reply': reply})


if __name__ == '__main__':
    # When running locally for development this block will start Flask's
    # development server. In production (Render/Gunicorn) the WSGI server
    # will import the `app` object directly. Read PORT from env so Render
    # can bind the correct port.
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)