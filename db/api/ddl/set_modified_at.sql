CREATE OR REPLACE FUNCTION public.set_modified_at()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.modified_at := now();
    RETURN NEW;
END;
$$;
