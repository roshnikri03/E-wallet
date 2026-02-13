from sqlalchemy.orm import Session
from models import Member
from schemas import MemberCreate, MemberUpdate
from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
import sys
sys.path.append(r'D:/API ENV/crud.py') 
import schemas,models
from pymysql.err import IntegrityError # type: ignore



#crud operations for user 
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists")
    return db_user


def read_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def read_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = user.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return  {"message":"User Updated Successfully"}

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    db.refresh(db_user)
    return  {"message":"User deleted Successfully"}


#crud operations for members

def create_member(db: Session, member: schemas.MemberCreate):
    db_member = models.Member(**member.dict())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member



def get_member(db: Session, member_id: int):
    return db.query(Member).filter(Member.Member_id == member_id).first()

def get_members(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Member).offset(skip).limit(limit).all()


def update_member(db: Session, member_id: int, member_update: MemberUpdate):
    member = db.query(Member).filter(Member.Member_id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    update_data = member_update.dict(exclude_unset=True)
    db.query(Member).filter(Member.Member_id == member_id).update(update_data)
    db.commit()
    db.refresh(member)
    return  {"message":"Member updated Successfully"}



def delete_member(db: Session, member_id: int):
    member = db.query(models.Member).filter(models.Member.Member_id == member_id).first()
    if member:
        db.delete(member)
        db.commit()
        return  {"message":"Member deleted Successfully"}
    

#CRUD operations for Country_Info

def create_country_info(db: Session, country_info: schemas.add_country):
    db_country_info = models.Country_Info(**country_info.dict())
    db.add(db_country_info)
    db.commit()
    db.refresh(db_country_info)
    return db_country_info

def get_country_info(db: Session, country_id: int):
    return db.query(models.Country_Info).filter(models.Country_Info.Country_Id == country_id).first()


# def get_deposit_statuses(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Deposit_status).offset(skip).limit(limit).all()
def get_all_country_info(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Country_Info).offset(skip).limit(limit).all()

def update_country_info(db: Session, country_id: int, country_info: schemas.update_country):
    db_country_info = db.query(models.Country_Info).filter(models.Country_Info.Country_Id == country_id).first()
    if db_country_info:
        for attr, value in country_info.dict().items():
            setattr(db_country_info, attr, value)
        db.commit()
        db.refresh(db_country_info)
    return db_country_info

def delete_country_info(db: Session, country_id: int):
    db_country_info = db.query(models.Country_Info).filter(models.Country_Info.Country_Id == country_id).first()
    if db_country_info:
        db.delete(db_country_info)
        db.commit()
    return db_country_info
