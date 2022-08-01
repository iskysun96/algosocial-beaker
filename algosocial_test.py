from ast import Constant
import json

from algosdk.atomic_transaction_composer import *
from algosdk.future.transaction import *
from algosdk.v2client.algod import AlgodClient
from algosdk.encoding import decode_address
from beaker import client, sandbox
from beaker.client.application_client import ApplicationClient

from algosocial import AlgoSocial


def demo():
    client = sandbox.get_client()

    accts = sandbox.get_accounts()

    addr1, sk1 = accts.pop()
    signer1 = AccountTransactionSigner(sk1)

    addr2, sk2 = accts.pop()
    signer2 = AccountTransactionSigner(sk2)

    # Initialize Application from algosocial.py
    app = AlgoSocial()

    # Create an Application client containing both an algod client and my app
    app_client = ApplicationClient(client, app)

    # Create the applicatiion on chain, set the app id for the app client
    app_id, app_addr, txid = app_client.create(signer=signer1)
    print(
        f"Created App with id: {app_id} and address addr: {app_addr} in tx: {txid} \n"
    )

    # Creator account. Owner of the social profile
    app_client1 = app_client.prepare(signer=signer1)

    # Fan of the creator. Used to test donation function
    app_client2 = app_client.prepare(signer=signer2)

    ##############
    # Create Profile
    ##############

    intro = "I am an Algorand Developer Advocate."
    twitter = "https://twitter.com/HGKimChris"

    app_client1.call(app.set_name, new_name="Chris Kim")
    app_client1.call(app.set_tag, new_tag="HGKimChris")
    app_client1.call(app.set_email, new_email="chris.kim@algorand.com")
    app_client1.call(app.set_age, new_age=25)
    app_client1.call(app.set_wallet, new_wallet=addr1)
    app_client1.call(app.set_intro, new_intro=intro)
    app_client1.call(app.set_twitter, new_twitter=twitter)

    print(f"Current app state {app_client.get_application_state()} \n")

    #############################
    # Non user App Call Fail Test
    #############################

    try:
        app_client2.call(app.set_name, new_name="Morty")
        app_client2.call(app.set_email, new_email="rick.morty@algorand.com")
        app_client2.call(app.set_age, new_age=12)
        app_client2.call(app.set_wallet, new_wallet=addr2)
    except Exception as e:
        print(
            "Failed as expected, only addr1 should be authorized to change profile info \n"
        )

    print(f"Current app state {app_client.get_application_state()} \n")

    ##########################
    # Profile Data Update Test
    ##########################

    app_client1.call(app.set_name, new_name="Chris H Kim")
    app_client1.call(app.set_email, new_email="chris.kim2@algorand.com")
    app_client1.call(app.set_age, new_age=26)

    print(f"Current app state {app_client.get_application_state()} \n")

    ##############
    # Donation Test
    ##############

    signer = AccountTransactionSigner(sk2)

    params = client.suggested_params()

    comp = AtomicTransactionComposer()

    receiver = app_addr
    amount = 1000000

    ptxn = TransactionWithSigner(PaymentTxn(addr2, params, receiver, amount), signer)

    app_client2.call(app.donate, txn=ptxn)

    print(f"Current app state {app_client.get_application_state()} \n")


demo()
