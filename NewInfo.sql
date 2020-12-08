ALTER TABLE CUSTOMERS 
ADD customer_role varchar(50) DEFAULT 'leatherman';

INSERT INTO CUSTOMERS VALUES (100,'Van Darkholme - admin', 48, '8344@ukr.net',
							  'a320480f534776bddb5cdb54b1e93d210a3c7d199e80a23c1b2178497b184c76', 'VanDarkholme',
							  '1234 1234 1234 1234','Full Master');


create or replace function update_customer(
	c_id customers.customer_id%type, 
	customer_login_v customers.customer_login%type, 
    customer_email_v customers.customer_email%type, 
	customer_age_v customers.customer_age%type, 
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
	SET (customer_login,customer_email,customer_age,customer_name,bank_card) = (customer_login_v,customer_email_v,customer_age_v,customer_name_v,bank_card_v)
	WHERE customers.customer_id = c_id;
	
	status := 'Successfully updated';
	
	return status;
	exception 
	   when others then 
	      status := 'Error updating';
		  return status;
end;
$body$ 


ALTER TABLE contracts
DROP CONSTRAINT contracts_contract_price_check;

ALTER TABLE CONTRACTS 
ADD COLUMN contract_is_paid boolean DEFAULT false

ALTER TABLE CHILDREN_CONTRACTS 
ADD COLUMN contract_is_paid boolean DEFAULT false



create or replace function create_contract(
	fk_customer_id_v contracts.fk_customer_id%TYPE,
	contract_type_v contracts.contract_type%TYPE,
	contract_price_v contracts.contract_price%TYPE,
	contract_end_date_v contracts.contract_end_date%TYPE
) returns text
language plpgsql
as
$body$
declare
   status int;
begin

	INSERT INTO contracts(fk_customer_id,contract_type,contract_price,contract_end_date) 
	VALUES (fk_customer_id_v,contract_type_v,contract_price_v,contract_end_date_v);
	
	status := currval(pg_get_serial_sequence('contracts','contract_id'));
	

	return status;
end;
$body$


create or replace function create_child_contract(
	child_name_v children_contracts.child_name%TYPE,
	fk_customer_id_v children_contracts.fk_customer_id%TYPE,
	contract_type_v children_contracts.contract_type%TYPE,
	contract_price_v children_contracts.contract_price%TYPE,
	contract_end_date_v children_contracts.contract_end_date%TYPE
) returns text
language plpgsql
as
$body$
declare
   status text;
begin

	IF child_name_v LIKE '' then
	child_name_v := NULL;
	END IF;

	INSERT INTO children_contracts(fk_customer_id,child_name,contract_type,contract_price,contract_end_date) 
	VALUES (fk_customer_id_v,child_name_v,contract_type_v,contract_price_v,contract_end_date_v);
	
	status := currval(pg_get_serial_sequence('children_contracts','child_id'));
	

	return status;
end;
$body$

ALTER TABLE children_contracts
DROP CONSTRAINT children_contracts_contract_price_check