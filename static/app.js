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

    function getSubjectTextColor(backgroundColor) {
        const red = parseInt(backgroundColor.slice(1, 3), 16);
        const green = parseInt(backgroundColor.slice(3, 5), 16);
        const blue = parseInt(backgroundColor.slice(5, 7), 16);
        const luminance = (red * 299 + green * 587 + blue * 114) / 1000;
        return luminance > 155 ? '#14162B' : '#FFFFFF';
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
            <div class="momentum-ring" style="background: conic-gradient(${color} ${progress}%, rgba(255, 255, 255, 0.16) 0);">
                <span>${progress}%</span>
            </div>
        `;
    }

  // Build Assignment Card HTML with extra specific details
    function buildCardHtml(item, showActions = false) {
        const uc = getUrgencyConfig(item);
        const tagColor = getSubjectColor(item.subject);
        const deadlineText = item.is_overdue ? 'Overdue!' : `Due in ${item.days_left} days`;

        // Gather assignment type specific details
        let extraFieldsHtml = '';
        const pills = [];

        if (item.submission_type && item.submission_type.trim()) {
            pills.push(`<span><strong>Submission:</strong> ${item.submission_type}</span>`);
        }

        if (item.milestones) {
            const ms = Array.isArray(item.milestones) ? item.milestones.join(', ') : item.milestones;
            if (ms.trim()) pills.push(`<span><strong>Milestones:</strong> ${ms}</span>`);
        }

        if (item.team_members) {
            const tm = Array.isArray(item.team_members) ? item.team_members.join(', ') : item.team_members;
            if (tm.trim()) pills.push(`<span><strong>Team:</strong> ${tm}</span>`);
        }

        if (item.important_topics) {
            const top = Array.isArray(item.important_topics) ? item.important_topics.join(', ') : item.important_topics;
            if (top.trim()) pills.push(`<span><strong>Important Topics:</strong> ${top}</span>`);
        }

        if (pills.length > 0) {
            extraFieldsHtml = `
                <div class="extra-fields-container">
                    ${pills.map(p => `<div class="extra-pill">${p}</div>`).join('')}
                </div>
            `;
        }

        const actionsHtml = showActions ? `
            <div class="actions">
                <button class="btn-mark" onclick="quickMarkDone('${item.subject}', '${item.title}')">✓ Mark Done</button>
                <button class="btn-del" onclick="deleteAssignment('${item.subject}', '${item.title}')">Delete</button>
            </div>
        ` : '';

        return `
            <div class="assignment-card ${uc.shadowClass}">
                ${createMomentumRing(item.progress, uc.color)}
                <div class="card-details">
                    <h3>${item.title}</h3>
                    <div>
                        <span class="subject-tag" style="background-color: ${tagColor}; color: ${getSubjectTextColor(tagColor)}">${item.subject}</span>
                        <span style="font-size: 0.85rem; color: #666;">${deadlineText} • Prio: ${item.priority_weight}</span>
                    </div>
                    ${extraFieldsHtml}
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
    
    // Your chosen minimalist data grid style:
    let ratesHtml = Object.entries(stats.completion_rates).map(([subj, rate]) => {
        const cleanRate = Math.round(rate);
        const isDone = cleanRate === 100;
        const color = isDone ? 'var(--signal-mint)' : 'var(--text-light)';
        const glow = isDone ? 'text-shadow: 0 0 10px rgba(47, 214, 117, 0.4);' : '';

        return `
            <div class="completion-rate-row">
                <span class="completion-rate-subject">${subj}</span>
                <span class="completion-rate-value" style="color: ${color}; ${glow}">
                    ${cleanRate}%
                </span>
            </div>
        `;
    }).join('');

    // Render the dashboard stats and the new minimalist list
    document.getElementById('app-content').innerHTML = `
        <h1 class="section-header">Statistics Overview</h1>
        
        <div class="dashboard-grid" style="margin-bottom: 2rem;">
            <div class="stat-card"><h3>Total Tasks</h3><div class="value">${stats.total}</div></div>
            <div class="stat-card"><h3>Completed</h3><div class="value">${stats.completed}</div></div>
            <div class="stat-card"><h3>Pending</h3><div class="value">${stats.pending}</div></div>
            <div class="stat-card"><h3>Avg Days to Done</h3><div class="value">${stats.avg_completion_time_days.toFixed(1)}</div></div>
        </div>

        <h2 class="section-header">Subject Completion Rates</h2>
        <div class="completion-rates-card">
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

 // Export Action (with Cache-Busting)
    document.getElementById('export-btn').addEventListener('click', () => {
        const timestamp = new Date().getTime(); // Generates a unique number right now
        window.open(`/api/export?t=${timestamp}`, '_blank');
    });

    document.querySelector('[data-logout-link]').addEventListener('click', (event) => {
        if (!window.confirm('Log out of StudyBuddy?')) {
            event.preventDefault();
            return;
        }
        event.preventDefault();
        const logoutLink = event.currentTarget;
        logoutLink.classList.add('is-logging-out');
        window.setTimeout(() => { window.location.href = logoutLink.href; }, 260);
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