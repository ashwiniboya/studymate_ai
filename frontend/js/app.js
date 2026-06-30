const API_BASE = '/api';

const api = {
  async get(path) {
    const res = await fetch(`${API_BASE}${path}`);
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  },

  async post(path, body) {
    const res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  },

  async upload(path, formData) {
    const res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  },

  async delete(path) {
    const res = await fetch(`${API_BASE}${path}`, { method: 'DELETE' });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  },
};

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

function showLoading(element, text = 'Loading...') {
  element.innerHTML = `<div class="loading"><div class="spinner"></div>${text}</div>`;
}

function navigateTo(page) {
  document.querySelectorAll('.page-section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));

  const section = document.getElementById(`page-${page}`);
  if (section) section.classList.add('active');

  const link = document.querySelector(`[data-page="${page}"]`);
  if (link) link.classList.add('active');

  document.getElementById('sidebar').classList.remove('open');

  const loaders = {
    dashboard: loadDashboard,
    upload: loadUpload,
    chat: loadChat,
    notes: loadNotes,
    flashcards: loadFlashcards,
    quiz: loadQuiz,
    progress: loadProgress,
  };
  if (loaders[page]) loaders[page]();
}

async function loadDocuments() {
  try {
    return await api.get('/documents/');
  } catch {
    return [];
  }
}

function populateDocSelect(selectId, documents) {
  const select = document.getElementById(selectId);
  if (!select) return;
  select.innerHTML = '<option value="">Select a document...</option>';
  documents.forEach(doc => {
    const opt = document.createElement('option');
    opt.value = doc.id;
    opt.textContent = `${doc.title} (${doc.file_type.toUpperCase()})`;
    select.appendChild(opt);
  });
}

async function loadDashboard() {
  const statsEl = document.getElementById('dashboard-stats');
  const docsEl = document.getElementById('dashboard-docs');

  try {
    const [docs, progress] = await Promise.all([
      loadDocuments(),
      api.get('/progress/summary').catch(() => ({ data: {} })),
    ]);

    const summary = progress.data?.summary || {};
    statsEl.innerHTML = `
      <div class="stat-card"><div class="stat-value">${summary.total_documents || docs.length}</div><div class="stat-label">Documents</div></div>
      <div class="stat-card"><div class="stat-value">${summary.total_notes || 0}</div><div class="stat-label">Notes</div></div>
      <div class="stat-card"><div class="stat-value">${summary.total_flashcards || 0}</div><div class="stat-label">Flashcards</div></div>
      <div class="stat-card"><div class="stat-value">${summary.total_quizzes || 0}</div><div class="stat-label">Quizzes</div></div>
    `;

    if (docs.length === 0) {
      docsEl.innerHTML = '<div class="empty-state"><div class="empty-icon">📄</div><p>No documents uploaded yet. Upload a PDF to get started!</p></div>';
    } else {
      docsEl.innerHTML = docs.slice(0, 5).map(doc => `
        <div class="doc-item">
          <div class="doc-info">
            <h4>${doc.title}</h4>
            <p>${doc.filename} &middot; ${doc.chunk_count} chunks</p>
          </div>
          <span class="doc-badge ${doc.file_type}">${doc.file_type}</span>
        </div>
      `).join('');
    }
  } catch (e) {
    showToast('Failed to load dashboard', 'error');
  }
}

function loadUpload() {
  const zone = document.getElementById('upload-zone');
  const input = document.getElementById('file-input');
  const list = document.getElementById('upload-list');

  zone.onclick = () => input.click();
  zone.ondragover = (e) => { e.preventDefault(); zone.classList.add('dragover'); };
  zone.ondragleave = () => zone.classList.remove('dragover');
  zone.ondrop = (e) => {
    e.preventDefault();
    zone.classList.remove('dragover');
    if (e.dataTransfer.files.length) handleUpload(e.dataTransfer.files[0]);
  };
  input.onchange = () => { if (input.files.length) handleUpload(input.files[0]); };

  loadDocuments().then(docs => {
    if (docs.length === 0) {
      list.innerHTML = '<div class="empty-state"><p>No documents yet</p></div>';
      return;
    }
    list.innerHTML = docs.map(doc => `
      <div class="doc-item">
        <div class="doc-info">
          <h4>${doc.title}</h4>
          <p>${doc.filename} &middot; ${new Date(doc.created_at).toLocaleDateString()}</p>
        </div>
        <div>
          <span class="doc-badge ${doc.file_type}">${doc.file_type}</span>
          <button class="btn btn-danger" style="margin-left:0.5rem;padding:0.25rem 0.5rem;font-size:0.75rem" onclick="deleteDoc(${doc.id})">Delete</button>
        </div>
      </div>
    `).join('');
  });
}

async function handleUpload(file) {
  const formData = new FormData();
  formData.append('file', file);
  showToast(`Uploading ${file.name}...`, 'info');

  try {
    const result = await api.upload('/documents/upload', formData);
    if (result.status === 'success') {
      showToast(`Uploaded: ${file.name}`, 'success');
      loadUpload();
    } else {
      showToast(result.message || 'Upload failed', 'error');
    }
  } catch {
    showToast('Upload failed', 'error');
  }
}

async function deleteDoc(id) {
  if (!confirm('Delete this document and all associated data?')) return;
  try {
    await api.delete(`/documents/${id}`);
    showToast('Document deleted', 'success');
    loadUpload();
  } catch {
    showToast('Delete failed', 'error');
  }
}

let chatHistory = [];

function loadChat() {
  loadDocuments().then(docs => populateDocSelect('chat-doc-select', docs));
  const messages = document.getElementById('chat-messages');
  if (chatHistory.length === 0) {
    messages.innerHTML = '<div class="chat-message assistant">Hello! I\'m StudyMate AI. Upload a document and ask me questions about your study materials.</div>';
  }
}

async function sendChat() {
  const input = document.getElementById('chat-input');
  const message = input.value.trim();
  if (!message) return;

  const docId = document.getElementById('chat-doc-select').value;
  const messages = document.getElementById('chat-messages');

  messages.innerHTML += `<div class="chat-message user">${escapeHtml(message)}</div>`;
  input.value = '';
  messages.scrollTop = messages.scrollHeight;

  const loading = document.createElement('div');
  loading.className = 'chat-message assistant';
  loading.innerHTML = '<div class="spinner" style="display:inline-block;width:16px;height:16px;margin-right:8px"></div>Thinking...';
  messages.appendChild(loading);
  messages.scrollTop = messages.scrollHeight;

  try {
    const result = await api.post('/chat/', {
      message,
      document_id: docId ? parseInt(docId) : null,
    });
    loading.remove();
    messages.innerHTML += `<div class="chat-message assistant">${escapeHtml(result.response)}</div>`;
    chatHistory.push({ role: 'user', content: message }, { role: 'assistant', content: result.response });
  } catch {
    loading.remove();
    messages.innerHTML += '<div class="chat-message assistant">Sorry, I encountered an error. Please try again.</div>';
  }
  messages.scrollTop = messages.scrollHeight;
}

function loadNotes() {
  loadDocuments().then(docs => populateDocSelect('notes-doc-select', docs));
  api.get('/notes/').then(notes => {
    const list = document.getElementById('notes-list');
    if (notes.length === 0) {
      list.innerHTML = '<div class="empty-state"><div class="empty-icon">📝</div><p>No notes yet. Generate notes from a document!</p></div>';
      return;
    }
    list.innerHTML = notes.map(note => `
      <div class="card" style="cursor:pointer" onclick="viewNote(${note.id})">
        <div class="card-header">
          <span class="card-title">${escapeHtml(note.title)}</span>
          <small style="color:var(--text-muted)">${new Date(note.created_at).toLocaleDateString()}</small>
        </div>
        <p style="color:var(--text-muted);font-size:0.85rem">${escapeHtml(note.content.substring(0, 150))}...</p>
      </div>
    `).join('');
  }).catch(() => {});
}

async function generateNotes() {
  const docId = document.getElementById('notes-doc-select').value;
  if (!docId) { showToast('Select a document first', 'error'); return; }

  const focus = document.getElementById('notes-focus').value;
  const btn = document.getElementById('generate-notes-btn');
  btn.disabled = true;
  btn.textContent = 'Generating...';

  try {
    const result = await api.post('/notes/generate', {
      document_id: parseInt(docId),
      focus_area: focus,
    });
    if (result.status === 'success') {
      showToast('Notes generated!', 'success');
      loadNotes();
    } else {
      showToast(result.message || 'Generation failed', 'error');
    }
  } catch {
    showToast('Failed to generate notes', 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Generate Notes';
  }
}

async function viewNote(id) {
  try {
    const note = await api.get(`/notes/${id}`);
    const viewer = document.getElementById('note-viewer');
    viewer.style.display = 'block';
    viewer.innerHTML = `
      <div class="card">
        <div class="card-header">
          <span class="card-title">${escapeHtml(note.title)}</span>
          <button class="btn btn-secondary" onclick="document.getElementById('note-viewer').style.display='none'">Close</button>
        </div>
        <div class="note-content">${formatMarkdown(note.content)}</div>
      </div>
    `;
  } catch {
    showToast('Failed to load note', 'error');
  }
}

let flashcards = [];
let currentCardIndex = 0;

function loadFlashcards() {
  loadDocuments().then(docs => populateDocSelect('flashcards-doc-select', docs));
  api.get('/flashcards/').then(cards => {
    flashcards = cards;
    currentCardIndex = 0;
    renderFlashcard();
    document.getElementById('flashcard-counter').textContent =
      cards.length > 0 ? `Card ${currentCardIndex + 1} of ${cards.length}` : 'No flashcards';
  }).catch(() => {});
}

function renderFlashcard() {
  const container = document.getElementById('flashcard-display');
  if (flashcards.length === 0) {
    container.innerHTML = '<div class="empty-state"><div class="empty-icon">🃏</div><p>No flashcards yet. Generate some from a document!</p></div>';
    return;
  }

  const card = flashcards[currentCardIndex];
  container.innerHTML = `
    <div class="flashcard-container" onclick="flipCard()">
      <div class="flashcard" id="flashcard">
        <div class="flashcard-face flashcard-front">${escapeHtml(card.front)}</div>
        <div class="flashcard-face flashcard-back">${escapeHtml(card.back)}</div>
      </div>
    </div>
    <div style="text-align:center;margin-top:1rem">
      <button class="btn btn-success" onclick="reviewCard(true)">✓ Got it</button>
      <button class="btn btn-danger" onclick="reviewCard(false)" style="margin-left:0.5rem">✗ Missed</button>
      <button class="btn btn-secondary" onclick="nextCard()" style="margin-left:0.5rem">Next →</button>
    </div>
  `;
  document.getElementById('flashcard-counter').textContent = `Card ${currentCardIndex + 1} of ${flashcards.length}`;
}

function flipCard() {
  document.getElementById('flashcard')?.classList.toggle('flipped');
}

function nextCard() {
  currentCardIndex = (currentCardIndex + 1) % flashcards.length;
  renderFlashcard();
}

async function reviewCard(correct) {
  const card = flashcards[currentCardIndex];
  try {
    await api.post(`/flashcards/${card.id}/review`, { correct });
    showToast(correct ? 'Great job!' : 'Keep practicing!', correct ? 'success' : 'info');
    nextCard();
  } catch {
    showToast('Failed to record review', 'error');
  }
}

async function generateFlashcards() {
  const docId = document.getElementById('flashcards-doc-select').value;
  if (!docId) { showToast('Select a document first', 'error'); return; }

  const num = parseInt(document.getElementById('flashcards-count').value) || 10;
  const btn = document.getElementById('generate-flashcards-btn');
  btn.disabled = true;
  btn.textContent = 'Generating...';

  try {
    const result = await api.post('/flashcards/generate', {
      document_id: parseInt(docId),
      num_cards: num,
    });
    if (result.status === 'success') {
      showToast(`Generated ${result.data?.count || num} flashcards!`, 'success');
      loadFlashcards();
    } else {
      showToast(result.message || 'Generation failed', 'error');
    }
  } catch {
    showToast('Failed to generate flashcards', 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Generate Flashcards';
  }
}

let currentQuiz = null;
let quizAnswers = {};

function loadQuiz() {
  loadDocuments().then(docs => populateDocSelect('quiz-doc-select', docs));
  api.get('/quiz/').then(quizzes => {
    const list = document.getElementById('quiz-list');
    if (quizzes.length === 0) {
      list.innerHTML = '<div class="empty-state"><div class="empty-icon">❓</div><p>No quizzes yet. Generate one from a document!</p></div>';
      return;
    }
    list.innerHTML = quizzes.map(q => `
      <div class="doc-item" style="cursor:pointer" onclick="startQuiz(${q.id})">
        <div class="doc-info">
          <h4>${escapeHtml(q.title)}</h4>
          <p>${q.questions.length} questions</p>
        </div>
        <button class="btn btn-primary">Start</button>
      </div>
    `).join('');
  }).catch(() => {});
}

async function generateQuiz() {
  const docId = document.getElementById('quiz-doc-select').value;
  if (!docId) { showToast('Select a document first', 'error'); return; }

  const btn = document.getElementById('generate-quiz-btn');
  btn.disabled = true;
  btn.textContent = 'Generating...';

  try {
    const result = await api.post('/quiz/generate', {
      document_id: parseInt(docId),
      num_questions: parseInt(document.getElementById('quiz-count').value) || 5,
      difficulty: document.getElementById('quiz-difficulty').value,
    });
    if (result.status === 'success') {
      showToast('Quiz generated!', 'success');
      loadQuiz();
    } else {
      showToast(result.message || 'Generation failed', 'error');
    }
  } catch {
    showToast('Failed to generate quiz', 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Generate Quiz';
  }
}

async function startQuiz(id) {
  try {
    currentQuiz = await api.get(`/quiz/${id}`);
    quizAnswers = {};
    const area = document.getElementById('quiz-area');
    area.style.display = 'block';
    area.innerHTML = `
      <div class="card">
        <div class="card-header">
          <span class="card-title">${escapeHtml(currentQuiz.title)}</span>
          <button class="btn btn-secondary" onclick="document.getElementById('quiz-area').style.display='none'">Close</button>
        </div>
        ${currentQuiz.questions.map((q, i) => `
          <div class="quiz-question" data-qid="${q.id}">
            <h4>${i + 1}. ${escapeHtml(q.question)}</h4>
            ${q.options.map(opt => `
              <button class="quiz-option" onclick="selectAnswer(${q.id}, '${escapeHtml(opt).replace(/'/g, "\\'")}', this)">${escapeHtml(opt)}</button>
            `).join('')}
          </div>
        `).join('')}
        <button class="btn btn-primary" onclick="submitQuiz(${currentQuiz.id})">Submit Answers</button>
      </div>
    `;
  } catch {
    showToast('Failed to load quiz', 'error');
  }
}

function selectAnswer(qId, answer, el) {
  quizAnswers[qId] = answer;
  el.parentElement.querySelectorAll('.quiz-option').forEach(o => o.classList.remove('selected'));
  el.classList.add('selected');
}

async function submitQuiz(id) {
  try {
    const result = await api.post(`/quiz/${id}/submit`, { answers: quizAnswers });
    showToast(result.message, result.data?.score >= 70 ? 'success' : 'info');

    if (result.data?.results) {
      result.data.results.forEach(r => {
        const qEl = document.querySelector(`[data-qid="${r.question_id}"]`);
        if (!qEl) return;
        qEl.querySelectorAll('.quiz-option').forEach(opt => {
          if (opt.textContent.trim() === r.correct_answer) opt.classList.add('correct');
          else if (opt.classList.contains('selected') && !r.correct) opt.classList.add('incorrect');
        });
      });
    }
  } catch {
    showToast('Failed to submit quiz', 'error');
  }
}

async function loadProgress() {
  const summaryEl = document.getElementById('progress-summary');
  const analysisEl = document.getElementById('progress-analysis');
  const recordsEl = document.getElementById('progress-records');

  try {
    const [progress, records] = await Promise.all([
      api.get('/progress/summary'),
      api.get('/progress/records'),
    ]);

    const s = progress.data?.summary || {};
    summaryEl.innerHTML = `
      <div class="grid grid-4">
        <div class="stat-card"><div class="stat-value">${s.total_documents || 0}</div><div class="stat-label">Documents</div></div>
        <div class="stat-card"><div class="stat-value">${s.total_activities || 0}</div><div class="stat-label">Activities</div></div>
        <div class="stat-card"><div class="stat-value">${s.average_score || 0}%</div><div class="stat-label">Avg Score</div></div>
        <div class="stat-card"><div class="stat-value">${s.total_flashcards || 0}</div><div class="stat-label">Flashcards</div></div>
      </div>
    `;

    if (progress.data?.analysis) {
      analysisEl.innerHTML = `
        <div class="card">
          <div class="card-header"><span class="card-title">AI Progress Analysis</span></div>
          <div class="note-content">${formatMarkdown(progress.data.analysis)}</div>
        </div>
      `;
    }

    if (records.length === 0) {
      recordsEl.innerHTML = '<div class="empty-state"><p>No activity recorded yet</p></div>';
    } else {
      recordsEl.innerHTML = records.slice(0, 20).map(r => `
        <div class="doc-item">
          <div class="doc-info">
            <h4>${r.activity_type.replace(/_/g, ' ')}</h4>
            <p>${r.details || 'No details'}</p>
          </div>
          <div>
            ${r.score > 0 ? `<strong>${r.score}%</strong> &middot; ` : ''}
            <small style="color:var(--text-muted)">${new Date(r.created_at).toLocaleString()}</small>
          </div>
        </div>
      `).join('');
    }
  } catch {
    showToast('Failed to load progress', 'error');
  }
}

async function createStudyPlan() {
  const docId = document.getElementById('plan-doc-select')?.value;
  if (!docId) {
    loadDocuments().then(docs => {
      populateDocSelect('plan-doc-select', docs);
    });
    showToast('Select a document for the study plan', 'error');
    return;
  }

  const goals = document.getElementById('plan-goals')?.value || '';
  showToast('Creating study plan...', 'info');

  try {
    const result = await api.post('/progress/plan', {
      document_id: parseInt(docId),
      goals,
    });
    if (result.status === 'success' && result.data?.plan_content) {
      document.getElementById('progress-analysis').innerHTML = `
        <div class="card">
          <div class="card-header"><span class="card-title">Study Plan</span></div>
          <div class="note-content">${formatMarkdown(result.data.plan_content)}</div>
        </div>
      `;
      showToast('Study plan created!', 'success');
    } else {
      showToast(result.message || 'Failed to create plan', 'error');
    }
  } catch {
    showToast('Failed to create study plan', 'error');
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatMarkdown(text) {
  return escapeHtml(text)
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n/g, '<br>');
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      navigateTo(link.dataset.page);
    });
  });

  document.getElementById('menu-toggle')?.addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('open');
  });

  document.getElementById('chat-input')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendChat();
  });

  loadDocuments().then(docs => populateDocSelect('plan-doc-select', docs));
  navigateTo('dashboard');
});
