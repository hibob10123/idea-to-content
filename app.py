from flask import Flask, jsonify, request, render_template, escape

app = Flask(__name__)


def generate_marketing_ideas(business_description, max_ideas=6):
    """Generate a small list of content-marketing ideas from a business description.

    This is a simple, deterministic generator intended as a placeholder so the
    app behaves like a chatbot. It can be swapped for an LLM call later.

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


@app.route('/idea-to-content', methods=['POST'])
def idea_to_content():
    """Endpoint that behaves like a small chatbot: accepts a business idea and
    returns content-marketing ideas."""
    data = request.get_json() or {}
    # Accept either 'idea' or 'description' or 'text'
    business_description = data.get('idea') or data.get('description') or data.get('text') or ''

    if not business_description.strip():
        return jsonify({'status': 'error', 'message': 'Please provide a business idea/description.'}), 400

    # Generate ideas
    ideas = generate_marketing_ideas(business_description)

    return jsonify({'status': 'success', 'input': business_description, 'ideas': ideas})


if __name__ == '__main__':
    app.run(debug=True)