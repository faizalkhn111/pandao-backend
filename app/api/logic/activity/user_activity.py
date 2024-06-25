import uuid

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.api.forms.blueprint import DeployCommunity
# from app.api.forms.blueprint import DeployCommunity
from models import dbsession as conn, BluePrint, Community as Com, User, Participants, UserActivity, UserMetaData
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.exc import SQLAlchemyError

from pydantic import BaseModel
from typing import List


class UserActivityModel(BaseModel):
    transaction_id: str
    user_address: str
    name: str
    image_url: str


def get_user_activity(community_id: uuid):
    try:
        response = []
        results = (conn.query(
            UserActivity.transaction_id,
            UserActivity.user_address,
            User.name,
            UserMetaData.image_url,
            UserActivity.transaction_info
        ).join(
            User, UserActivity.user_address == User.public_address
        ).join(
            UserMetaData, User.public_address == UserMetaData.user_address
        ).filter(
            UserActivity.community_id == community_id
        ).all())
        for data in results:
            activity = {
                'tx_id': data[0],
                'user_address': data[1],
                'user_name': data[2],
                'user_image_url': data[3],
                'info': data[4],
            }
            response.append(activity)
        return response

    except SQLAlchemyError as e:
        # Log the error e
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
