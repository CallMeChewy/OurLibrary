# audit-secrets.sh
#!/usr/bin/env bash
echo "🔍 Scanning repo for secrets..."

# Common keywords to look for
grep -rInE "secret|password|passwd|pwd|token|apikey|api_key|oauth|client_id|client_secret" --exclude-dir={.git,node_modules,.venv,Data,archive,installers,playwright-report,test-results,.playwright-mcp} .

# Look for hard-coded emails
grep -rInE "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}" --exclude-dir={.git,node_modules,.venv,Data,archive,installers,playwright-report,test-results,.playwright-mcp} .

# Look for common private key headers
grep -rIn "BEGIN RSA PRIVATE KEY" --exclude-dir={.git,node_modules,.venv,Data,archive,installers,playwright-report,test-results,.playwright-mcp} .
grep -rIn "BEGIN PRIVATE KEY" --exclude-dir={.git,node_modules,.venv,Data,archive,installers,playwright-report,test-results,.playwright-mcp} .
 