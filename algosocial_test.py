from ast import Constant
import json

from algosdk.atomic_transaction_composer import *
from algosdk.future.transaction import *
from algosdk.v2client.algod import AlgodClient
from algosdk.encoding import decode_address
from algosdk.abi import *
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
    app_client = ApplicationClient(client, app, signer=signer1)

    # Create the applicatiion on chain, set the app id for the app client
    app_id, app_addr, txid = app_client.create()
    print(
        f"Created App with id: {app_id} and address addr: {app_addr} in tx: {txid} \n"
    )

    # Fan of the creator. Used to test donation function
    app_client2 = app_client.prepare(signer=signer2)

    ##############
    # Initialize
    ##############

    params = client.suggested_params()
    receiver = app_addr
    amount = 100000
    signer = AccountTransactionSigner(sk1)

    ptxn = TransactionWithSigner(PaymentTxn(addr1, params, receiver, amount), signer)

    app_client.call(app.initialize, txn=ptxn)

    account_info = client.account_info(app_addr)
    print(
        "Social App balance after initialization: {} Algos".format(
            account_info.get("amount") / 1000000
        )
        + "\n"
    )

    ##############
    # Create Profile
    ##############

    comp = AtomicTransactionComposer()

    intro = "I am an Algorand Developer Advocate."
    twitter = "https://twitter.com/HGKimChris"

    comp.add_method_call

    comp.add_method_call(
        app_id,
        app.contract.get_method_by_name("set_name"),
        addr1,
        params,
        signer1,
        method_args=["Chris Kim"],
    )

    comp.add_method_call(
        app_id,
        app.contract.get_method_by_name("set_tag"),
        addr1,
        params,
        signer1,
        method_args=["HGKimChris"],
    )

    comp.add_method_call(
        app_id,
        app.contract.get_method_by_name("set_email"),
        addr1,
        params,
        signer1,
        method_args=["chris.kim@algorand.com"],
    )

    comp.add_method_call(
        app_id,
        app.contract.get_method_by_name("set_age"),
        addr1,
        params,
        signer1,
        method_args=[25],
    )

    comp.add_method_call(
        app_id,
        app.contract.get_method_by_name("set_wallet"),
        addr1,
        params,
        signer1,
        method_args=[addr1],
    )

    comp.add_method_call(
        app_id,
        app.contract.get_method_by_name("set_intro"),
        addr1,
        params,
        signer1,
        method_args=[intro],
    )

    comp.add_method_call(
        app_id,
        app.contract.get_method_by_name("set_twitter"),
        addr1,
        params,
        signer1,
        method_args=[twitter],
    )

    comp.execute(client, 2)

    print("### App state after initial creation ### \n")

    for key in app_client.get_application_state():
        print(key, "->", app_client.get_application_state()[key])

    print("\n")

    #############################
    # Non user App Call Fail Test
    #############################

    print("### Trying to update info with address 2 (Should fail) ### \n")

    try:
        app_client2.call(app.set_name, new_name="Morty")
        app_client2.call(app.set_email, new_email="rick.morty@algorand.com")
        app_client2.call(app.set_age, new_age=12)
        app_client2.call(app.set_wallet, new_wallet=addr2)
    except Exception as e:
        print(
            "Failed as expected, only addr1 should be authorized to change profile info \n"
        )

    print(
        "### App state after update attempt from address 2. (should be the same) ### \n"
    )

    for key in app_client.get_application_state():
        print(key, "->", app_client.get_application_state()[key])

    print("\n")

    ##########################
    # Profile Data Update Test
    ##########################

    app_client.call(app.set_name, new_name="Chris H Kim")
    app_client.call(app.set_email, new_email="chris.kim2@algorand.com")
    app_client.call(app.set_age, new_age=26)

    print("### App state after update from address 1 ### \n")

    for key in app_client.get_application_state():
        print(key, "->", app_client.get_application_state()[key])

    account_info = client.account_info(app_addr)

    print("\n")

    ##############
    # Donation Test
    ##############

    account_info = client.account_info(addr2)
    print(
        "Account 2 balance before donation: {} Algos".format(
            account_info.get("amount") / 1000000
        )
        + "\n"
    )

    signer = AccountTransactionSigner(sk2)

    comp = AtomicTransactionComposer()

    receiver = app_addr
    amount = 1000000000  # 1000 Algo

    ptxn = TransactionWithSigner(PaymentTxn(addr2, params, receiver, amount), signer)

    app_client2.call(app.donate, txn=ptxn)

    print("Donation completed. \n")

    account_info = client.account_info(addr2)
    print(
        "Account 2 balance after donation: {} Algos".format(
            account_info.get("amount") / 1000000
        )
        + "\n"
    )

    print("### App state after donation ### \n")

    print("Donation Amount: ", app_client.get_application_state()["donation_amt"])

    account_info = client.account_info(app_addr)
    print(
        "Social App balance: {} Algos".format(account_info.get("amount") / 1000000)
        + "\n"
    )

    ##############
    # Withdraw Test
    ##############

    account_info = client.account_info(addr1)
    print(
        "Account 1 balance before withdrawing: {} Algos".format(
            account_info.get("amount") / 1000000
        )
        + "\n"
    )

    app_client.call(app.withdraw)

    account_info = client.account_info(addr1)
    print(
        "Account 1 balance after withdrawing: {} Algos".format(
            account_info.get("amount") / 1000000
        )
        + "\n"
    )

    print("### App State after Withdrawal ### \n")

    print("Donation Amount: ", app_client.get_application_state()["donation_amt"])

    account_info = client.account_info(app_addr)
    print(
        "Social App balance: {} Algos".format(account_info.get("amount") / 1000000)
        + "\n"
    )

    print("\n")

    ######################
    # Second Donation Test
    ######################

    account_info = client.account_info(addr2)
    print(
        "Account 2 balance before donation: {} Algos".format(
            account_info.get("amount") / 1000000
        )
        + "\n"
    )

    signer = AccountTransactionSigner(sk2)

    comp = AtomicTransactionComposer()

    receiver = app_addr
    amount = 1000000000  # 1000 Algo

    ptxn = TransactionWithSigner(PaymentTxn(addr2, params, receiver, amount), signer)

    app_client2.call(app.donate, txn=ptxn)

    print("Donation completed. \n")

    account_info = client.account_info(addr2)
    print(
        "Account balance 2 after donation: {} Algos".format(
            account_info.get("amount") / 1000000
        )
        + "\n"
    )

    print("### App state after donation ### \n")
    print("Donation Amount: ", app_client.get_application_state()["donation_amt"])

    account_info = client.account_info(app_addr)
    print(
        "Social App balance: {} Algos".format(account_info.get("amount") / 1000000)
        + "\n"
    )

    ########################################################################################################
    # Second Withdraw Test (check if min balance and min txn fees are maintained after multiple withdrawals)
    ########################################################################################################

    account_info = client.account_info(addr1)
    print(
        "Account 1 balance before withdrawing: {} Algos".format(
            account_info.get("amount") / 1000000
        )
        + "\n"
    )

    app_client.call(app.withdraw)

    account_info = client.account_info(addr1)
    print(
        "Account 1 balance after withdrawing: {} Algos".format(
            account_info.get("amount") / 1000000
        )
        + "\n"
    )

    print("### App State after Withdrawal ### \n")
    print("Donation Amount: ", app_client.get_application_state()["donation_amt"])

    account_info = client.account_info(app_addr)
    print(
        "Social App balance: {} Algos".format(account_info.get("amount") / 1000000)
        + "\n"
    )

    print("\n")


demo()
