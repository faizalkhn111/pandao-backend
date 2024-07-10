from idlelib.pyparse import trans

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Boolean, Enum, DECIMAL, Float, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum as PYENUM
from typing import List
from typing import Optional
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    name: Mapped[str] = Column(String)
    public_address: Mapped[str] = Column(String(256), primary_key=True)
    last_login: Mapped[DateTime] = Column(DateTime, default=func.now())
    usermetadata: Mapped["UserMetaData"] = relationship("UserMetaData", back_populates="user")


class UserMetaData(Base):
    __tablename__ = 'user_meta_data'
    user_address: Mapped[str] = Column(String, ForeignKey('users.public_address'), primary_key=True)
    about: Mapped[str] = Column(String)
    image_url: Mapped[str] = Column(String)

    user: Mapped["User"] = relationship("User", back_populates="usermetadata")


class UserActivity(Base):
    __tablename__ = 'user_activity'
    transaction_id: Mapped[str] = Column(String, primary_key=True)
    # this contains a basic info about a user transaction in the DAO
    transaction_info: Mapped[str] = Column(String)
    activity_type: Mapped[str] = Column(String)
    community_id = Column(UUID(as_uuid=True))
    user_address: Mapped[str] = Column(String, ForeignKey('users.public_address'))


class BluePrint(Base):
    __tablename__ = 'blueprint'
    slug: Mapped[str] = mapped_column(String, primary_key=True)
    description: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(DECIMAL)
    package_addr = Column(String, nullable=False)
    # define relationships
    terms: Mapped[list["BluePrintTerms"]] = relationship("BluePrintTerms", back_populates="blueprint")


class BluePrintTerms(Base):
    __tablename__ = 'blueprint_terms'
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    term: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    blueprint_slug: Mapped[str] = mapped_column(ForeignKey("blueprint.slug"))
    blueprint: Mapped["BluePrint"] = relationship("BluePrint", back_populates="terms")


class Community(Base):
    __tablename__ = 'community'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(128))
    component_address = Column(String(2048))
    description = Column(String)
    blueprint_slug: Mapped[str] = mapped_column(ForeignKey("blueprint.slug"))
    token_address = Column(String)
    owner_token_address = Column(String)
    image = Column(String)
    token_price = Column(Float)  # Assuming token price is stored as a float
    token_buy_back_price = Column(Float)  # Assuming buy-back price is stored as a float
    total_token = Column(Integer)
    token_bought = Column(Integer)
    owner_address = Column(String, ForeignKey('users.public_address'))
    funds = Column(Float)
    community_comment: Mapped[list['CommunityComments']] = relationship("CommunityComments", back_populates="community")


class Participants(Base):
    __tablename__ = 'participants'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    community_id = Column(UUID(as_uuid=True), ForeignKey('community.id'))
    user_addr = Column(String, ForeignKey('users.public_address'))


class CommunityToken(Base):
    __tablename__ = 'community_token'
    community_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    user_address = Column(String, ForeignKey('users.public_address'), primary_key=True)
    token_owned = Column(Float)


class CommunityComments(Base):
    __tablename__ = 'community_comments'
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    community_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("community.id"))
    commented_by: Mapped[str] = mapped_column(String, ForeignKey("users.public_address"))
    # commented_at: Mapped[DateTime] = Column(DateTime, default=func.now())
    comment: Mapped[str] = mapped_column(String)
    community: Mapped["Community"] = relationship("Community", back_populates="community_comment")


class Proposal(Base):
    __tablename__ = 'proposal'
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proposal: Mapped[str] = mapped_column(String)
    community_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("community.id"))
    voted_for = Column(Float)
    voted_against = Column(Float)
    is_active = Column(Boolean)
    start_time = Column(Integer)
    ends_time = Column(Integer)
    minimum_quorum = Column(Integer)
    proposal_address : Mapped[str] = mapped_column(String)


# Create an engine


engine = create_engine(
    'postgresql://pandao_backend_fw67_user:jPMCLTHyKvp296K7vuC3l0TGhE72gS30@dpg-cpsnpsl6l47c73e9nc2g-a.oregon-postgres.render.com/pandao_backend_fw67')
Base.metadata.create_all(engine)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)



# Create a Session
dbsession = Session()




