
-- token_blacklist sample data
--
-- No foreign keys are declared: user_id refers to application_user 1 (admin)
-- and 2 (plh). jti is the JWT id of the revoked token.

INSERT INTO public.token_blacklist (
    jti,
    user_id,
    reason,
    expiry
) VALUES
(
    '0d52e1ff-8448-4f69-ad08-24982b8aba58',
    2,
    'logout',
    now() + interval '1 hour'
),
(
    'f60a5eac-c9b3-4688-90b4-b3d2cec6d23e',
    1,
    'password changed',
    now() + interval '15 minutes'
);
