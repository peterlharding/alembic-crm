-- Every table with a modified_at column must have it stamped by an UPDATE.
-- Runs in a transaction that is rolled back, so the database is unchanged.

BEGIN;

DO $$
DECLARE
    tbl    text;
    rows   bigint;
    stale  bigint;
    tested int := 0;
BEGIN
    FOR tbl IN
        SELECT c.relname
          FROM pg_class c
          JOIN pg_namespace n ON n.oid = c.relnamespace
          JOIN pg_attribute a ON a.attrelid = c.oid
         WHERE n.nspname = 'public'
           AND c.relkind = 'r'
           AND a.attname = 'modified_at'
           AND NOT a.attisdropped
         ORDER BY c.relname
    LOOP
        EXECUTE format('SELECT count(*) FROM public.%I', tbl) INTO rows;
        IF rows = 0 THEN
            RAISE NOTICE 'skip %: no rows to update', tbl;
            CONTINUE;
        END IF;

        -- Back-date every row, then let the trigger overwrite it. now() is
        -- the transaction start, so a stamped row reads exactly now().
        EXECUTE format('UPDATE public.%I SET modified_at = %L', tbl, '2000-01-01');
        EXECUTE format('SELECT count(*) FROM public.%I WHERE modified_at <> now()', tbl) INTO stale;
        IF stale > 0 THEN
            RAISE EXCEPTION 'UPDATE on % did not stamp modified_at on % of % rows', tbl, stale, rows;
        END IF;

        RAISE NOTICE 'ok %: modified_at stamped on % rows', tbl, rows;
        tested := tested + 1;
    END LOOP;

    IF tested = 0 THEN
        RAISE EXCEPTION 'no table with a modified_at column had rows to test';
    END IF;
END;
$$;

ROLLBACK;
