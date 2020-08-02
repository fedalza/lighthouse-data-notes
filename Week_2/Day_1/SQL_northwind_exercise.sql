-- Q1. Write a query to get Product name and quantity/unit.
SELECT ProductName, UnitsInStock From Products;

-- Q2. Write a query to get most expense and least expensive Product list (name and unit price)
SELECT ProductName, UnitPrice from Products
  Where (UnitPrice = (Select Max(UnitPrice) from Products) OR UnitPrice = (Select Min(UnitPrice) from Products))
  ORDER by UnitPrice DESC;

-- Q3. Write a query to count current and discontinued products.
SELECT COUNT(ProductID)-Count(distinct Discontinued) as Current, Count(distinct Discontinued) as discontinued from Products;

-- Q4. Select all product names and their category names (77 rows)
SELECT Products.ProductName, Categories.CategoryName from Products
  Left outer join Categories
    on Categories.CategoryID=Products.CategoryID;

-- Q5. Select all product names, unit price and the supplier region that don't have suppliers from USA region. (26 rows)
SELECT Products.ProductName, Products.UnitPrice, Suppliers.Region from Products
  left outer join Suppliers
    on Suppliers.SupplierID = Products.SupplierID
  where Suppliers.Country NOT LIKE '%USA%';

-- Q6. Get the total quantity of orders sold.( 51317)
SELECT SUM(Quantity) from Order_Details;


-- Q7. Get the total quantity of orders sold for each order.(830 rows)
SELECT distinct OrderID, Quantity from Order_Details;

-- Q8. Get the number of employees who have been working more than 5 year in the company. (9 rows)
SELECT EmployeeID from Employees
  where DATEDIFF(year,GETDATE(),HireDate)>5
