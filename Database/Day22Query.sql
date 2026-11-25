show databases
create database Retail_analysis
use Retail_analysis
select*from retail_sales LIMIT 5
select count(*) as total_rows from retail_sales
select SUM(Sales) as Total_revenue from retail_sales
select Count(DISTINCT Order_ID) as Total_Order from retail_sales
select sum(Quantity) as Unit_sold from retail_sales
select Category,sum(Sales) as Total_sales from retail_sales group by Category order by Total_sales Desc
SELECT strftime('%Y-%m', Order_Date) AS Year_Month,SUM(Sales) AS Monthly_Revenue,COUNT(DISTINCT Order_ID) AS Total_Orders FROM retail_sales GROUP BY Year_Month ORDER BY Year_Month;
SELECT Product_Name,SUM(Sales) AS Total_Revenue FROM retail_sales GROUP BY Product_Name ORDER BY Total_Revenue DESC;