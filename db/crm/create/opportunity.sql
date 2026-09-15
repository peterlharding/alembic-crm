
-- opportunity

DROP TABLE IF EXISTS public.opportunity;

CREATE TABLE public.opportunity (
    id                          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    guid                        uuid,

    name                        varchar(128),
    description                 text,

    stage_name                  varchar(32),
    amount                      varchar(32),
    probability                 varchar(32),
    expected_revenue            varchar(32),
    total_opportunity_quantity  varchar(32),
    type                        varchar(64),
    next_step                   varchar(32),

    account_id                  bigint,
    owner_id                    bigint,

    lead_source                 text,

    is_private                  boolean DEFAULT false,
    is_closed                   boolean DEFAULT false,
    is_won                      boolean DEFAULT false,
    is_deleted                  boolean DEFAULT false,

    forecast_category           varchar(32),
    campaign_ref                uuid,
    has_opportunity_line_item   boolean DEFAULT false,

    pricebook_ref               uuid,

    close_date                  timestamptz NOT NULL DEFAULT now(),
    last_activity_date          timestamptz NOT NULL DEFAULT now(),

    fiscal_year                 varchar(32),
    fiscal_quarter              varchar(32),

    modified_at                 timestamptz NOT NULL DEFAULT now(),
    modified_by_id              bigint,
    created_at                  timestamptz NOT NULL DEFAULT now(),
    created_by_id               bigint
);

