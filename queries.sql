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


INSERT INTO categories (name, description)
VALUES ("salary", "This category covers the collection of salaries for jobs"), 
("service payment", "This category covers the payment of utility bills such as electricity, gas, telephone, internet, water, etc."), 
("shopping", "This category covers purchases made, whether food, clothing, appliances, household items, furniture, etc."), 
("rent", "This category covers the payment of rent for housing, whether apartments or houses."),
("expense", "This category covers the payment of real estate expenses in the buildings/houses where one lives.")