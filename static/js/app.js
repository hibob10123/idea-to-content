document.addEventListener('DOMContentLoaded', () => {
  const generateBtn = document.getElementById('generate-btn');
  const descEl = document.getElementById('business-description');
  const resultsEl = document.getElementById('results');

  function showPlaceholder() {
    resultsEl.classList.add('empty');
    resultsEl.innerHTML = `
      <div class="placeholder">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M12 2v6" stroke-linecap="round" stroke-linejoin="round"></path>
          <path d="M5 12h14" stroke-linecap="round" stroke-linejoin="round"></path>
          <path d="M12 22v-6" stroke-linecap="round" stroke-linejoin="round"></path>
        </svg>
        <p class="muted">Your ideas will appear here</p>
      </div>`;
  }

  function makeIdeaCard(idea) {
    const div = document.createElement('div');
    div.className = 'idea-card';

    div.innerHTML = `
      <div class="idea-header">
        <div>
          <div class="idea-title">${escapeHtml(idea.title)}</div>
          <div class="idea-meta">${escapeHtml(idea.format)} • ${escapeHtml(idea.tone)}</div>
        </div>
        <div class="pill">${escapeHtml(idea.duration)}</div>
      </div>
      <div class="idea-body">
        <div class="muted"><strong>Hook / caption:</strong> ${escapeHtml(idea.caption)}</div>
        <div style="margin-top:8px"><strong>Shot list & script:</strong>
          <div class="muted" style="margin-top:6px;white-space:pre-wrap">${escapeHtml(idea.script)}</div>
        </div>
        <div class="actions">
          <button class="copy-btn" data-copy>Copy full script</button>
          <button class="copy-btn" data-copy-caption>Copy caption</button>
        </div>
        <div style="margin-top:10px;color:var(--muted)"><strong>Apps:</strong> ${escapeHtml(idea.apps.join(', '))}</div>
      </div>
    `;

    // attach copy handlers
    div.querySelectorAll('[data-copy],[data-copy-caption]').forEach(btn => {
      btn.addEventListener('click', () => {
        if (btn.hasAttribute('data-copy')) {
          copyToClipboard(idea.scriptFull || (idea.caption + '\n\n' + idea.script));
        } else {
          copyToClipboard(idea.caption);
        }
        btn.textContent = 'Copied';
        setTimeout(() => (btn.textContent = btn.hasAttribute('data-copy') ? 'Copy full script' : 'Copy caption'), 1200);
      });
    });

    return div;
  }

  function renderIdeas(ideas) {
    resultsEl.classList.remove('empty');
    resultsEl.innerHTML = '';
    ideas.forEach(i => resultsEl.appendChild(makeIdeaCard(i)));
  }

  function buildPlaceholderIdeas(description, format, tone) {
    // Lightweight deterministic placeholder generator for demo purposes
    const base = description ? description.split('.')[0] : 'Your business';
    return [1,2,3].map(n => {
      return {
        title: `${base} — ${['Quick tip','Customer story','Before & after'][n-1]}`,
        format: format === 'youtube-long' ? 'YouTube (long)' : (format === 'youtube' ? 'YouTube Short' : 'Reel/TikTok'),
        tone: tone,
        duration: format === 'youtube-long' ? '2-5 min' : (format === 'youtube' ? '0:15' : '0:30'),
        caption: `Quick ${tone} idea to boost engagement #${n}`,
        script: `${n}. Hook (2-4s): Grab attention with unexpected fact about ${base}\n`+
                `${n}. Shot 1: Close-up — 3s\n${n}. Shot 2: Demo — 6s\n${n}. Shot 3: CTA — 3s\n\nNotes: Keep it authentic, add captions, vertical crop.`,
        scriptFull: `HOOK:\nGrab attention with a short line about ${base}\n\nSCRIPT:\n${n}. Shot 1: ...` ,
        apps: n === 1 ? ['CapCut','InShot','Canva'] : (n===2 ? ['VN','Instagram Reels','Descript'] : ['LumaFusion','Premiere Rush','Spark Video'])
      };
    });
  }

  function escapeHtml(str){
    if(!str) return '';
    return String(str)
      .replace(/&/g,'&amp;')
      .replace(/</g,'&lt;')
      .replace(/>/g,'&gt;')
      .replace(/"/g,'&quot;')
      .replace(/'/g,'&#039;');
  }

  function copyToClipboard(text){
    if(!text) return;
    navigator.clipboard && navigator.clipboard.writeText(text).catch(()=>{
      const ta = document.createElement('textarea');
      ta.value = text; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); ta.remove();
    });
  }

  async function generate() {
    const description = descEl.value.trim();
    const format = document.getElementById('video-format').value;
    const tone = document.getElementById('tone').value;

    // show loading state
    resultsEl.classList.remove('empty');
    resultsEl.innerHTML = '<div class="muted">Generating ideas…</div>';

    // try contacting backend if available; otherwise fallback to local placeholders
    try {
      const resp = await fetch('/generate_content', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({description, format, tone})
      });
      if (resp.ok) {
        const data = await resp.json();
        if (data && data.ideas) {
          renderIdeas(data.ideas.map(mapBackendIdea));
          return;
        }
      }
    } catch (err) {
      // ignoring errors from backend in demo mode
      console.debug('Backend not available or returned error', err);
    }

    // fallback
    const ideas = buildPlaceholderIdeas(description, format, tone);
    renderIdeas(ideas);
  }

  function mapBackendIdea(raw){
    // adapt a simple backend idea shape to UI card
    return {
      title: raw.title || raw.headline || 'Untitled idea',
      format: raw.format || 'Reel',
      tone: raw.tone || 'neutral',
      duration: raw.duration || '0:30',
      caption: raw.caption || raw.hook || '',
      script: raw.script || raw.body || '',
      scriptFull: raw.scriptFull || raw.script || '',
      apps: raw.apps || ['CapCut','Canva']
    };
  }

  // wire UI
  generateBtn.addEventListener('click', () => {
    generateBtn.disabled = true;
    generateBtn.textContent = 'Working...';
    generate().finally(()=>{generateBtn.disabled=false;generateBtn.textContent='Generate ideas'});
  });

  // show initial placeholder
  showPlaceholder();
});
