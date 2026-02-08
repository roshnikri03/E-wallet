from fastapi import FastAPI,HTTPException,Query,Depends,status,Response
from typing import Optional,List
import mysql.connector
import time
from database import Base,engine,SessionLocal
from models import User
#from . import models,schemas
from sqlalchemy.orm import Session
from pydantic import ValidationError
from sqlalchemy import text

import sys
sys.path.append(r'D:/API ENV/main.py')
import models , schemas , crud
from crud import create_user, read_users, read_user, update_user, delete_user
models.Base.metadata.create_all(bind=engine)
from sqlalchemy import func

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

while True:
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            port="3306",
            user="root",
            password="naJL9!2d",
            database="Digital_Wallet"
        )
        print("Connected")
        break


    except Exception as error:
        print("Connection Failed")
        print("Error", error)
        time.sleep(2)


mycursor = mydb.cursor()


@app.post("/users/", response_model=schemas.UserBase)
def create_user_api(user: schemas.UserCreate, db: Session = Depends(get_db)):
     db_user = create_user(db=db, user=user)
     return schemas.UserBase.from_orm(db_user)

# get all users
@app.get("/users/", response_model=List[schemas.User])
def read_users_api(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = "SELECT * FROM Users"
    mycursor.execute(query, {"limit": limit, "skip": skip})
    users = mycursor.fetchall()
    return [
        schemas.User(
            id=user[0],
            username=user[1],
            password=user[2],
            complete_name=user[3],
            email_address=user[4]
        )
        for user in users
    ]


# get a specific user by id
@app.get("/users/{user_id}", response_model=schemas.User)
def read_user_api(user_id: int, db: Session = Depends(get_db)):
    query = "SELECT * FROM Users WHERE id = %s"
    mycursor.execute(query, (user_id,))
    user = mycursor.fetchone()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.User(
        id=user[0],
        username=user[1],
        password=user[2],
        complete_name=user[3],
        email_address=user[4]
    )


#update a user by id

@app.put("/users/{user_id}")
def update_user_api(user_id: int, user:schemas.UserUpdate , db: Session = Depends(get_db)):
    query = text("UPDATE users SET username = :username, password = :password, complete_name = :complete_name, email_address = :email_address WHERE id = :id")
    values = {
        "id": user_id,
        "username": user.username,
        "password": user.password,
        "complete_name": user.complete_name,
        "email_address": user.email_address,
    }
    db.execute(query, values)
    db.commit()
    return {"message": "User updated successfully"}

@app.delete("/users/{user_id}")
def delete_user_api(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}

#CRUD operations for Member entity
#create a new member

@app.post("/members/", response_model=schemas.Member)
def create_member_api(member: schemas.MemberCreate, db: Session = Depends(get_db)):
    try:
        processed_by_id = member.processed_by_id
        print(processed_by_id)
        return crud.create_member(db=db, member=member)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    
#getting All members

@app.get("/members/", response_model=List[schemas.Member])
def read_members_api(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = "SELECT * FROM Members"
    mycursor.execute(query, {"limit": limit, "skip": skip})
    members = mycursor.fetchall()
    return [
        schemas.Member(
            Member_id=row[0],
            First_name=row[1],
            Middle_name=row[2],
            Last_name=row[3],
            Email=row[4],
            Country_Id=row[5],
            Contact_Number=row[6],
            username=row[7],
            password=row[8],
            account_status=row[9],
            processed_by_id =row[10]
        )
        for row in members
    ]
  

# get a specific member by id
@app.get("/members/{member_id}", response_model=schemas.Member)
def read_member_api(member_id: int, db: Session = Depends(get_db)):
    query = "SELECT * FROM Members WHERE Member_id = %s"
    mycursor.execute(query, (member_id,))
    member = mycursor.fetchone()
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return schemas.Member(
           Member_id=member[0],
            First_name=member[1],
            Middle_name=member[2],
            Last_name=member[3],
            Email=member[4],
            Country_Id=member[5],
            Contact_Number=member[6],
            username=member[7],
            password=member[8],
            account_status=member[9],
            processed_by_id =member[10]
        )
    

@app.put("/members/{member_id}", response_model=schemas.Member)
def update_member_api(member_id: int, member_update: schemas.MemberUpdate, db: Session = Depends(get_db)):
    query = text("""
        UPDATE members 
        SET First_name = :first_name, 
            Last_name = :last_name,
            Email = :email,
            Country_ID = :country_id,
            Contact_Number = :contact_number,
            username = :username,
            password = :password,
            account_status = :account_status,
            processed_by_id = :processed_by_id
        WHERE Member_id = :member_id
    """)

    values = {
        "member_id": member_id,
        "first_name": member_update.First_name,
        "last_name": member_update.Last_name,
        "email": member_update.Email,
        "country_id": member_update.Country_Id,
        "contact_number": member_update.Contact_Number,
        "username": member_update.username,
        "password": member_update.password,
        "account_status": member_update.account_status,
        "processed_by_id": member_update.processed_by_id
    }

    db.execute(query, values)
    db.commit()

    updated_member = crud.get_member(db, member_id=member_id)
    if updated_member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    return updated_member
# delete a member by id`

@app.delete("/members/{member_id}")
def delete_member_api(member_id: int, db: Session = Depends(get_db)):
    db_member = crud.get_member(db, member_id=member_id)
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    crud.delete_member(db=db, member_id=member_id)
    return {"message": "Member deleted successfully"}

#creating a new currrency
@app.post("/country_info/", response_model=schemas.Country_Info)
def create_country_info(country_info: schemas.add_country, db: Session = Depends(get_db)):
    try:
        return crud.create_country_info(db=db, country_info=country_info)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))



