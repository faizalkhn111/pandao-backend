import uuid

import requests
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, NoResultFound

from models import Community, dbsession as conn, UserActivity, CommunityToken, Proposal


## pending , add logger

def token_bucket_deploy_event_listener(tx_id: str, user_address: str):
    url = "https://babylon-stokenet-gateway.radixdlt.com/transaction/committed-details"
    data = {
        "intent_hash": tx_id,
        "receipt_events": True,
        "opt_ins": {
            "receipt_events": True
        }
    }

    # Send a POST request with the JSON data
    response = requests.post(url, json=data)

    # Check if the request was successful
    if response.status_code == 200:
        # create an empty dict to strore data
        resources = {}
        metadata = {}
        # Parse the response JSON data
        response_data = response.json()
        # Print the response JSON data

        # Store the response data in a dictionary

        response_data = response_data
        tx_events = response_data['transaction']['receipt']['events']
        # print(tx_events)
        for event in tx_events:
            if event['name'] == 'PandaoEvent':
                for field in event['data']['fields']:
                    print(field['field_name'])
                    if field['field_name'] == 'meta_data':
                        for m_d in field['fields']:
                            for _m_d in m_d['fields']:
                                metadata[_m_d['field_name']] = _m_d['value']


                    else:
                        resources[field['field_name']] = field.get('value') or field.get('variant_name')

        # check the event type of the tx
        try:
            if resources['event_type'] == 'DEPLOYMENT':
                # create a new community
                community_id = uuid.uuid4()
                temp = metadata['community_name']
                community = Community(
                    id=community_id,
                    name=metadata['community_name'],
                    component_address=metadata['component_address'],
                    description=metadata['description'],
                    blueprint_slug='token-weight',
                    token_address=metadata['token_address'],
                    owner_token_address=metadata['owner_token_address'],
                    owner_address=user_address,
                    token_price=metadata['token_price'],
                    token_buy_back_price=metadata['token_buy_back_price'],
                    image=metadata['community_image'],
                    total_token=metadata['total_token'],
                    funds=0,
                    token_bought=0
                )

                # create user activity

                activity = UserActivity(
                    transaction_id=tx_id,
                    transaction_info=f'created  {temp}',
                    user_address=user_address,
                    community_id=community_id
                )
                conn.add(community)
                conn.add(activity)
                conn.commit()
            elif resources['event_type'] == 'TOKEN_BOUGHT':
                # in case of token bought , get community details and add activity
                community_address = resources['component_address']
                # get community names and detail
                community = conn.query(Community).filter(Community.component_address == community_address).first()
                community.funds += float(metadata['amount_paid'])
                community.token_bought += float(metadata['amount'])
                token_bought = float(metadata['amount'])
                try:
                    # Attempt to retrieve the existing row
                    community_token = conn.query(CommunityToken).filter_by(
                        community_id=community.id,
                        user_address=user_address
                    ).one()
                    community_token.token_owned += float(token_bought)
                    conn.commit()


                except NoResultFound:
                    community_token = CommunityToken(
                        community_id=community.id,
                        user_address=user_address,
                        token_owned=float(token_bought)
                    )
                    conn.add(community_token)

                activity = UserActivity(
                    transaction_id=tx_id,
                    transaction_info=f'bought {token_bought} tokens in {community.name}',
                    user_address=user_address,
                    community_id=community.id
                )
                conn.add(activity)
                conn.commit()

            elif resources['event_type'] == 'TOKEN_SELL':
                # in case of token bought , get community details and add activity
                community_address = resources['component_address']
                # get community names and detail
                community = conn.query(Community).filter(Community.component_address == community_address).first()
                community.funds -= float(metadata['amount_paid'])
                community.token_bought -= float(metadata['amount'])
                token_bought = float(metadata['amount'])
                try:
                    # Attempt to retrieve the existing row
                    community_token = conn.query(CommunityToken).filter_by(
                        community_id=community.id,
                        user_address=user_address
                    ).one()
                    community_token.token_owned -= float(token_bought)
                    conn.commit()


                except NoResultFound:
                    pass
                activity = UserActivity(
                    transaction_id=tx_id,
                    transaction_info=f'sold {token_bought} tokens in {community.name}',
                    user_address=user_address,
                    community_id=community.id
                )
                conn.add(activity)
                conn.commit()

                pass
            elif resources['event_type'] == 'PRAPOSAL':
                community_address = resources['component_address']
                # get community names and detail
                community = conn.query(Community).filter(Community.component_address == community_address).first()
                new_proposal = Proposal(
                    proposal=metadata['current_praposal'],
                    community_id=community.id,
                    voted_for=metadata['voted_for'],
                    voted_against=metadata['voted_againt'],
                    is_active=True,
                    start_time=metadata['start_time_ts'],
                    ends_time=metadata['end_time_ts'],
                    minimum_quorum=metadata['minimum_quorum'],
                    proposal_address=metadata['component_address']
                )
                activity = UserActivity(
                    transaction_id=tx_id,
                    transaction_info=f'created a proposal',
                    user_address=user_address,
                    community_id=community.id
                )
                conn.add(activity)
                conn.add(new_proposal)
                conn.commit()
            elif resources['event_type'] == 'VOTE':
                proposal_address = resources['component_address']
                proposal_address = metadata['praposal_address']
                proposal = conn.query(Proposal).filter(Proposal.proposal_address == proposal_address).first()
                vote_againts = metadata['againts']
                print(vote_againts)
                if vote_againts:
                    proposal.voted_against += float(metadata['voting_amount'])
                else:
                    proposal.voted_for += float(metadata['voting_amount'])
                conn.commit()


        except SQLAlchemyError as e:
            print(e)
            conn.rollback()
            # logger.error(f"SQLAlchemy error occurred: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

        return resources

    else:
        print(f"Request failed with status code {response.status_code}")
