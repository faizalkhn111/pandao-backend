import uuid
from uuid import UUID
from pydantic import BaseModel, Field
from typing_extensions import Optional, List
from enum import Enum


class CreateCommunityForm(BaseModel):
    name: str = Field(..., description="name of the community")
    component_address: str = Field(..., description="component address of the community")
    description: str = Field(..., description="description of the community")
    owner_address: str = Field(..., description="owner address of the community")


class CommunityParticipant(BaseModel):
    community_id: uuid.UUID = Field(..., description="community id")
    participant_address: str = Field(..., description="participant id")


class CommunityComment(BaseModel):
    user_addr: str = Field(..., description="user address of the community")
    comment: str = Field(..., description="description of the community")
    community_id: uuid.UUID = Field(..., description="community id")


class ProposalComment(BaseModel):
    user_addr: str = Field(..., description="user address of the community")
    comment: str = Field(..., description="description of the community")
    proposal_id: uuid.UUID = Field(..., description="community id")
