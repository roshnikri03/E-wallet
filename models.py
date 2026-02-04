from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String,ForeignKey,Boolean,Float,DateTime
from database import Base
from sqlalchemy import event


# User Model
class User(Base): 
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), index=True, nullable=False)
    password = Column(String(50))
    complete_name = Column(String(50),nullable=False)
    email_address = Column(String(120), index=True,unique=True, nullable=False)

class Member(Base):
    __tablename__ = "Members"

    Member_id = Column(Integer,primary_key= True,index = True)
    First_name = Column(String(20))
    Middle_name = Column(String(20))  #optional Attribute
    Last_name = Column(String(20))
    Email = Column(String(150), index=True,unique=True, nullable=False)
    Country_Id = Column(Integer, ForeignKey("Country_Info.Country_Id", onupdate='CASCADE', ondelete='CASCADE'))
    Contact_Number = Column(String(20),unique=True, nullable=False)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(50))
    account_status = Column(Integer)
    processed_by_id = Column(Integer, ForeignKey("Users.id", onupdate='CASCADE', ondelete='CASCADE'))



    processed_by = relationship("User", backref="processed_by", passive_deletes=True)
    deposits = relationship("Deposit", back_populates="member", passive_deletes=True)
    withdrawals = relationship('Withdrawal', back_populates='member', passive_deletes=True)
    transaction_logs = relationship('TransactionLog', back_populates='member', passive_deletes=True)
    currency_info  = relationship('Country_Info', back_populates='member', passive_deletes=True)



#Country Info id 
class Country_Info(Base):
    __tablename__ = "Country_Info"
    
    Country_Id = Column(Integer, primary_key=True, index=True)
    Country_Name = Column(String(40))


    member = relationship('Member', back_populates='currency_info', passive_deletes=True)
    

    #Currency_Support Model

class Currency_supported(Base):
    __tablename__= "Currency_Supported"
    
    currency_id=Column(Integer , primary_key= True , index = True)
    status= Column(Integer , default= False)
    USD_equivalent=Column(Integer)
    currency_info_id= Column(Integer, ForeignKey("Currency_info.currency_info_id", onupdate='CASCADE', ondelete='CASCADE'))

    deposits = relationship("Deposit", back_populates="currency_supported", passive_deletes=True)
    currency_info =  relationship("Currency_info", back_populates="currency_supported", passive_deletes=True)


#currecy_info Model

class Currency_info(Base):
    __tablename__ = "Currency_info"

    currency_info_id=Column(Integer , primary_key= True , index = True)
    currency_name= Column(String(25))
    currency_symbol = Column( String(10))

    currency_supported = relationship("Currency_supported", back_populates="currency_info", passive_deletes=True)
    

class Withdrawal(Base):
    __tablename__ = 'withdrawals'

    withdrawal_id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_code = Column(String(30))
    amount = Column(Float)
    charged = Column(Float)
    to_receive = Column(Float)
    date_time = Column(DateTime)
    method = Column(String(30))
    status = Column(Integer)
    remarks = Column(String(30))
    member_id = Column(Integer, ForeignKey("Members.Member_id", onupdate='CASCADE',  ondelete="CASCADE"))

    member = relationship('Member', back_populates='withdrawals', passive_deletes=True)


#Deposits Model
class Deposit(Base):
    __tablename__ = "Deposits"

    id = Column(Integer, primary_key=True, index=True)
    transaction_code = Column(String(30), unique=True, index=True)
    member_id = Column(Integer, ForeignKey("Members.Member_id", onupdate='CASCADE',  ondelete="CASCADE"))
    deposit_amount = Column(Float)
    currency_id = Column(Integer, ForeignKey("Currency_Supported.currency_id", onupdate='CASCADE',  ondelete="CASCADE"))
    date_time = Column(DateTime)
    gateway_id = Column(Integer, ForeignKey("Gateway.gateway_id", onupdate='CASCADE',  ondelete="CASCADE"))
    status_id =  Column(Integer, ForeignKey("Deposit_Status.status_id", onupdate='CASCADE',  ondelete="CASCADE"))
    

    member = relationship("Member", back_populates="deposits", passive_deletes=True)
    currency_supported = relationship("Currency_supported", back_populates="deposits", passive_deletes=True)
    gateway = relationship("gateway", back_populates="deposits", passive_deletes=True)
    status = relationship("Deposit_status", back_populates="deposits", passive_deletes=True)



#Deposits status model
class Deposit_status(Base):
    __tablename__ = "Deposit_Status"
    
    status_id = Column(Integer, primary_key=True, index=True)
    status = Column(Integer)
    remarks = Column(String(40))

    deposits = relationship("Deposit", back_populates="status", passive_deletes=True)

#Gateway Model
class gateway(Base):
    __tablename__ = "Gateway"
    
    gateway_id = Column(Integer , primary_key= True , index=True )
    gateway_name =Column(String(25))
    gateway_status =Column(Boolean , default=False)
    gateway_type =Column(String(30))

    deposits = relationship("Deposit", back_populates="gateway", passive_deletes=True)


class TransactionLog(Base):
    __tablename__ = 'Transaction_Logs'

    transaction_log_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("Members.Member_id", onupdate='CASCADE', ondelete="CASCADE"))
    transaction_type = Column(Integer)
    amount = Column(Float)
    status = Column(Integer)

    member = relationship('Member', back_populates='transaction_logs', passive_deletes=True)
