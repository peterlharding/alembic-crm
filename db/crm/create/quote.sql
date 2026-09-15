
-- quote

DROP TABLE IF EXISTS public.quote CASCADE;

CREATE TABLE public.quote (
    id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    quote_date       date,
    quote_amount     numeric(12,2),

    quoter           varchar(64) NOT NULL,
    quoter_id        bigint,

    account_id       bigint,
    company          varchar(80) DEFAULT NULL,

    contact_id       bigint,
    contact          varchar(32) DEFAULT NULL,

    comment          text DEFAULT '',
    description      text DEFAULT '',

    order_no         varchar(32) DEFAULT NULL,
    order_date       date,
    order_amount     numeric(12,2),

    invoice_no       varchar(32) DEFAULT NULL,
    invoice_date     date,
    invoice_amount   numeric(12,2),

    status           varchar(16) DEFAULT 'Active',
    doc_path         text,

    modified_at      timestamptz NOT NULL DEFAULT now(),
    modified_by_id   bigint,
    created_at       timestamptz NOT NULL DEFAULT now(),
    created_by_id    bigint
);

