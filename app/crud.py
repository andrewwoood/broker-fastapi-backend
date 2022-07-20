# import os
# import boto3
# from dotenv import load_dotenv
# load_dotenv()

from datetime import datetime

from sqlalchemy.orm import Session

from . import models, schemas, utils


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_account(db: Session, account: schemas.AccountCreate):
    name = account.name
    email = account.email
    password = account.password
    hashed_password = password + "notreallyhashed"

    # In order to get the ID and authenticate, use AWS Cognito
    signup_result = utils.cognito_signup(username=email, password=hashed_password)
    id = signup_result.user_id
    access_token = signup_result.access_token
    refresh_token = signup_result.refresh_token

    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    # After getting ID and authenticating, create model and store it in DB
    db_user = models.Account(
        id=id,
        name=name,
        email=email,
        created_at=datetime.now().strftime(DATE_FORMAT),
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    service_result = utils.ServiceResult(db_user, access_token, refresh_token)
    return service_result

# Old one
def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password) # ID must be parameter later
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
