from typing import Optional
from pydantic import BaseModel,constr
from datetime import datetime

# User schema 
class UserBase(BaseModel):
    username: str
    password: str
    complete_name: str 
    email_address: str 


    class Config:
        orm_mode = True


class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

# Member Schema
class MemberBase(BaseModel):
    First_name: str
    Middle_name: Optional[str] = None
    Last_name: str
    Email: str
    Country_Id : int 
    Contact_Number: str
    username: str
    password: str
    account_status: int
    processed_by_id: int


class MemberCreate(MemberBase):
    pass


class MemberUpdate(MemberBase):
    pass


class Member(MemberBase):
   # id: int

    class Config:
        orm_mode = True

#Country Info Schema
class country_supported_base(BaseModel):
    
    Country_Name : str
    
    class Config:
        orm_mode = True
    

class add_country(country_supported_base):
    pass    

class update_country(country_supported_base):
    pass

class Country_Info(country_supported_base):
    Country_Id : int 
    
    class config:
        orm_mode = True


#currency supported schema

class currency_supported_base(BaseModel):
    status : int
    USD_equivalent : int
    currency_info_id : int
   
    
    class Config:
        orm_mode = True
    

class add_currency(currency_supported_base):
    pass    

class update_currency(currency_supported_base):
    pass

class currency_supported(currency_supported_base):
    currency_id : int 
    
    class config:
        orm_mode = True



#schema for currency_info 

class  currency_info_base(BaseModel):
       currency_symbol: str
       currency_name : str
       
       

       class Config:
           orm_mode = True
class add_currency_info(currency_info_base):
    pass    

class update_currency_info(currency_info_base):
    pass

class currency_info (currency_info_base):
    currency_info_id : int 
    
    class Config:
        orm_mode = True





class WithdrawalBase(BaseModel):
    transaction_code: str
    amount: float
    charged: float
    to_receive: float
    date_time: datetime
    method: str
    status: int
    remarks: str
    member_id : int
    
    class Config:
        orm_mode = True
class WithdrawalCreate(WithdrawalBase):
    pass


class WithdrawalUpdate(WithdrawalBase):
    
    pass


class Withdrawal(WithdrawalBase):
    withdrawal_id: int

    class Config:
        orm_mode = True


class DepositBase(BaseModel):
    transaction_code: str
    member_id: int
    deposit_amount: float
    currency_id: int
    date_time: datetime
    gateway_id: int
    status_id: int
   

    class Config:
        orm_mode = True


class DepositCreate(DepositBase):
    pass


class DepositUpdate(DepositBase):
    pass


class Deposit(DepositBase):
    id: int

    class Config:
        orm_mode = True


#Deposits status INfo Schema

class deposit_status_base(BaseModel):

    status: int
    remarks: str

    class Config:
        orm_mode = True


class add_deposit_status(deposit_status_base):
    pass


class update_status(deposit_status_base):
    pass


class  deposit_status(deposit_status_base):
   # id: int

    class Config:
        orm_mode = True




#Gateway  schema
class gateway_base(BaseModel):
    gateway_name : str
    gateway_status: bool
    gateway_type : str
  
    
    class Config:
        orm_mode = True
    

class add_gateway(gateway_base):
    pass    

class update_gateway(gateway_base):
    pass

class gateway(gateway_base):
    gateway_id : int 
    
    class config:
        orm_mode = True


class TransactionLogBase(BaseModel):
    member_id: int
    transaction_type: int
    amount: float
    status: int


class TransactionLogCreate(TransactionLogBase):
    pass


class TransactionLogUpdate(TransactionLogBase):
    pass


class TransactionLog(TransactionLogBase):
    transaction_log_id: int

    class Config:
        orm_mode = True



from pydantic import BaseModel

class MemberTransactionStatus(BaseModel):
    MemberID: int
    Username: str
    EmailAddress: str
    TotalDepositAmount: float
    TotalWithdrawalAmount: float
    TransactionStatus: str