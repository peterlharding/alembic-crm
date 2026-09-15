
-- audit_log sample data
--
-- No foreign keys are declared: reference_type 1 is account and 2 is
-- opportunity, reference_id is the row id, user_id holds the username.

INSERT INTO public.audit_log (
    application,
    reference_type,
    reference_id,
    reference,
    event,
    description,
    user_id
) VALUES
(
    'crm',
    1,
    1,
    'ACC-0001',
    'update',
    'Changed rating from Warm to Hot',
    'plh'
),
(
    'crm',
    2,
    2,
    'Harbourview - Patient Booking',
    'close_won',
    'Opportunity closed won at 22500.00',
    'plh'
);
