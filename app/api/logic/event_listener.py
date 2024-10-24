import uuid

import requests
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, NoResultFound

from app.api.logic.community.community import generate_random_string
from models import Community, dbsession as conn, UserActivity, CommunityToken, Proposal, Participants, CommunityTags


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
        community_tags = []
        for event in tx_events:
            if event['name'] == 'PandaoEvent':
                for field in event['data']['fields']:
                    print(field['field_name'])
                    if field['field_name'] == 'meta_data':
                        print(field['field_name'])
                        for m_d in field['fields']:
                            for _m_d in m_d['fields']:
                                print(_m_d['field_name'])
                                if _m_d['field_name'] == 'tags':
                                    for tags in _m_d['elements']:
                                        community_tags.append(tags['value'])
                                elif _m_d['field_name'] == 'address_issued_bonds_to_sell' or _m_d[
                                    'field_name'] == 'target_xrd_amount' or _m_d[
                                    'field_name'] == 'proposal_creator_address':
                                    metadata[_m_d['field_name']] = _m_d['fields'][0]['value']
                                elif _m_d['field_name'] == 'amount_of_tokens_should_be_minted':
                                    pass
                                else:
                                    metadata[_m_d['field_name']] = _m_d['value']
                    else:
                        resources[field['field_name']] = field.get('value') or field.get('variant_name')

        print(community_tags)
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
                    token_bought=0,
                    purpose=metadata['purpose']
                )
                conn.add(community)
                for t in community_tags:
                    tag = CommunityTags(
                        community_id=community_id,
                        tag=t
                    )
                    conn.add(tag)
                conn.commit()
                participant = Participants(
                    user_addr=user_address,
                    community_id=community_id,
                )
                conn.add(participant)
                conn.commit()

                community = conn.query(Community).filter(Community.id == community_id).first()
                community_name = community.name
                random_string = generate_random_string()
                # add comment activity
                participate_activity = UserActivity(
                    transaction_id=random_string,
                    transaction_info=f'participated in {community_name}',
                    user_address=user_address,
                    community_id=community_id
                )
                conn.add(participate_activity)

                activity = UserActivity(
                    transaction_id=tx_id,
                    transaction_info=f'created  {temp}',
                    user_address=user_address,
                    community_id=community_id
                )
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
                    proposal=metadata['title'],
                    description=metadata['description'],
                    community_id=community.id,
                    voted_for=0,
                    voted_against=0,
                    is_active=True,
                    start_time=metadata['start_time_ts'],
                    ends_time=metadata['end_time_ts'],
                    minimum_quorum=metadata['minimum_quorum'],
                    proposal_address=metadata['component_address'],
                    proposal_id=metadata['proposal_id']
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

                activity = UserActivity(
                    transaction_id=tx_id,
                    transaction_info=f'voted in ongoing proposal',
                    user_address=user_address,
                    community_id=proposal.community_id
                )
                conn.commit()
            elif resources['event_type'] == 'EXECUTE_PROPOSAL':
                component_address = resources['component_address']
                proposal_address = metadata['praposal_address']
                community = conn.query(Community).filter(Community.component_address == component_address).first()
                community.funds = community.funds - 40
                proposal = conn.query(Proposal).filter(Proposal.proposal_address == proposal_address).first()
                proposal.is_active = False
                activity = UserActivity(
                    transaction_id=tx_id,
                    transaction_info=f'executed a proposal',
                    user_address=user_address,
                    community_id=proposal.community_id
                )
                conn.add(activity)
                conn.commit()


        except SQLAlchemyError as e:
            print(e)
            conn.rollback()
            # logger.error(f"SQLAlchemy error occurred: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

        return resources

    else:
        print(f"Request failed with status code {response.status_code}")
