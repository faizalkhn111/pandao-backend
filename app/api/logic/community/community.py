import uuid

import requests
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.api.forms.blueprint import DeployCommunity
from app.api.forms.community import CommunityComment
# from app.api.forms.blueprint import DeployCommunity
from models import dbsession as conn, BluePrint, Community as Com, User, Participants, UserMetaData, CommunityComments, \
    UserActivity, Community
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


class CommunityParticipant:
    pass


def user_participate_in_community(user_addr: str, community_id: uuid.UUID):
    try:
        # create new user participant
        participant = Participants(
            user_addr=user_addr,
            community_id=community_id,

        )
        conn.add(participant)
        conn.commit()

        community = conn.query(Community).filter(Community.id == community_id).first()
        community_name = community.name
        # add comment activity
        activity = UserActivity(
            transaction_id="",
            transaction_info=f'participated in {community_name}',
            user_address=user_addr
        )

    except IntegrityError as e:
        conn.rollback()
        print(f"Integrity error occurred: {e}")
        raise HTTPException(status_code=400,
                            detail="Integrity error: possibly duplicate entry or foreign key constraint.")

    except SQLAlchemyError as e:
        conn.rollback()
        print(f"SQLAlchemy error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    except Exception as e:
        conn.rollback()
        print(f"Unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


def get_community_participants(community_id: UUID):
    result = (
        conn.query(User.public_address, User.name, UserMetaData.image_url)
        .join(UserMetaData, User.public_address == UserMetaData.user_address)
        .join(Participants, Participants.user_addr == User.public_address)
        .filter(Participants.community_id == community_id)
        .all()
    )

    res = []
    for data in result:
        pa, un, dp = data
        res.append(
            {
                "participant": pa,
                "name": un,
                "image_url": dp,
            }
        )

    return res


def check_user_community_status(user_addr: str, community_id: uuid.UUID):
    try:
        user_data = conn.query(CommunityParticipant).filter(CommunityParticipant.community_id == community_id,
                                                            CommunityParticipant.participant == user_addr).first()
        if user_data is None:
            return {
                "user_participated": False
            }
        else:
            return {
                "user_participated": True
            }
    except IntegrityError as e:
        conn.rollback()

        raise HTTPException(status_code=400,
                            detail="Integrity error: possibly duplicate entry or foreign key constraint.")

    except SQLAlchemyError as e:
        conn.rollback()

        raise HTTPException(status_code=500, detail="Internal Server Error")

    except Exception as e:
        conn.rollback()

        raise HTTPException(status_code=500, detail="Internal Server Error")


def get_community_comments(c_id: uuid.UUID):
    # Join the tables
    results = conn.query(CommunityComments.comment, User.name, UserMetaData.image_url, User.public_address).join(User,
                                                                                                                 CommunityComments.commented_by == User.public_address).join(
        UserMetaData, User.public_address == UserMetaData.user_address).filter(
        CommunityComments.community_id == c_id).all()

    # Format the response
    comments = [
        {
            "comment": row.comment,
            "user_name": row.name,
            "user_image": row.image_url,
            "user_address": row.public_address,
        }
        for row in results
    ]

    return comments


def get_single_community(community_id: uuid.UUID):
    communities = conn.query(Com).first()
    return communities


def add_community_comment(req: CommunityComment):
    try:
        c_id = req.community_id
        u_adr = req.user_addr
        c = req.comment

        new_comment = CommunityComments(
            community_id=c_id,
            commented_by=u_adr,
            comment=c
        )
        # get user data and community data
        community = conn.query(Community).filter(Community.id == c_id).first()
        community_name = community.name
        # add comment activity
        activity = UserActivity(
            transaction_id="",
            transaction_info=f'commented in {community_name}',
            user_address=u_adr
        )
        conn.add(new_comment)
        conn.add(activity)
        conn.commit()

    except IntegrityError as e:
        conn.rollback()

        raise HTTPException(status_code=400,
                            detail="Integrity error: possibly duplicate entry or foreign key constraint.")

    except SQLAlchemyError as e:
        conn.rollback()

        raise HTTPException(status_code=500, detail="Internal Server Error")

    except Exception as e:
        conn.rollback()

        raise HTTPException(status_code=500, detail="Internal Server Error")


def get_community_metadata_details(community_id: uuid.UUID):
    try:
        # https://babylon-stokenet-gateway.radixdlt.com/state/entity/details
        # get community component address
        community = conn.query(Community).filter(Community.id == community_id).first()
        url = "https://babylon-stokenet-gateway.radixdlt.com/state/entity/details"

        # Define the JSON data
        data = {
            "addresses": [community.component_address],
            "aggregation_level": "Vault",
            "opt_ins": {
                "ancestor_identities": False,
                "component_royalty_vault_balance": False,
                "explicit_metadata": [],
                "non_fungible_include_nfids": True,
                "package_royalty_vault_balance": False
            }
        }

        # Make the request
        tokens = {}

        response = requests.post(url, json=data)
        response = response.json()
        for data in response['items']:
            print(data)


    finally:
        pass