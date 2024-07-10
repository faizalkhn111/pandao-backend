from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.api.forms.transaction_manifest import DeployTokenWeightedDao, BuyTokenWeightedDaoToken, DeployProposal, \
    ProposalVote
from models import Community, Participants, Proposal, CommunityToken
from models import dbsession as conn


def transaction_manifest_routes(app):
    @app.post('/manifest/build/deploy_token_weighted_dao', tags=(['manifest_builder']))
    def build_token_weight_deploy_manifest(req: DeployTokenWeightedDao):
        organization_name = req.communityName
        token_supply = req.tokenSupply
        token_price = req.tokenPrice
        token_withdraw_price = req.tokenWithDrawPrice
        organization_image = req.communityImage
        organization_token_image = req.tokenImage
        description = req.description
        user_account = req.userAddress
        manifest = command_string = (
            f'CALL_FUNCTION\n'
            f'Address("package_tdx_2_1p4hvprlpzwnztl370lpg9yxvw6d3r6jaz0nf6pth75s9r7wmzzrcsy")\n'
            f'"TokenWeigtedDao"\n'
            f'"initiate"\n'
            f'"{organization_name}"\n'
            f'{token_supply}i32\n'
            f'0u8\n'
            f'Decimal("{token_price}")\n'
            f'Decimal("{token_withdraw_price}")\n'
            f'"{organization_image}"\n'
            f'"{organization_token_image}"\n'
            f'"{description}"\n'
            f';\n'
            f'CALL_METHOD\n'
            f'    Address("{user_account}")\n'
            f'    "deposit_batch"\n'
            f'    Expression("ENTIRE_WORKTOP")\n'
            f';'
        )
        return manifest

    @app.post('/manifest/build/buy_token/token_weighted_dao', tags=(['manifest_builder']))
    def buy_token_token_weighted_dao(req: BuyTokenWeightedDaoToken):
        try:
            community = conn.query(Community).filter(Community.id == req.community_id).first()
            account_address = req.userAddress
            XRD_take = req.tokenSupply + community.token_price
            community_address = community.component_address
            token_take = req.tokenSupply
            does_user_exist = conn.query(Participants).filter(Participants.community_id == community.id,
                                                              Participants.user_addr == account_address).first()
            if not does_user_exist:
                raise HTTPException(status_code=401, detail="not a community participant")

            transaction_string = f"""
        CALL_METHOD
            Address("{account_address}")
            "withdraw"
            Address("resource_tdx_2_1tknxxxxxxxxxradxrdxxxxxxxxx009923554798xxxxxxxxxtfd2jc")
            Decimal("{XRD_take}")
        ;

        TAKE_FROM_WORKTOP
            Address("resource_tdx_2_1tknxxxxxxxxxradxrdxxxxxxxxx009923554798xxxxxxxxxtfd2jc")
            Decimal("{XRD_take}")
            Bucket("bucket1")
        ;

        CALL_METHOD
        Address("{community_address}")
        "obtain_token"
        Bucket("bucket1")
        Decimal("{token_take}")
        ;

        CALL_METHOD
            Address("{account_address}")
            "deposit_batch"
            Expression("ENTIRE_WORKTOP")
        ;
        """
            return transaction_string

        except SQLAlchemyError as e:
            # Log the error e
            print(e)
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @app.post('/manifest/build/sell_token/token_weighted_dao', tags=(['manifest_builder']))
    def sell_token_token_weighted_dao(req: BuyTokenWeightedDaoToken):
        try:
            community = conn.query(Community).filter(Community.id == req.community_id).first()
            account_address = req.userAddress
            XRD_take = req.tokenSupply
            community_address = community.component_address
            token_address = community.token_address
            token_take = req.tokenSupply

            transaction_string = f"""
           CALL_METHOD
               Address("{account_address}")
               "withdraw"
               Address("{token_address}")
               Decimal("{XRD_take}")
           ;

           TAKE_FROM_WORKTOP
               Address("{token_address}")
               Decimal("{XRD_take}")
               Bucket("bucket1")
           ;

           CALL_METHOD
               Address("{community_address}")
               "withdraw_power"
               Bucket("bucket1")
           ;

           CALL_METHOD
               Address("{account_address}")
               "deposit_batch"
               Expression("ENTIRE_WORKTOP")
           ;
           """
            return transaction_string

        except SQLAlchemyError as e:
            # Log the error e
            print(e)
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @app.post('/manifest/build/praposal', tags=(['manifest_builder']))
    def sell_token_token_weighted_dao(req: DeployProposal):
        try:
            community = conn.query(Community).filter(Community.id == req.community_id).first()
            # check if there is any ongoing proposal
            proposal = conn.query(Proposal).filter(Proposal.community_id == req.community_id,
                                                   Proposal.is_active == True).first()
            if proposal:
                raise HTTPException(status_code=401, detail="there is already a active proposal")

            start_time = req.start_time
            end_time = req.end_time
            account_address = req.userAddress
            end_time_unix = int(end_time)  # Convert string to integer Unix timestamp
            end_time_dt = datetime.utcfromtimestamp(end_time_unix)

            # Extract year, month, day, hour, minute, second
            end_year = end_time_dt.year
            end_month = end_time_dt.month
            end_day = end_time_dt.day
            end_hour = end_time_dt.hour
            end_minute = end_time_dt.minute
            end_second = end_time_dt.second

            start_time_unix = int(start_time)  # Convert string to integer Unix timestamp
            start_time_dt = datetime.utcfromtimestamp(start_time_unix)

            # Extract year, month, day, hour, minute, second
            start_year = start_time_dt.year
            start_month = start_time_dt.month
            start_day = start_time_dt.day
            start_hour = start_time_dt.hour
            start_minute = start_time_dt.minute
            start_second = start_time_dt.second

            transaction_string = f"""
                                    
                                    CALL_METHOD
                                    Address("{account_address}")
                                    "create_proof_of_amount"
                                    Address("{community.owner_token_address}")
                                    Decimal("1")
                                    ;
                                    CALL_METHOD
                                    Address("{community.component_address}")
                                    "create_praposal"
                                    "{req.proposal}"
                                    {req.minimumquorum}u8
                                    Tuple(
                                    {start_year}u32 ,
                                    {start_month}u8 ,
                                    {start_day}u8 ,
                                    {start_hour}u8 ,
                                    {start_minute}u8 ,
                                    {start_second}u8)
                                    Tuple(
                                   {end_year}u32 ,
                                    {end_month}u8 ,
                                    {end_day}u8 ,
                                    {end_hour}u8 ,
                                    {end_minute}u8 ,
                                    {end_second}u8)
                                    ;
            """
            return transaction_string

        except SQLAlchemyError as e:
            # Log the error e
            print(e)
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @app.post('/manifest/proposal/vote', tags=(['manifest_builder']))
    def vote_in_proposal(req: ProposalVote):
        proposal = conn.query(Proposal).filter(Proposal.proposal_address == req.proposal_address).first()
        community_id = proposal.community_id
        user_token = conn.query(CommunityToken).filter(CommunityToken.community_id == community_id, CommunityToken.user_address == req.userAddress).first()
        token_supply = user_token.token_owned
        return {}