@app.get("/country_info/{country_id}", response_model=schemas.Country_Info)
def read_country_info(country_id: int, db: Session = Depends(get_db)):
    db_country_info = crud.get_country_info(db=db, country_id=country_id)
    if db_country_info is None:
        raise HTTPException(status_code=404, detail="Country info not found")
    return db_country_info

@app.get("/country_info/", response_model=list[schemas.Country_Info])
def read_all_country_info(db: Session = Depends(get_db)):
    return crud.get_all_country_info(db=db)

@app.put("/country_info/{country_id}", response_model=schemas.Country_Info)
def update_country_info(country_id: int, country_info: schemas.update_country, db: Session = Depends(get_db)):
    db_country_info = crud.update_country_info(db=db, country_id=country_id, country_info=country_info)
    if db_country_info is None:
        raise HTTPException(status_code=404, detail="Country info not found")
    return db_country_info

@app.delete("/country_info/{country_id}", response_model=schemas.Country_Info)
def delete_country_info(country_id: int, db: Session = Depends(get_db)):
    db_country_info = crud.delete_country_info(db=db, country_id=country_id)
    if db_country_info is None:
        raise HTTPException(status_code=404, detail="Country info not found")
    return db_country_info
# API's for operations of currency_supported entity

# Adding a New currency 
@app.post("/currency_supported/", response_model=schemas.currency_supported)
def add_currency_api(currency_supported: schemas.add_currency,  db: Session = Depends(get_db)):
    try:
        return crud.add_currency(db=db, currency_supported=currency_supported)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    

    
 #get all currencies
