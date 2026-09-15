
-- login_session sample data
--
-- No foreign keys are declared: user_id refers to application_user 1 (admin)
-- and 2 (plh). Only the sha256 of a session token is stored; the tokens here
-- are the literal strings being hashed. Session 2 has been revoked, so only
-- session 1 shows in login_session_active.

INSERT INTO public.login_session (
    session_token_hash,
    user_id,
    workstation,
    ip_address,
    user_agent,
    data,
    revoked_at
) VALUES
(
    sha256('sample-session-token-1'::bytea),
    2,
    'demo-laptop',
    '192.0.2.10',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 15_6) AppleWebKit/605.1.15 Safari/605.1.15',
    '{"theme": "dark", "last_view": "opportunity"}',
    NULL
),
(
    sha256('sample-session-token-2'::bytea),
    1,
    'demo-desktop',
    '198.51.100.24',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/142.0',
    '{}',
    now()
);
