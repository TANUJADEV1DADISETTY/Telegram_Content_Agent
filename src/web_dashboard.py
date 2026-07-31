DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Content Agent - Live Operations Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@500;600;700;800&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #090d16;
            --card-bg: rgba(21, 29, 46, 0.7);
            --card-border: rgba(255, 255, 255, 0.08);
            --accent-blue: #3b82f6;
            --accent-purple: #8b5cf6;
            --accent-emerald: #10b981;
            --accent-amber: #f59e0b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-main);
            min-height: 100vh;
            background-image: 
                radial-gradient(circle at 15% 15%, rgba(59, 130, 246, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 85% 85%, rgba(139, 92, 246, 0.15) 0%, transparent 40%);
            padding: 2rem 1.5rem;
        }

        .container {
            max-width: 1280px;
            margin: 0 auto;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2.5rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--card-border);
        }

        .logo-group {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .logo-icon {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
        }

        h1 {
            font-family: 'Outfit', sans-serif;
            font-size: 1.75rem;
            font-weight: 700;
            background: linear-gradient(90deg, #ffffff, #cbd5e1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .subtitle {
            font-size: 0.875rem;
            color: var(--text-muted);
        }

        .status-badge {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 0.5rem 1rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--accent-emerald);
        }

        .pulse-dot {
            width: 8px;
            height: 8px;
            background-color: var(--accent-emerald);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.25rem;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }

        .stat-card:hover {
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.2);
        }

        .stat-label {
            font-size: 0.8125rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }

        .stat-value {
            font-family: 'Outfit', sans-serif;
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-main);
        }

        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        @media (max-width: 960px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
        }

        .panel {
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 1.5rem;
        }

        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.25rem;
        }

        .panel-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1.125rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .tabs {
            display: flex;
            gap: 0.5rem;
            background: rgba(0, 0, 0, 0.3);
            padding: 0.25rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }

        .tab {
            flex: 1;
            padding: 0.5rem;
            text-align: center;
            font-size: 0.8125rem;
            font-weight: 500;
            color: var(--text-muted);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .tab.active {
            background: var(--accent-blue);
            color: #ffffff;
        }

        .form-group {
            margin-bottom: 1rem;
        }

        label {
            display: block;
            font-size: 0.8125rem;
            font-weight: 500;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
        }

        input[type="text"], textarea, select {
            width: 100%;
            padding: 0.75rem 1rem;
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid var(--card-border);
            border-radius: 10px;
            color: var(--text-main);
            font-family: inherit;
            font-size: 0.875rem;
            transition: border-color 0.2s ease;
        }

        input[type="text"]:focus, textarea:focus, select:focus {
            outline: none;
            border-color: var(--accent-blue);
        }

        textarea {
            resize: vertical;
            min-height: 110px;
        }

        button.btn-primary {
            width: 100%;
            padding: 0.875rem;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            border: none;
            border-radius: 12px;
            color: #ffffff;
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            font-size: 0.9375rem;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
            transition: opacity 0.2s ease, transform 0.1s ease;
        }

        button.btn-primary:hover {
            opacity: 0.95;
            transform: translateY(-1px);
        }

        .output-card {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 1rem;
            margin-top: 1rem;
        }

        .output-title {
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            font-size: 1rem;
            color: var(--accent-blue);
            margin-bottom: 0.5rem;
        }

        .output-meta {
            display: flex;
            gap: 0.75rem;
            margin-bottom: 0.75rem;
        }

        .badge {
            background: rgba(139, 92, 246, 0.2);
            color: var(--accent-purple);
            border: 1px solid rgba(139, 92, 246, 0.3);
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 500;
        }

        .post-preview {
            background: rgba(255, 255, 255, 0.03);
            border-left: 3px solid var(--accent-blue);
            padding: 0.75rem 1rem;
            border-radius: 0 8px 8px 0;
            font-size: 0.875rem;
            line-height: 1.5;
            margin-bottom: 0.75rem;
            white-space: pre-wrap;
        }

        .post-preview.linkedin {
            border-left-color: var(--accent-purple);
        }

        .arch-diagram {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .arch-node {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 0.875rem 1.25rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .arch-title {
            font-weight: 600;
            font-size: 0.875rem;
        }

        .arch-desc {
            font-size: 0.75rem;
            color: var(--text-muted);
        }

        .arrow-down {
            text-align: center;
            color: var(--text-muted);
            font-size: 1rem;
        }

        footer {
            text-align: center;
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--card-border);
            color: var(--text-muted);
            font-size: 0.8125rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo-group">
                <div class="logo-icon">⚡</div>
                <div>
                    <h1>Telegram Content Agent</h1>
                    <div class="subtitle">Multi-Format Ingestion & Persistent Memory System</div>
                </div>
            </div>
            <div class="status-badge">
                <div class="pulse-dot"></div>
                System Healthy • Long Polling
            </div>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Active Provider</div>
                <div class="stat-value" style="color: var(--accent-blue);">Gemini 1.5 Flash</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Supported Formats</div>
                <div class="stat-value">Text • URL • PDF</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Style Memory</div>
                <div class="stat-value" style="color: var(--accent-purple);">SQLite Enabled</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Sheet Logger</div>
                <div class="stat-value" style="color: var(--accent-emerald);">Idempotency Active</div>
            </div>
        </div>

        <div class="main-grid">
            <div class="panel">
                <div class="panel-header">
                    <div class="panel-title">🚀 Interactive Content Simulator</div>
                </div>

                <div class="tabs">
                    <div class="tab active" onclick="setTab('url')">🌐 Web URL</div>
                    <div class="tab" onclick="setTab('text')">📝 Plain Text</div>
                    <div class="tab" onclick="setTab('pdf')">📄 PDF Doc</div>
                </div>

                <div class="form-group">
                    <label id="input-label">Article / Web URL</label>
                    <input type="text" id="content-input" value="https://techcrunch.com/2026/ai-agents-automation" placeholder="Paste article link here...">
                </div>

                <div class="form-group">
                    <label>Persistent Style Memory Prompt (or set via /setstyle)</label>
                    <input type="text" id="style-input" value="Witty developer tone with tech insights and subtle emojis" placeholder="e.g. Write like a witty tech expert">
                </div>

                <button class="btn-primary" onclick="simulateIngestion()">Simulate Agent Ingestion & Draft Generation</button>

                <div id="output-container" class="output-card" style="display: none;">
                    <div class="output-title" id="out-title">AI Agents Redefining Software Engineering in 2026</div>
                    <div class="output-meta">
                        <span class="badge" id="out-cat">Category: AI</span>
                        <span class="badge" style="background: rgba(16, 185, 129, 0.2); color: var(--accent-emerald);">Idempotent ID Verified</span>
                    </div>
                    <div class="stat-label">Rationale</div>
                    <div style="font-size: 0.8125rem; margin-bottom: 0.75rem; color: var(--text-muted);" id="out-rationale">Highlights key paradigm shifts in autonomous coding assistants and workflow automation.</div>

                    <div class="stat-label">𝕏 Draft (245 / 280 chars)</div>
                    <div class="post-preview" id="out-x">🚀 AI Agents aren't just autocomplete anymore—they're executing complex full-stack features independently! Here is how modern dev teams leverage agentic workflows in 2026 💻⚡ #AI #DevOps</div>

                    <div class="stat-label">💼 LinkedIn Draft</div>
                    <div class="post-preview linkedin" id="out-li">Autonomous AI Agents are transforming modern software development pipelines.\n\nKey takeaways from recent shifts:\n• Agentic architecture enables end-to-end task completion\n• Code quality & test verification built into loop\n• Developers shift from manual coders to AI pair programming leads.</div>
                </div>
            </div>

            <div class="panel">
                <div class="panel-header">
                    <div class="panel-title">🛠 Architectural Pipeline</div>
                </div>

                <div class="arch-diagram">
                    <div class="arch-node">
                        <div>
                            <div class="arch-title">1. Telegram Ingestion Layer</div>
                            <div class="arch-desc">Long Polling listener accepting Text, URLs, PDFs</div>
                        </div>
                        <span style="color: var(--accent-emerald);">Active</span>
                    </div>

                    <div class="arrow-down">↓</div>

                    <div class="arch-node">
                        <div>
                            <div class="arch-title">2. Format Extractor Router</div>
                            <div class="arch-desc">trafilatura (Web) | markitdown (PDF) | SHA-256 (Text)</div>
                        </div>
                        <span style="color: var(--accent-blue);">Ready</span>
                    </div>

                    <div class="arrow-down">↓</div>

                    <div class="arch-node">
                        <div>
                            <div class="arch-title">3. Persistent SQLite Memory</div>
                            <div class="arch-desc">Fetches user style memory & checks duplicate submission</div>
                        </div>
                        <span style="color: var(--accent-purple);">Connected</span>
                    </div>

                    <div class="arrow-down">↓</div>

                    <div class="arch-node">
                        <div>
                            <div class="arch-title">4. LLM Generation Engine</div>
                            <div class="arch-desc">Gemini / Ollama / Groq with 3x retry self-correction</div>
                        </div>
                        <span style="color: var(--accent-amber);">Structured</span>
                    </div>

                    <div class="arrow-down">↓</div>

                    <div class="arch-node">
                        <div>
                            <div class="arch-title">5. Idempotent Google Sheets Logger</div>
                            <div class="arch-desc">Appends structured row to worksheet 'Content'</div>
                        </div>
                        <span style="color: var(--accent-emerald);">Synced</span>
                    </div>
                </div>
            </div>
        </div>

        <footer>
            Multi-Format Telegram Content Agent • Containerized via Docker & Docker Compose • HTTP Health Check :8000/health
        </footer>
    </div>

    <script>
        let currentTab = 'url';
        function setTab(tab) {
            currentTab = tab;
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            
            const label = document.getElementById('input-label');
            const input = document.getElementById('content-input');
            if (tab === 'url') {
                label.innerText = 'Article / Web URL';
                input.value = 'https://techcrunch.com/2026/ai-agents-automation';
            } else if (tab === 'text') {
                label.innerText = 'Plain Text Content';
                input.value = 'We are releasing a new major update to our developer platform with automated workflows and real-time monitoring.';
            } else if (tab === 'pdf') {
                label.innerText = 'PDF Document Path / File Name';
                input.value = 'q3_strategy_report.pdf';
            }
        }

        function simulateIngestion() {
            const outContainer = document.getElementById('output-container');
            const style = document.getElementById('style-input').value;
            outContainer.style.display = 'block';
            
            if (style.toLowerCase().includes('pirate')) {
                document.getElementById('out-x').innerText = 'Ahoy mateys! 🏴‍☠️ The AI agents be takin over the code seas in 2026! Sail into automated dev pipelines! ⚡ #AI';
            } else {
                document.getElementById('out-x').innerText = '🚀 AI Agents aren\'t just autocomplete anymore—they\'re executing complex full-stack features independently! Here is how modern dev teams leverage agentic workflows in 2026 💻⚡ #AI #DevOps';
            }
        }
    </script>
</body>
</html>
"""
