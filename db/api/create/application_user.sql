
-- DROP TABLE IF EXISTS public.application_user;

CREATE TABLE public.application_user (
    id              integer     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_guid       uuid        NOT NULL DEFAULT gen_random_uuid(),
    username        text        NOT NULL,
    password_hash   text        NOT NULL,
    email           text        NOT NULL,
    first_name      text,
    last_name       text,
    role            text        NOT NULL DEFAULT 'user',
    is_active       boolean     NOT NULL DEFAULT true,
    notes           text        NOT NULL DEFAULT '',
    last_login      timestamptz,
    created_at      timestamptz NOT NULL DEFAULT now(),
    modified_at     timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT application_user_user_guid_key UNIQUE (user_guid),
    CONSTRAINT application_user_username_key  UNIQUE (username),
    CONSTRAINT application_user_role_check    CHECK (role IN ('user', 'admin', 'service')),
    CONSTRAINT application_user_username_len  CHECK (char_length(username) BETWEEN 3 AND 64),
    CONSTRAINT application_user_email_len     CHECK (char_length(email) <= 320),
    CONSTRAINT application_user_email_format  CHECK (email LIKE '%_@_%._%')
);


-- ----------------------------------------------------------------------------
-- Case-insensitive uniqueness: Peter@x.com and peter@x.com are one account
CREATE UNIQUE INDEX application_user_email_lower_key
    ON application_user (lower(email));


--  ---------------------------------------------------------------------------
-- New tables should call public.set_modified_at().
CREATE TRIGGER application_user_set_modified_at
    BEFORE UPDATE ON public.application_user
    FOR EACH ROW
    WHEN (OLD.* IS DISTINCT FROM NEW.*)
    EXECUTE FUNCTION public.set_modified_at();


--  ---------------------------------------------------------------------------
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


