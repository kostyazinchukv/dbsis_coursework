ALTER TABLE CUSTOMERS 
ADD customer_role varchar(50) DEFAULT 'leatherman';


INSERT INTO CUSTOMERS VALUES (100,'Van Darkholme - admin', 48, '8889344@ukr.net',
							  'a320480f534776bddb5cdb54b1e93d210a3c7d199e80a23c1b2178497b184c76', 'VanDarkholme',
							  '1234 1234 1234 1234','Full Master');


create or replace function update_customer(
	c_id customers.customer_id%type, 
	customer_login_v customers.customer_login%type, 
    customer_email_v customers.customer_email%type, 
    customer_name_v customers.customer_name%type,
	bank_card_v customers.bank_card%type
) returns text
language plpgsql
as
$body$
declare
   status text;
begin
	
	IF customer_name_v LIKE '' then
	customer_name_v := NULL;
	END IF;
	
	UPDATE customers
	SET (customer_login,customer_email,customer_name,bank_card) = (customer_login_v,customer_email_v,customer_name_v,bank_card_v)
	WHERE customers.customer_id = c_id;
	
	status := 'Successfully updated';
	
	return status;
	exception 
	   when others then 
	      status := 'Error updating';
		  return status;
end;
$body$