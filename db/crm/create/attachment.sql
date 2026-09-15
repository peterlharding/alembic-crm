
-- attachment

DROP TABLE IF EXISTS public.attachment;

CREATE TABLE public.attachment (
    id                      bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    guid                    uuid,
    name                    varchar(128),

    content_type            varchar(32),
    body_length             integer DEFAULT 0,
    body_length_compressed  integer DEFAULT 0,

    parent_id               bigint,
    owner_id                bigint,

    is_deleted              boolean DEFAULT false,
    is_private              boolean DEFAULT false,

    modified_at             timestamptz NOT NULL DEFAULT now(),
    modified_by_id          bigint,
    created_at              timestamptz NOT NULL DEFAULT now(),
    created_by_id           bigint
);

