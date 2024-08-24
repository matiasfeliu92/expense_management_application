CREATE VIEW user_expenses AS
SELECT 
    users.name AS user_name,
    users.email AS user_email,
    expenses.concept AS expense_concept,
    expenses.amount AS expense_amount,
    expenses.type AS expense_type,
    expenses.createdAt AS created_at,
    expenses.updatedAt AS updated_at
FROM 
    users
INNER JOIN 
    expenses 
ON 
    users.id = expenses.user_id;