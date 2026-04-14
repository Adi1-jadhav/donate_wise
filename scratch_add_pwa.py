import os

pwa_snippet = """
    <!-- PWA Installation Requirements -->
    <link rel="manifest" href="/static/manifest.json">
    <meta name="theme-color" content="#4f46e5">
    <script>
      if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
          navigator.serviceWorker.register('/static/sw.js');
        });
      }
    </script>
"""

files = ['landing.html', 'donate.html', 'dashboard.html', 'ngo_dashboard.html', 'history.html', 'profile.html', 'register.html', 'donor_login.html', 'ngo_login.html', 'admin_login.html']
project_dir = r"c:\Users\Rahul Bhamare\.gemini\antigravity\scratch\-Helping-Hand-Intelligent-System-main"
template_dir = os.path.join(project_dir, 'templates')

for f in files:
    p = os.path.join(template_dir, f)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f_in:
            content = f_in.read()
        
        if '<link rel="manifest"' not in content:
            content = content.replace('</head>', pwa_snippet + '</head>')
            with open(p, 'w', encoding='utf-8') as f_out:
                f_out.write(content)
            print(f"Updated {p}")
        else:
            print(f"Skipped {p} (already has manifest)")
    else:
        print(f"File not found: {p}")
