-- quert 1
SELECT COUNT(*)
FROM orders;

-- query 2
SELECT MIN(orderdate)
FROM orders;

-- query 3
SELECT MAX(orderdate)
FROM orders;

DROP TABLE if exists end_obs_dates;

CREATE TABLE end_obs_dates 
AS
SELECT GENERATE_SERIES AS end_obs_date
FROM GENERATE_SERIES(CAST('1996-08-01' AS DATE),CAST('1998-06-01' AS DATE),'1 month');

DROP TABLE if exists ads_population_hist;

CREATE TABLE ads_population_hist 
AS
SELECT A.*,
       B.*
FROM end_obs_dates AS A
  CROSS JOIN (SELECT DISTINCT customerid FROM customers) AS B;

 -- query 4
SELECT *
FROM ads_population_hist
LIMIT 10;

-- query 5
SELECT *,
       unitprice*quantity AS totalprice_for_product
FROM order_details
LIMIT 20;


-- query 6
SELECT A.orderid,
       COUNT(DISTINCT A.productid) AS no_of_distinct_products,
       SUM(A.quantity) AS no_of_items,
       SUM(A.totalprice_for_product) AS total_price,
       SUM(A.discount * A.totalprice_for_product)/SUM(A.totalprice_for_product) as total_discount,
       SUM(A.discount)/COUNT(DISTINCT A.productid) as avg_discount_per_order
FROM (SELECT *,
             unitprice*quantity AS totalprice_for_product
      FROM order_details) AS A
GROUP BY 1;

-- query 7
SELECT orderid,
       customerid,
       orderdate
FROM orders
LIMIT 10;


-- query 8
SELECT orderid,
       customerid,
       orderdate,
       CAST(DATE_TRUNC('month',orderdate) +INTERVAL '1 month' AS DATE) AS end_obs_date
FROM orders
order by (customerid,CAST(DATE_TRUNC('month',orderdate) +INTERVAL '1 month' AS DATE))
LIMIT 10;

DROP TABLE if exists ads_orders_hist;

CREATE TABLE ads_orders_hist 
AS
SELECT A.orderid,
       A.customerid,
       A.end_obs_date,
       B.no_of_distinct_products,
       B.no_of_items,
       B.total_price,
       B.total_discount,
       B.avg_discount_per_order
FROM (
-- table orders

     SELECT orderid,customerid,orderdate,CAST(DATE_TRUNC('month',orderdate) +INTERVAL '1 month' AS DATE) AS end_obs_date 
     FROM orders) AS A
  LEFT OUTER JOIN (
-- table order_details
SELECT A.orderid,
  COUNT (DISTINCT A.productid) AS no_of_distinct_products,
  SUM (A.quantity) AS no_of_items,
  SUM (A.totalprice_for_product) AS total_price,
  SUM(A.discount * A.totalprice_for_product)/SUM(A.totalprice_for_product) as total_discount,
  SUM(A.discount)/COUNT(DISTINCT A.productid) as avg_discount_per_order
    FROM (
-- adding totalprice_for_product
SELECT*,unitprice*quantity AS totalprice_for_product FROM order_details) AS A
GROUP BY 1) AS B ON A.orderid = B.orderid;

-- query 9
SELECT orderid,
       COUNT(*)
FROM ads_orders_hist
GROUP BY 1
ORDER BY 2 DESC LIMIT 5;

DROP TABLE if exists ads_observation_hist;

CREATE TABLE ads_observation_hist 
AS
SELECT A.*
-- we can replace missings with 0 because it means there were no orders for this client during specific month.
       ,
       COALESCE(B.no_of_distinct_orders_1M,0) AS no_of_distinct_orders_1M,
       COALESCE(B.no_of_items_1M,0) AS no_of_items_1M,
       COALESCE(B.total_price_1M,0) AS total_price_1M,
       COALESCE(B.total_discount_1M,0) as total_discount_1M,
       COALESCE(B.avg_discount_per_order_1M,0) as avg_discount_per_order_1M       
FROM ads_population_hist AS A
  LEFT OUTER JOIN (
-- we need to group by our orders to customer level
SELECT customerid,
  end_obs_date,
  COUNT (DISTINCT orderid) AS no_of_distinct_orders_1M,
  SUM (no_of_items) AS no_of_items_1M,
  SUM (total_price) AS total_price_1M, 
  SUM (total_discount*total_price)/SUM(total_price) as total_discount_1M,
  SUM (avg_discount_per_order)/COUNT(DISTINCT orderid) as avg_discount_per_order_1M
FROM ads_orders_hist
GROUP BY 1,
         2) AS B ON A.customerid = B.customerid AND A.end_obs_date = B.end_obs_date;

-- query 10
SELECT customerid,
       end_obs_date,
       COUNT(*)
FROM ads_observation_hist
GROUP BY 1,
         2
ORDER BY 3 DESC LIMIT 5;



DROP TABLE if exists threeM;
CREATE TABLE threeM
AS
SELECT customerid, end_obs_date, 
    lag(no_of_items_1M,1) over w as previous, 
    no_of_items_1M as currently, 
    lead(no_of_items_1M,1) over w as next,
    LAG(total_price_1M,1) over w as previous_tp,
    total_price_1M as currently_tp,
    lead(total_price_1M,1) over w as next_tp
  from ads_observation_hist
  window w as (partition by customerid order by end_obs_date);

-- query 11
select customerid, end_obs_date, (select max(x) from (VALUES (currently_tp), (previous_tp),(next_tp)) as value(x)) as max_tp_3m from threeM;

-- query 11
SELECT ads_observation_hist.*, 
-- could use coalesce to replace empty with 0  
  COALESCE(threeM.previous+threeM.currently+threeM.next,0) as no_of_items_3M,
  COALESCE(threeM.previous_tp+threeM.currently_tp+threeM.next_tp,0) as total_price_3M,
  COALESCE((select max(x) from (VALUES (threeM.currently_tp), (threeM.previous_tp),(threeM.next_tp)) as mxvalue(x)),0) as max_monthlytotal_price_3M,
  COALESCE((select min(x) from (VALUES (threeM.currently_tp), (threeM.previous_tp),(threeM.next_tp)) as mnvalue(x)),0) as min_monthlytotal_price_3M,
  COALESCE((select avg(x) from (VALUES (threeM.currently), (threeM.previous),(threeM.next)) as avgvalue(x)),0) as avg_no_of_items_3M
-- ADD NEW ATTRIBUTES HERE
FROM ads_observation_hist
join threeM
  on ads_observation_hist.customerid = threeM.customerid AND ads_observation_hist.end_obs_date = threeM.end_obs_date
ORDER BY END_OBS_DATE
--where ads_observation_hist.customerid = 'ANATR'
LIMIT 150;

-- query 12
-- select * from ads_population_hist;
