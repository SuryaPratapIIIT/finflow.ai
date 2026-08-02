-- 1. DSO (Days Sales Outstanding) trend by month
-- Note: Simplified DSO approximation for this portfolio project.
-- We group by invoice month and calculate the average days_late for paid invoices.
SELECT 
    strftime('%Y-%m', i.due_date) as month,
    AVG(p.days_late) as avg_days_late
FROM invoices i
JOIN payment_history p ON i.id = p.invoice_id
GROUP BY month
ORDER BY month;

-- 2. Top 5 customers by total overdue amount
SELECT 
    c.name,
    SUM(i.amount) as total_overdue
FROM invoices i
JOIN customers c ON i.customer_id = c.id
WHERE i.status = 'overdue'
GROUP BY c.id, c.name
ORDER BY total_overdue DESC
LIMIT 5;

-- 3. % of invoices paid late vs on time, grouped by customer reliability tier
-- Using a CASE statement to bucket the continuous score into tiers
SELECT 
    CASE 
        WHEN c.payment_reliability_score >= 80 THEN 'Reliable'
        WHEN c.payment_reliability_score >= 40 THEN 'Moderate'
        ELSE 'Unreliable'
    END as tier,
    COUNT(p.id) as total_invoices,
    SUM(CASE WHEN p.paid_on_time = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(p.id) as pct_on_time,
    SUM(CASE WHEN p.paid_on_time = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(p.id) as pct_late
FROM payment_history p
JOIN customers c ON p.customer_id = c.id
GROUP BY tier;

-- 4. A "bottleneck" query: average days between invoice due_date and first follow-up
-- TODO: Once we have an 'outreach_logs' table mapping invoice_id to follow_up_date, 
-- we can join it here. Example conceptual query:
/*
SELECT 
    AVG(julianday(o.follow_up_date) - julianday(i.due_date)) as avg_followup_lag
FROM invoices i
JOIN outreach_logs o ON i.id = o.invoice_id
WHERE i.status = 'overdue'
*/
