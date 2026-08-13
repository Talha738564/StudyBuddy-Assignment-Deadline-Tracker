document.addEventListener('DOMContentLoaded', () => {
    // Colors and subject tag assignment
    const TAG_COLORS = ['#5B4FE9', '#FF6B4A', '#2FD675', '#FFB020', '#3EC6E0', '#E84393'];
    const subjectColorMap = {};

    function getSubjectColor(subject) {
        const normalized = subject.toLowerCase().trim();
        if (!subjectColorMap[normalized]) {
            const index = Object.keys(subjectColorMap).length % TAG_COLORS.length;
            subjectColorMap[normalized] = TAG_COLORS[index];
        }
        return subjectColorMap[normalized];
    }

    // Determine Urgency Details (Ring Color & Shadow Class)
    function getUrgencyConfig(item) {
        if (item.is_overdue || item.days_left <= 2) {
            return { color: 'var(--signal-coral)', shadowClass: 'tier-urgent' };
        } else if (item.days_left <= 7) {
            return { color: 'var(--signal-amber)', shadowClass: 'tier-soon' };
        } else {
            return { color: 'var(--signal-mint)', shadowClass: 'tier-normal' };
        }
    }

    // Create the signature momentum ring element
    function createMomentumRing(progress, color) {
        return `
            <div class="momentum-ring" style="background: conic-gradient(${color} ${progress}%, #eee 0);">
                <span>${progress}%</span>
            </div>
        `;
    }

    // Build Assignment Card HTML
    function buildCardHtml(item, showActions = false) {
        const uc = getUrgencyConfig(item);
        const tagColor = getSubjectColor(item.subject);
        const deadlineText = item.is_overdue ? 'Overdue!' : `Due in ${item.days_left} days`;

        const actionsHtml = showActions ? `
            <div class="actions">
                <button class="btn-del" onclick="deleteAssignment('${item.subject}', '${item.title}')">Delete</button>
                <button class="btn-mark" onclick="quickMarkDone('${item.subject}', '${item.title}')">Mark Done</button>
            </div>
        ` : '';

        return `
            <div class="assignment-card ${uc.shadowClass}">
                ${createMomentumRing(item.progress, uc.color)}
                <div class="card-details">
                    <h3>${item.title}</h3>
                    <div>
                        <span class="subject-tag" style="background-color: ${tagColor}">${item.subject}</span>
                        <span style="font-size: 0.85rem; color: #666;">${deadlineText} • Prio: ${item.priority_weight}</span>
                    </div>
                </div>
                ${actionsHtml}
            </div>
        `;
    }

    // ---- API & Rendering Methods ----

    async function fetchDashboard() {
        // Statistics
        const statsRes = await fetch('/api/statistics');
        const stats = await statsRes.json();
        
        const dashboardHtml = `
            <h1 class="section-header">Dashboard</h1>
            <div class="dashboard-grid">
                <div class="stat-card"><h3>Total Tasks</h3><div class="value">${stats.total}</div></div>
                <div class="stat-card"><h3>Completed</h3><div class="value">${stats.completed}</div></div>
                <div class="stat-card"><h3>Pending</h3><div class="value">${stats.pending}</div></div>
                <div class="stat-card"><h3>Avg Days to Done</h3><div class="value">${stats.avg_completion_time_days.toFixed(1)}</div></div>
            </div>
            <h2 class="section-header">Today's Focus (Top 5)</h2>
            <div id="focus-list" class="cards-list">Loading...</div>
            <h2 class="section-header" style="margin-top: 2rem;">Reminders (Due Soon)</h2>
            <div id="reminders-list" class="cards-list">Loading...</div>
        `;
        document.getElementById('app-content').innerHTML = dashboardHtml;

        // Fetch Focus & Reminders concurrently
        const [focusRes, remRes] = await Promise.all([ fetch('/api/focus'), fetch('/api/reminders?days=2') ]);
        const focusItems = await focusRes.json();
        const remItems = await remRes.json();

        document.getElementById('focus-list').innerHTML = focusItems.length ? focusItems.map(i => buildCardHtml(i)).join('') : '<p>No items.</p>';
        document.getElementById('reminders-list').innerHTML = remItems.length ? remItems.map(i => buildCardHtml(i)).join('') : '<p>No items due soon.</p>';
    }

    async function fetchAllAssignments() {
        document.getElementById('app-content').innerHTML = `<h1 class="section-header">All Assignments</h1><div id="all-list" class="cards-list">Loading...</div>`;
        const res = await fetch('/api/assignments');
        const items = await res.json();
        document.getElementById('all-list').innerHTML = items.length ? items.map(i => buildCardHtml(i, true)).join('') : '<p>No assignments found.</p>';
    }

    async function fetchStatistics() {
        const res = await fetch('/api/statistics');
        const stats = await res.json();
        let ratesHtml = Object.entries(stats.completion_rates).map(([subj, rate]) => {
            return `<div style="margin-bottom: 1rem;">
                        <span style="font-weight:600">${subj}</span>
                        <div style="background: #eee; height: 12px; border-radius: 6px; overflow: hidden; margin-top: 5px;">
                            <div style="width: ${rate}%; height: 100%; background: var(--accent-indigo);"></div>
                        </div>
                    </div>`;
        }).join('');

        document.getElementById('app-content').innerHTML = `
            <h1 class="section-header">Subject Completion Rates</h1>
            <div style="background: #fff; padding: 2rem; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.03);">
                ${ratesHtml || '<p>No subject data yet.</p>'}
            </div>
        `;
    }

    // ---- Event Listeners & Interactions ----

    // Navigation View switching
    document.querySelectorAll('.nav-links li').forEach(el => {
        el.addEventListener('click', (e) => {
            document.querySelectorAll('.nav-links li').forEach(li => li.classList.remove('active'));
            e.target.classList.add('active');
            const view = e.target.dataset.view;
            if(view === 'dashboard') fetchDashboard();
            if(view === 'all-assignments') fetchAllAssignments();
            if(view === 'statistics') fetchStatistics();
        });
    });

    // Export Action
    document.getElementById('export-btn').addEventListener('click', () => {
        window.open('/api/export', '_blank');
    });

    // Slide-over Handlers
    const slideOver = document.getElementById('slide-over');
    const backdrop = document.getElementById('backdrop');
    
    document.getElementById('fab').addEventListener('click', () => {
        slideOver.classList.remove('hidden');
        backdrop.classList.remove('hidden');
        setTimeout(() => slideOver.style.transform = 'translateX(0)', 10);
    });

    function closeForm() {
        slideOver.style.transform = 'translateX(100%)';
        setTimeout(() => {
            slideOver.classList.add('hidden');
            backdrop.classList.add('hidden');
            document.getElementById('add-form').reset();
            document.getElementById('form-error').classList.add('hidden');
            document.getElementById('a_type').dispatchEvent(new Event('change'));
        }, 300);
    }
    
    document.getElementById('close-slide-over').addEventListener('click', closeForm);
    backdrop.addEventListener('click', closeForm);

    // Dynamic Form Fields based on Type
    document.getElementById('a_type').addEventListener('change', (e) => {
        document.querySelectorAll('.field-group').forEach(el => el.classList.add('hidden'));
        document.querySelector(`.${e.target.value}-fields`).classList.remove('hidden');
    });

    // Handle Form Submission
    document.getElementById('add-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
            type: document.getElementById('a_type').value,
            title: document.getElementById('title').value,
            subject: document.getElementById('subject').value,
            deadline: document.getElementById('deadline').value,
            priority_weight: parseInt(document.getElementById('priority').value),
            estimated_hours: parseInt(document.getElementById('hours').value),
            progress: parseInt(document.getElementById('progress').value),
            submission_type: document.getElementById('submission_type').value,
            milestones: document.getElementById('milestones').value,
            team_members: document.getElementById('team_members').value,
            important_topics: document.getElementById('topics').value
        };

        const response = await fetch('/api/assignments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        const errorEl = document.getElementById('form-error');
        
        if (!response.ok) {
            errorEl.textContent = result.error;
            errorEl.classList.remove('hidden');
        } else {
            closeForm();
            // Refresh current view
            const activeView = document.querySelector('.nav-links li.active').dataset.view;
            if(activeView === 'dashboard') fetchDashboard();
            if(activeView === 'all-assignments') fetchAllAssignments();
        }
    });

    // Global Functions for inline actions
    window.deleteAssignment = async (subject, title) => {
        if (!confirm(`Delete '${title}'?`)) return;
        await fetch(`/api/assignments/${subject}/${title}`, { method: 'DELETE' });
        fetchAllAssignments();
    };

    window.quickMarkDone = async (subject, title) => {
        await fetch(`/api/assignments/${subject}/${title}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ progress: 100 })
        });
        fetchAllAssignments();
    };

    // Initialization
    fetchDashboard();
});