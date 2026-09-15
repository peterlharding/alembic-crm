-- Superseded by set_modified_at.sql: no table has a when_modified column.
-- Kept because API_001 and the downgrade of CRM_006 load it.

CREATE OR REPLACE FUNCTION public.set_when_modified()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.when_modified := now();
    RETURN NEW;
END;
$$;
