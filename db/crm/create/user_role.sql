
-- user_role

DROP TABLE IF EXISTS user_role CASCADE;

CREATE TABLE public.user_role (
    id                                    bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    guid                                  uuid,
    name                                  varchar(64),

    parent_role_id                        bigint,
    rollup_description                    text,

    opportunity_access_for_account_owner  varchar(20) DEFAULT 'Edit',
    case_access_for_account_owner         varchar(20) DEFAULT 'Edit',
    contact_access_for_account_owner      varchar(20) DEFAULT 'Edit',

    forecast_user_id                      bigint,

    portal_account_ref                    varchar(18),
    portal_type                           varchar(20),

    modified_at                           timestamptz NOT NULL DEFAULT now(),
    modified_by_id                        bigint,
    created_at                            timestamptz NOT NULL DEFAULT now(),
    created_by_id                         bigint
);


