create database internship;
use internship;
create table customer (CustomerID int,CustomerName varchar(20) not null,city varchar(10) not null,primary key(CustomerID));
insert into customer (CustomerID,CustomerName,city)values(101,"Ayush","Pune"),(102,"Shashi","Mumbai"),(103,"Kiran","Solapur");
select * from customer
#Where claues
SELECT *
FROM customer
WHERE city = 'Pune';
