-- Password: Much-More-Secret

INSERT INTO public.application_user (
    user_guid,
    username,
    password_hash,
    email,
    first_name,
    last_name,
    role,
    is_active,
    notes
) VALUES (
    '3b3fb7f6-1c39-452e-a5bb-262e58618ceb',
    'admin',
    'a81b423e3b1afc6e915f934c7e364d4201c4ccb1df00e890e6eabc89b549a775',
    'admin@example.com',
    'Admin',
    'User',
    'admin',
    True,
    ''
);