@app.get("/currency_supported/", response_model=List[schemas.currency_supported])
def read_currencies_api(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = "SELECT * FROM Currency_Supported"
    mycursor.execute(query, {"limit": limit, "skip": skip})
    currency = mycursor.fetchall()
    return [
        schemas.currency_supported(
            currency_id=row[0],
            status=row[1],
            USD_equivalent=row[2],
            currency_info_id =row[3],

        )
        for row in currency
    ]
  

    
#corrected
# get a specific currency by id
@app.get("/currency_supported/{currency_id}", response_model=schemas.currency_supported)
def read_currency_api(currency_id: int, db: Session = Depends(get_db)):
    query = "SELECT * FROM Currency_Supported WHERE  currency_id = %s"
    mycursor.execute(query, ( currency_id,))
    currency = mycursor.fetchone()
    if currency is None:
        raise HTTPException(status_code=404, detail="Currency not found")
    return schemas.currency_supported(
            currency_id=currency[0],
            status=currency[1],
            USD_equivalent=currency[2],
            currency_info_id =currency[3],
           
        )

@app.put("/currency_supported/{currency_id}", response_model=schemas.currency_supported)
def update_currency_api(currency_id: int, currency_update: schemas.update_currency, db: Session = Depends(get_db)):
    query = text("""
        UPDATE currency_supported 
        SET 
            status = :status,
            USD_equivalent = :usd_equivalent
        WHERE currency_id = :currency_id
    """)

    values = {
        "currency_id": currency_id,
        "status": currency_update.status,
        "usd_equivalent": currency_update.USD_equivalent,
    }

    db.execute(query, values)
    db.commit()

    updated_currency = crud.get_currency(db, currency_id=currency_id)
    if updated_currency is None:
        raise HTTPException(status_code=404, detail="Currency not found")

    return updated_currency



#to be corrected
@app.delete("/currency_supported/{currency_id}", response_model=schemas.currency_supported)
def delete_currency_api(currency_id: int, db: Session = Depends(get_db)):
    currency_supported = crud.delete_currency_info(db=db,currency_id = currency_id)
    if currency_supported is None:
        raise HTTPException(status_code=404, detail="Currency Supported not found")

    db.delete(currency_supported)
    db.commit()

    # Return a response indicating a successful deletion
    return {"message": "Currency Supported deleted successfully"}

#Api's for currency_info
#Corrected
@app.post("/currency_info/", response_model=schemas.currency_info)
def add_currency_info_api(currency_info: schemas.add_currency_info,  db: Session = Depends(get_db)):
    try:
        return crud.add_currency_info(db=db, currency_info=currency_info)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    

    
 #get all currencies
@app.get("/currency_info/", response_model=List[schemas.currency_info])
def read_currencies_info_api(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = "SELECT * FROM Currency_info"
    mycursor.execute(query, {"limit": limit, "skip": skip})
    currency = mycursor.fetchall()
    return [
        schemas.currency_info(
            currency_info_id=row[0],
            currency_name=row[1],
            currency_symbol=row[2],
          
        )
        for row in currency
    ]
  

    
#corrected
# get a specific currency by id
@app.get("/currecny_info/{currency_info_id}", response_model=schemas.currency_info)
def read_currency_info_api(currency_info_id: int, db: Session = Depends(get_db)):
    query = "SELECT * FROM Currency_info WHERE  currency_info_id = %s"
    mycursor.execute(query, ( currency_info_id,))
    currency = mycursor.fetchone()
    if currency is None:
        raise HTTPException(status_code=404, detail="Currency info not found")
    return schemas.currency_info(
            currency_info_id=currency[0],
            currency_name=currency[1],
            currency_symbol=currency[2],
           
        )

@app.put("/currency_info/{currency_info_id}", response_model=schemas.currency_info)
def update_currency_info_api(currency_info_id: int, currency_info_update: schemas.update_currency_info, db: Session = Depends(get_db)):
    query = text("""
        UPDATE currency_info 
        SET currency_name = :currency_name, 
            currency_symbol = :currency_symbol
        WHERE currency_info_id = :currency_info_id
    """)

    values = {
        "currency_info_id": currency_info_id,
        "currency_name": currency_info_update.currency_name,
        "currency_symbol": currency_info_update.currency_symbol,
    }

    db.execute(query, values)
    db.commit()

    updated_currency_info = crud.get_currency_info(db, currency_info_id= currency_info_id)
    if updated_currency_info is None:
        raise HTTPException(status_code=404, detail="Currency info not found")

    return updated_currency_info

@app.delete("/currency_info/{currency_info_id}", response_model=schemas.currency_info)
def delete_currency_api(currency_info_id: int, db: Session = Depends(get_db)):
    db_currency_info = crud.delete_currency_info(db, currency_info_id=currency_info_id)
    if db_currency_info is None:
        raise HTTPException(status_code=404, detail="Currency info not found")
    return db_currency_info


# API's for operations of currency_supported entity

#APIs for Deposit entity


@app.post("/withdrawals/", response_model=schemas.Withdrawal)
def create_withdrawal(withdrawal: schemas.WithdrawalCreate, db: Session = Depends(get_db)):
    return crud.create_withdrawal(db, withdrawal)


@app.get("/withdrawals/{withdrawal_id}", response_model=schemas.Withdrawal)
def get_withdrawal(withdrawal_id: int, db: Session = Depends(get_db)):
    query = "SELECT * FROM withdrawals WHERE  withdrawal_id = %s"
    mycursor.execute(query, ( withdrawal_id,))
    withdrawal = mycursor.fetchone()
    if  withdrawal is None:
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    return schemas.Withdrawal(
            withdrawal_id= withdrawal[0],
            transaction_code= withdrawal[1],
            amount= withdrawal[2],
            charged= withdrawal[3],
            to_receive= withdrawal[4],
            date_time= withdrawal[5],
            method= withdrawal[6],
            status= withdrawal[7],
            remarks= withdrawal[8],
            member_id= withdrawal[9],
            
        )


@app.get("/withdrawals/", response_model=list[schemas.Withdrawal])
def get_all_withdrawals(db: Session = Depends(get_db)):
    query = "SELECT * FROM withdrawals"
    mycursor.execute(query)
    withdrawal = mycursor.fetchall()
    return [
        schemas.Withdrawal(
            withdrawal_id=row[0],
            transaction_code=row[1],
            amount=row[2],
            charged=row[3],
            to_receive=row[4],
            date_time=row[5],
            method=row[6],
            status=row[7],
            remarks=row[8],
            member_id=row[9],
            
        )
        for row in withdrawal
    ]



#Corrected
@app.put("/withdrawals/{withdrawal_id}", response_model=schemas.Withdrawal)
def update_withdrawal(withdrawal_id: int, withdrawal: schemas.WithdrawalUpdate, db: Session = Depends(get_db)):
    db_withdrawal = db.query(models.Withdrawal).get(withdrawal_id)
    if not db_withdrawal:
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    
    # Update the withdrawal object with the provided data
    db_withdrawal.transaction_code = withdrawal.transaction_code
    db_withdrawal.amount = withdrawal.amount
    db_withdrawal.charged = withdrawal.charged
    db_withdrawal.to_receive = withdrawal.to_receive
    db_withdrawal.date_time = withdrawal.date_time
    db_withdrawal.method = withdrawal.method
    db_withdrawal.status = withdrawal.status
    db_withdrawal.remarks = withdrawal.remarks
    db_withdrawal.member_id = withdrawal.member_id
    
    db.commit()
    db.refresh(db_withdrawal)

    return db_withdrawal

@app.delete("/withdrawals/{withdrawal_id}")
def delete_withdrawal(withdrawal_id: int, db: Session = Depends(get_db)):
    db_withdrawal = crud.get_withdrawal(db, withdrawal_id)
    if db_withdrawal is None:
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    return crud.delete_withdrawal(db, withdrawal_id)

# API's for operations of Deposit entity

# Adding a New Deposit 
@app.post("/Deposit/", response_model=schemas.Deposit)
def add_deposit(deposit: schemas.DepositCreate,  db: Session = Depends(get_db)):
    try:
        return crud.create_deposit(db=db, deposit= deposit)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    
 #get all deposits
@app.get("/Deposit/", response_model=List[schemas.Deposit])
def read_deposits(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = "SELECT * FROM Deposits"
    mycursor.execute(query)
    Deposits = mycursor.fetchall()
    return [
        schemas.Deposit(
            id =row[0],
            transaction_code=row[1],
            member_id=row[2],
            deposit_amount=row[3],
            currency_id =row[4],
            date_time=row[5],
            gateway_id=row[6],
            status_id = row[7],
        )
        for row in Deposits
    ]
# Corrected
# get a specific deposit by id
@app.get("/Deposit/{deposit_id}", response_model=schemas.Deposit)
def read_deposit(deposit_id: int, db: Session = Depends(get_db)):
    query = "SELECT * FROM Deposits WHERE  id = %s"
    mycursor.execute(query, ( deposit_id,))
    deposit = mycursor.fetchone()
    if  deposit  is None:
        raise HTTPException(status_code=404, detail="Deposit not found")
    return schemas.Deposit(
            id = deposit[0],
            transaction_code= deposit[1],
            member_id= deposit[2],
            deposit_amount= deposit[3],
            currency_id = deposit[4],
            date_time= deposit[5],
            gateway_id= deposit[6],
            status_id = deposit[7],
        )

# update a deposit by id
@app.put("/Deposit/{deposit_id}", response_model=schemas.Deposit)
def update_deposit(deposit_id: int, deposit_update: schemas.DepositUpdate, db: Session = Depends(get_db)):
    query = text("""
        UPDATE Deposits 
        SET transaction_code = :transaction_code, 
            deposit_amount = :deposit_amount,
            date_time = :date_time
        WHERE id = :deposit_id
    """)

    values = {
        "deposit_id": deposit_id,
        "transaction_code": deposit_update.transaction_code,
        "deposit_amount": deposit_update.deposit_amount,
        "date_time": deposit_update.date_time,
    }

    db.execute(query, values)
    db.commit()

    updated_deposit = crud.get_deposit(db, deposit_id)
    if updated_deposit is None:
        raise HTTPException(status_code=404, detail="Deposit not found")

    return updated_deposit

#Corrected
 
# delete a deposit by id
@app.delete("/Deposit/{deposit_id}", response_model=schemas.Deposit)
def delete_deposit(deposit_id: int, db: Session = Depends(get_db)):
    db_deposit = crud.delete_deposit(db, deposit_id =deposit_id)
    if db_deposit is None:
        raise HTTPException(status_code=404, detail="deposit not found")
    return db_deposit


 #API's to for deposit status
@app.post("/Deposit_status/", response_model=schemas.deposit_status)
def add_deposit_status(deposit: schemas.add_deposit_status,  db: Session = Depends(get_db)):
    try:
        return crud.create_deposit_status(db=db, deposit= deposit)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    

    
 #get all deposits
@app.get("/Deposit_status/", response_model=List[schemas.deposit_status])
def read_statuses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = "SELECT * FROM Deposit_Status"
    mycursor.execute(query)
    Deposits = mycursor.fetchall()
    return [
        schemas.deposit_status(
            status_id =row[0],
            status=row[1],
            remarks =row[2],
        )
        for row in Deposits
    ]
# Corrected
# get a specific deposit by id
@app.get("/Deposit_status/{status_id}", response_model=schemas.deposit_status)
def read_deposit_status(status_id: int, db: Session = Depends(get_db)):
    query = "SELECT * FROM  Deposit_Status WHERE  status_id = %s"
    mycursor.execute(query, ( status_id,))
    deposit = mycursor.fetchone()
    if  deposit  is None:
        raise HTTPException(status_code=404, detail="Status not found")
    return schemas.deposit_status(
            status_id = deposit[0],
            status= deposit[1],
            remarks = deposit[2],
            
            
        )
# TO BE corrected
@app.put("/Deposit_status/{status_id}", response_model=schemas.deposit_status)
def update_deposit_status(status_id: int, status_update: schemas.update_status, db: Session = Depends(get_db)):
    query = text("""
        UPDATE  Deposit_Status
        SET   status = :status,
            remarks = :remarks
        WHERE status_id = :status_id
    """)

    values = {
        "status_id": status_id,
        "status": status_update.status,
        "remarks": status_update.remarks,
    }

    db.execute(query, values)
    db.commit()

    updated_deposit = crud.get_deposit(db, status_id)
    if updated_deposit is None:
        raise HTTPException(status_code=404, detail="Status not found")

    return updated_deposit


# delete a deposit by id
@app.delete("/Deposit_status/{status_id}", response_model=schemas.deposit_status)
def delete_deposit_status(status_id: int, db: Session = Depends(get_db)):
    db_deposit = crud.delete_deposit_status(db, status_id = status_id)
    if db_deposit is None:
        raise HTTPException(status_code=404, detail=" Status not found")
    return db_deposit  




# API's for operations of Gateway entity
# Adding a New Gateway 
@app.post("/Gateway/", response_model=schemas.gateway)
def add_gateway_api(gateway: schemas.add_gateway,  db: Session = Depends(get_db)):
    try:
        return crud.add_gateway(db=db, gateway=gateway)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    
 #get all Gateways
@app.get("/Gateway/", response_model=List[schemas.gateway])
def read_gateways_api(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = "SELECT * FROM Gateway"
    mycursor.execute(query)
    gateway = mycursor.fetchall()
    return [
        schemas.gateway(
            gateway_id  =row[0],
            gateway_name=row[1],
            gateway_status=row[2],
            gateway_type=row[3],
        )
        for row in gateway
    ]
    
#Corrected
# get a specific gateway by id
@app.get("/Gateway/{gateway_id}", response_model=schemas.gateway)
def read_gateway_api(gateway_id: int, db: Session = Depends(get_db)):
    query = "SELECT * FROM Gateway WHERE  gateway_id = %s"
    mycursor.execute(query, (gateway_id ,))
    gateway = mycursor.fetchone()
    if  gateway is None:
        raise HTTPException(status_code=404, detail=" Gateway not found")
    return schemas.gateway(
            gateway_id  =gateway[0],
            gateway_name=gateway[1],
            gateway_status=gateway[2],
            gateway_type=gateway[3],
           
        )
#Corrected 
# update a gateway by id
@app.put("/Gateway/{gateway_id}", response_model=schemas.gateway)
def update_gateway_api(gateway_id: int, gateway_update: schemas.update_gateway, db: Session = Depends(get_db)):
    query = text("""
        UPDATE Gateway
        SET gateway_name = :gateway_name,
            gateway_status = :gateway_status,
            gateway_type = :gateway_type
        WHERE gateway_id = :gateway_id
    """)

    values = {
        "gateway_id": gateway_id,
        "gateway_name": gateway_update.gateway_name,
        "gateway_status": gateway_update.gateway_status,
        "gateway_type": gateway_update.gateway_type,
    }

    db.execute(query, values)
    db.commit()

    updated_gateway = crud.get_gateway(db, gateway_id)
    if updated_gateway is None:
        raise HTTPException(status_code=404, detail="Gateway not found")

    return updated_gateway


#Corrected
# # delete a gateway by id
# @app.delete("/Gateway/{gateway_id}", response_model=schemas.gateway)
# def delete_gateway_api(gateway_id: int, db: Session = Depends(get_db)):
#     db_gateway = crud.get_gateway(db, gateway_id= gateway_id)
#     if db_gateway is None:
#         raise HTTPException(status_code=404, detail="gateway not found")
#     return crud.delete_gateway(db=db,gateway_id= gateway_id)  

@app.delete("/Gateway/{gateway_id}", response_model=schemas.gateway)
def delete_gateway_api(gateway_id: int, db: Session = Depends(get_db)):
    db_gateway = crud.get_gateway(db, gateway_id=gateway_id)
    if db_gateway is None:
        raise HTTPException(status_code=404, detail="Gateway not found")
    return crud.delete_gateway(db=db, gateway_id=gateway_id) 

@app.put("/transaction_logs/{transaction_log_id}", response_model=schemas.TransactionLog)
def update_transaction_log(transaction_log_id: int, transaction_log_update: schemas.TransactionLogUpdate, db: Session = Depends(get_db)):
    query = text("""
        UPDATE transaction_logs 
        SET transaction_type = :transaction_type, 
            amount = :amount,
            status = :status
        WHERE transaction_log_id = :log_id
    """)

    values = {
        "log_id": transaction_log_id,
        "transaction_type": transaction_log_update.transaction_type,
        "amount": transaction_log_update.amount,
        "status": transaction_log_update.status,
    }

    db.execute(query, values)
    db.commit()

    updated_transaction_log = crud.get_transaction_log(db, transaction_log_id)
    if updated_transaction_log is None:
        raise HTTPException(status_code=404, detail="Transaction Log not found")

    return {"message":"log updated successfully"}


#APIs for Transaction logs 
@app.post("/transaction_logs/", response_model=schemas.TransactionLog)
def create_transaction_log(transaction_log: schemas.TransactionLogCreate, db: Session = Depends(get_db)):
    return crud.create_transaction_log(db, transaction_log)


@app.get("/transaction_logs/{transaction_log_id}", response_model=schemas.TransactionLog)
def get_transaction_log(transaction_log_id: int, db: Session = Depends(get_db)):
    query = "SELECT * FROM transaction_logs WHERE   transaction_log_id  = %s"
    mycursor.execute(query, (transaction_log_id ,))
    transaction_log = mycursor.fetchone()
    if transaction_log is None:
        raise HTTPException(status_code=404, detail="transaction_log  not found")
    return schemas.TransactionLog(
            transaction_log_id=transaction_log[0],
            member_id=transaction_log[1],
            transaction_type=transaction_log[2],
            amount=transaction_log[3],
            status=transaction_log[4],
 
        )
    


@app.get("/transaction_logs/", response_model=list[schemas.TransactionLog])
def get_all_transaction_logs(db: Session = Depends(get_db)):
    query = "SELECT * FROM transaction_logs"
    mycursor.execute(query)
    transaction_logs = mycursor.fetchall()
    return [
        schemas.TransactionLog(
            transaction_log_id=row[0],
            member_id=row[1],
            transaction_type=row[2],
            amount=row[3],
            status=row[4],

        )
        for row in transaction_logs
    ]

#update transaction log
#need to be corrected
@app.put("/transaction_logs/{transaction_log_id}", response_model=schemas.TransactionLog)
def update_transaction_log(transaction_log_id: int, transaction_log_update: schemas.TransactionLogUpdate,
                          db: Session = Depends(get_db)):
    query = text("""
        UPDATE transaction_logs 
        SET transaction_type = :transaction_type, 
            amount = :amount,
            status = :status
        WHERE transaction_log_id = :log_id
    """)

    values = {
        "log_id": transaction_log_id,
        "transaction_type": transaction_log_update.transaction_type,
        "amount": transaction_log_update.amount,
        "status": transaction_log_update.status,
    }

    db.execute(query, values)
    db.commit()

    updated_transaction_log = crud.update_transaction_log(db, transaction_log_id, transaction_log_update)
    if updated_transaction_log is None:
        raise HTTPException(status_code=404, detail="Transaction Log not found")

    return updated_transaction_log


@app.delete("/transaction_logs/{transaction_log_id}")
def delete_transaction_log(transaction_log_id: int, db: Session = Depends(get_db)):
    db_transaction_log = crud.get_transaction_log(db, transaction_log_id)
    if db_transaction_log is None:
        raise HTTPException(status_code=404, detail="Transaction Log not found")
    return crud.delete_transaction_log(db, transaction_log_id)


@app.get("/members__transaction_status/{member_id}", response_model=schemas.MemberTransactionStatus)
def get_member_transaction_status(member_id: int ,db: Session = Depends(get_db)):

    # Perform the query to retrieve member information and transaction status
    query = db.query(models.Member, func.coalesce(func.sum(models.Deposit.deposit_amount), 0).label("TotalDepositAmount"),
                     func.coalesce(func.sum(models.Withdrawal.amount ), 0).label("TotalWithdrawalAmount")).\
        join(models.Deposit,models.Member.Member_id == models.Deposit.member_id, isouter=True).\
        join(models.Withdrawal, models.Member.Member_id == models.Withdrawal.member_id, isouter=True).\
        filter(models.Member.Member_id == member_id).\
        group_by(models.Member.Member_id,models.Member.username, models.Member.Email).first()
    
    # Check if the query result is None
    if query is None:
        raise HTTPException(status_code=404, detail="Member not found")

    # Calculate the transaction status
    total_deposit_amount = query.TotalDepositAmount
    total_withdrawal_amount = query.TotalWithdrawalAmount
    transaction_status = "Transaction can occur" if total_deposit_amount >= total_withdrawal_amount \
        else "Transaction cannot occur"

    # Prepare the response data
    response_data = {
        "MemberID": query.Member.Member_id,
        "Username": query.Member.username,
        "EmailAddress": query.Member.Email,
        "TotalDepositAmount": total_deposit_amount,
        "TotalWithdrawalAmount": total_withdrawal_amount,
        "TransactionStatus": transaction_status
    }

    db.close()

    return response_data