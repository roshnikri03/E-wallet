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
