/**
 * Shadow Corp — Internal Admin API (Node.js / Express)
 * ======================================================
 * This microservice simulates a private internal API that should NEVER
 * be reachable from the public internet — only accessible within the
 * Docker private network.
 *
 * It is the SSRF target:
 *   Attacker → (via backend) → http://internal-api:3000/admin/secret
 *
 * Port 3000 is NOT exposed to the host in docker-compose (internal only).
 */

const express = require('express');
const app = express();

// ── "Secret" internal endpoints ─────────────────────────────────────────────

app.get('/', (req, res) => {
  res.json({
    service: 'ShadowCorp Internal Admin API',
    version: '1.0.0',
    endpoints: [
      'GET /admin/secret',
      'GET /admin/users',
      'GET /admin/config',
      'GET /health',
    ],
    note: 'This service is internal only — should not be reachable from the internet.',
  });
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', uptime: process.uptime() });
});

// Simulate a sensitive internal endpoint
app.get('/admin/secret', (req, res) => {
  res.json({
    WARNING: 'SSRF SUCCESSFUL — you reached the internal admin API!',
    internal_token:    'sk-internal-shadowcorp-a7f3b91c2d04e5f6',
    db_password:       'Pr0d-DB-P@ss!2025',
    jwt_secret:        'shadow-corp-insecure-dev-key-DO-NOT-USE',
    internal_api_base: 'http://internal-api:3000',
    admin_email:       'admin@shadowcorp.com',
    notes: 'This would typically expose cloud metadata, internal tokens, or service credentials.',
  });
});

app.get('/admin/users', (req, res) => {
  res.json({
    WARNING: 'Internal user dump — only accessible via SSRF',
    users: [
      { id: 6, username: 'support_admin', role: 'support-admin', internal_notes: 'Provisioned 2024-01-15' },
      { id: 7, username: 'superadmin',    role: 'super-admin',   internal_notes: 'Do not rotate password without notice' },
    ],
  });
});

app.get('/admin/config', (req, res) => {
  res.json({
    WARNING: 'Internal config dump — only accessible via SSRF',
    flask_secret:   'shadow-corp-insecure-dev-key-DO-NOT-USE',
    database:       'LabDatabase.db',
    debug:          true,
    smtp_password:  'smtp-p4ssw0rd-internal',
    aws_key_id:     'AKIAIOSFODNN7EXAMPLE',
    aws_secret:     'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
  });
});

// ── Start ────────────────────────────────────────────────────────────────────
const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`[internal-api] Listening on port ${PORT} (internal network only)`);
});
