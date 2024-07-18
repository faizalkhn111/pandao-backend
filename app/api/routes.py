import uuid

from fastapi import FastAPI
from starlette import status

from .forms.blueprint import DeployCommunity
from .forms.community import CommunityParticipant, CommunityComment
from .forms.transaction_manifest import TransactionSubmit
# from .forms.blueprint import DeployCommunity
from .logic import health as health_handler
from .logic.activity.user_activity import get_user_activity, UserActivityModel, get_community_activity
from .logic.auth.users import user_login_req, user_sign_up, check_user_exist, get_user_detail, update_user_profile
from .logic.blueprint import add_blueprint as add_blueprint_logic
from .forms import *
from .logic.blueprint.blueprint import get_all_blueprints, get_blueprint

from .logic.community import get_community
from .logic.community.community import create_community, get_user_community, check_user_community_status, \
    user_participate_in_community, get_community_participants, get_community_comments, add_community_comment, \
    get_single_community, get_community_metadata_details, get_community_tokens, get_community_active_proposal
from .logic.event_listener import token_bucket_deploy_event_listener
from .utils.presignsignature import generate_signature


def load_server(app):
    # defines routes

    @app.get('/')
    def health_check():
        return health_handler()

    @app.get("/image-upload/signature", tags=(['presign-url']))
    def get_image_upload_signature_route():
        return generate_signature()

    # api for user to register
    @app.post('/user/signup', status_code=status.HTTP_201_CREATED, tags=(['user-auth']))
    def user_signup_route(req: UserSignupForm):
        return user_sign_up(req)

    @app.get('/user/activity', status_code=status.HTTP_201_CREATED, tags=(['user-auth']))
    def get_user_activity_route(user_address: str, page: int = 1, page_size: int = 10):
        return get_user_activity(user_address, page, page_size)

    @app.get('/user/check-signup/{public_address}', status_code=status.HTTP_200_OK, tags=(['user-auth']))
    def user_check_signup_route(public_address: str):
        return check_user_exist(public_address)

    @app.get('/user/details/{public_address}', status_code=status.HTTP_200_OK, tags=(['user-detail']))
    def get_user_details_route(public_address: str):
        return get_user_detail(public_address)

    @app.patch('/user/update-user', status_code=status.HTTP_200_OK, tags=(['user-detail']))
    def update_user_route(req: UserProfileUpdate):
        return update_user_profile(req)

    @app.post('/user/login', status_code=status.HTTP_201_CREATED, tags=(['user-auth']))
    def register(req: UserLogin):
        return user_login_req(req)

    # define routes for blueprints

    @app.post('/blueprint', summary="add a blueprint ", description="add blue print by admin", tags=(['blue-print']))
    def add_blueprint_route(req: BlurPrintForm):
        add_blueprint_logic(req)

    @app.get('/blueprint', summary="get all blueprint on the platform", tags=(['blue-print']))
    def get_all_blueprint_route():
        return get_all_blueprints()

    @app.get('/blueprint/{slug}', summary="get a blueprint detail on the platform", tags=(['blue-print']))
    def get_all_blueprint_route(slug: str):
        return get_blueprint(slug)

    @app.get('/community', summary="get communities of the platform ", description="get communities of platform",
             tags=(['community']))
    def get_community_route():
        return get_community()

    @app.get('/community/{user_addr}', summary="get communities iof user ",
             description="get communities of user", tags=(['community']))
    def get_community_user_route(user_addr: str):
        return get_user_community(user_addr)

    # @app.post('/community/deploy', summary="send this to server after deploying a community",
    #           description="send this to server after deploying a community")
    # def deploy_token_weighted_dao(req:DeployCommunity):
    #     return create_community(req)
    @app.post('/submit-tx', summary="submits a transaction on the platform",
              description="submits a transaction on the platform")
    def callme(req: TransactionSubmit):
        return token_bucket_deploy_event_listener(req.tx_id, req.user_address)

    ## routes related to activity
    @app.get('/activity/{community_id}', summary='get all the activity on the platform',
             description="get all the activity on the platform", tags=(['user-activity ']))
    def get_activity_route(community_id: uuid.UUID):
        return get_community_activity(community_id)

    @app.get('/community/check/user_status', summary="check if user is participant of community", tags=(['community']))
    def check_user_community_status_route(user_addr: str, community_id: uuid.UUID):
        return check_user_community_status(user_addr, community_id)

    # @app.get('/community/{user_addr}', summary="get communities of the platform ",
    #          description="get communities of platform")
    # def get_community_user_route(user_addr: str):
    #     return get_user_community(user_addr)

    @app.post('/community/participant', summary="user join a community", tags=(['community']))
    def join_community(req: CommunityParticipant):
        return user_participate_in_community(req.participant_address, req.community_id)

    @app.get('/community/participant/{c_id}', summary="user join a community", tags=(['community']))
    def get_community_participant_route(c_id: uuid.UUID):
        return get_community_participants(c_id)

    @app.get('/community/comments/{c_id}', summary="get comments of user community", tags=(['community']))
    def get_community_route(c_id: uuid.UUID):
        return get_community_comments(c_id)

    @app.post('/community/comment', summary='add comment on community', tags=(['community']))
    def add_community_comment_route(req: CommunityComment):
        return add_community_comment(req)

    @app.get('/community/detail/{c_id}', summary="get community detail", tags=(['community']))
    def get_community_detail_route(c_id: uuid.UUID):
        return get_single_community(c_id)

    @app.get('/community/detail/metadata/{c_id}', summary="get community detail", tags=(['community']))
    def get_community_metadata_route(c_id: uuid.UUID):
        return get_community_metadata_details(c_id)

    @app.get('/community/token/{c_id}', summary="get community tokens holder details", tags=(['community']))
    def get_community_token_route(c_id: uuid.UUID):
        return get_community_tokens(c_id)

    @app.get('/community/proposal/active/{c_id}', summary="get community active proposal", tags=(['community']))
    def get_community_token_route(c_id: uuid.UUID):
        return get_community_active_proposal(c_id)
