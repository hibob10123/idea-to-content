document.addEventListener('DOMContentLoaded', () => {
  // Pages
  const pages = Array.from(document.querySelectorAll('.page'));
  const showPage = (name) => {
    pages.forEach(p => {
      if (p.dataset.page === name) {
        p.classList.add('page-active');
        requestAnimationFrame(()=> p.classList.add('fade-in'));
      } else {
        p.classList.remove('page-active', 'fade-in');
      }
    });
    window.scrollTo({top:0,behavior:'smooth'});
  };

  // Elements
  const descEl = document.getElementById('business-description');
  const formatEl = document.getElementById('video-format');
  const toneEl = document.getElementById('tone');
  const toIdeasBtn = document.getElementById('to-ideas');
  const ideasGrid = document.getElementById('ideas-grid');
  const detailTitle = document.getElementById('detail-title');
  const detailBody = document.getElementById('detail-body');
  const backToHome = document.getElementById('back-to-home');
  const backToIdeas = document.getElementById('back-to-ideas');

  // nav buttons
  document.querySelectorAll('[data-nav]').forEach(btn => btn.addEventListener('click', ()=> showPage(btn.dataset.nav)));

  backToHome && backToHome.addEventListener('click', ()=> showPage('home'));
  backToIdeas && backToIdeas.addEventListener('click', ()=> showPage('ideas'));

  // budget
  function getBudget(){
    const el = document.querySelector('input[name="budget"]:checked');
    return el ? el.value : 'free';
  }

  // Spinner / loading helper
  function setLoading(on, target){
    if(on){
      target.innerHTML = '<div class="muted">Generating ideas…</div>';
    }
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

  function buildPlaceholderIdeas(description, format, tone, budget){
    const base = description ? description.split('.')[0] : 'Your business';
    return [1,2,3,4].map(n => {
      const kind = ['Quick tip','Customer story','Before & after','How-to'][n-1];
      return {
        id: 'ph-'+n,
        title: `${base} — ${kind}`,
        format: format === 'youtube-long' ? 'YouTube (long)' : (format === 'youtube' ? 'YouTube Short' : 'Reel/TikTok'),
        tone,
        duration: format === 'youtube-long' ? `${2+n} min` : (format === 'youtube' ? '0:15' : '0:30'),
        caption: `${kind} to boost engagement #${n}`,
        script: `${n}. Hook (2-4s): Short surprising fact about ${base}\nShot 1: Close-up — 3s\nShot 2: Demo — 8s\nShot 3: CTA — 3s\nNotes: Add captions, natural light.`,
        scriptFull: `HOOK:\nShort surprising fact about ${base}\n\nSCRIPT:\n${n}. Shot 1: ...` ,
        apps: budget === 'free' ? ['CapCut','InShot','Canva'] : ['Premiere Pro','Final Cut Pro','DaVinci Resolve']
      };
    });
  }

  function mapBackendIdea(raw, budget){
    return {
      id: raw.id || raw.title,
      title: raw.title || raw.headline || 'Untitled idea',
      format: raw.format || 'Reel',
      tone: raw.tone || 'neutral',
      duration: raw.duration || '0:30',
      caption: raw.caption || raw.hook || '',
      script: raw.script || raw.body || '',
      scriptFull: raw.scriptFull || raw.script || '',
      apps: raw.apps || (budget === 'free' ? ['CapCut','Canva'] : ['Premiere Pro','Resolve'])
    };
  }

  function makeIdeaCard(idea){
    const el = document.createElement('article');
    el.className = 'idea-card fade-in';
    el.innerHTML = `
      <div class="idea-header">
        <div>
          <div class="idea-title">${escapeHtml(idea.title)}</div>
          <div class="idea-meta">${escapeHtml(idea.format)} • ${escapeHtml(idea.tone)}</div>
        </div>
        <div class="pill">${escapeHtml(idea.duration)}</div>
      </div>
      <div class="idea-body">
        <div class="muted"><strong>Hook:</strong> ${escapeHtml(idea.caption)}</div>
        <div style="margin-top:8px"><strong>Preview:</strong>
          <div class="muted" style="margin-top:6px;white-space:pre-wrap">${escapeHtml(idea.script.split('\n').slice(0,4).join('\n'))}…</div>
        </div>
        <div class="actions">
          <button class="copy-btn" data-copy>Copy script</button>
        </div>
        <div style="margin-top:10px;color:var(--muted)"><strong>Apps:</strong> ${escapeHtml((idea.apps||[]).join(', '))}</div>
      </div>`;

    el.addEventListener('click', (e)=>{
      // avoid card click when interacting with buttons
      if(e.target.closest('button')) return;
      showDetail(idea);
    });

    el.querySelectorAll('[data-copy]').forEach(btn => {
      btn.addEventListener('click', (ev)=>{
        ev.stopPropagation();
        copyToClipboard(idea.scriptFull || idea.script || idea.caption);
        btn.textContent = 'Copied';
        setTimeout(()=> btn.textContent = 'Copy script', 1200);
      });
    });

    return el;
  }

  function renderIdeas(list){
    ideasGrid.innerHTML = '';
    list.forEach(i => ideasGrid.appendChild(makeIdeaCard(i)));
    showPage('ideas');
  }

  async function generateIdeas(){
    const description = descEl.value.trim();
    const format = formatEl.value;
    const tone = toneEl.value;
    const budget = getBudget();

    if(!description){
      alert('Please enter a short description of your business to get tailored ideas.');
      return;
    }

    ideasGrid.innerHTML = '<div class="muted">Generating ideas…</div>';

    // Try backend first
    try{
      const resp = await fetch('/idea-to-content', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({description})
      });
      if(resp.ok){
        const data = await resp.json();
        if(data && data.ideas){
          const list = data.ideas.map(raw => mapBackendIdea(raw, budget));
          renderIdeas(list);
          return;
        }
      }
    }catch(err){
      console.debug('Backend not available—using local placeholders', err);
    }

    // fallback local generation
    const fallback = buildPlaceholderIdeas(description, format, tone, budget);
    renderIdeas(fallback);
  }

  function showDetail(idea){
    detailTitle.textContent = idea.title;
    detailBody.innerHTML = '';

    const steps = [];
    steps.push({title:'Hook',body:`${idea.caption || 'Short one-line hook to grab attention.'}`});
    steps.push({title:'Shot list',body: (idea.script || '').split('\n').slice(0,6).join('\n') || '3 shots: intro, demo, CTA.'});
    steps.push({title:'Script',body: idea.scriptFull || idea.script || 'Write a short 20-40s script with clear CTA.'});
    steps.push({title:'Editing & Apps',body: `Recommended apps: ${idea.apps && idea.apps.join(', ')}`});
    steps.push({title:'Distribution',body: 'Short caption + hashtags; post within first 60 minutes of scheduled time.'});

    steps.forEach(s=>{
      const el = document.createElement('div');
      el.className = 'detail-step fade-in';
      el.innerHTML = `<h4>${escapeHtml(s.title)}</h4><div class="muted-2" style="white-space:pre-wrap">${escapeHtml(s.body)}</div>`;
      detailBody.appendChild(el);
    });

    showPage('detail');
  }

  // event hooks
  toIdeasBtn.addEventListener('click', ()=>{
    toIdeasBtn.disabled = true; toIdeasBtn.textContent = 'Working...';
    generateIdeas().finally(()=>{toIdeasBtn.disabled = false; toIdeasBtn.textContent = 'See ideas'});
  });

  // initial page
  showPage('home');
});
