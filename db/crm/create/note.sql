
-- note

DROP TABLE IF EXISTS public.note;

CREATE TABLE public.note (
    id                      bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    guid                    uuid,

    title                   text,
    body                    text,

    parent_type             varchar(64),
    parent_id               bigint,

    is_deleted              boolean DEFAULT false,
    is_private              boolean DEFAULT false,

    owner_id                bigint,

    modified_at             timestamptz NOT NULL DEFAULT now(),
    modified_by_id          bigint,
    created_at              timestamptz NOT NULL DEFAULT now(),
    created_by_id           bigint
);

