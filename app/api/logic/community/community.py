import uuid

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.api.forms.blueprint import DeployCommunity
# from app.api.forms.blueprint import DeployCommunity
from models import dbsession as conn, BluePrint, Community as Com, User, Participants
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.exc import SQLAlchemyError

# define models
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class CommunityCreate:
    pass


def get_community():
    try:
        communities = conn.query(Com).all()
        return communities
    except SQLAlchemyError as e:
        # Log the error e
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


def get_user_community(user_addr: str):
    communities = conn.query(Com).join(
        Participants, Com.id == Participants.community_id, isouter=True
    ).filter(
        or_(
            Com.owner_address == user_addr,
            Participants.user_addr == user_addr
        )
    ).all()
    return communities


def create_community(community: DeployCommunity):
    pass
    # try:
    #     # get events emitted from the blueprint
    #     tx_deploy_events = token_bucket_deploy_event_listener(community.tx_id)
    #     # create a new community with data
    #     db_community = Com(
    #         name=community.name,
    #         component_address=tx_deploy_events['component_address'],
    #         token_address=tx_deploy_events['token_address'],
    #         owner_token_address=tx_deploy_events['owner_token_address'],
    #         description=community.description,
    #         owner_address=community.user_address
    #     )
    #
    #     conn.add(db_community)
    #     conn.commit()
    #     conn.refresh(db_community)
    #     return db_community
    # except SQLAlchemyError as e:
    #     # Log the error e
    #     print(e)
    #     raise HTTPException(status_code=500, detail="Internal Server Error")
