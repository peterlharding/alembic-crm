-- Superseded by set_modified_at.sql in revision 010: no table has a
-- when_modified column. Kept because revision 001 and the downgrade of
-- revision 010 load it.

CREATE OR REPLACE FUNCTION public.set_when_modified()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.when_modified := now();
    RETURN NEW;
END;
$$;
