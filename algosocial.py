from typing import Final


from algosdk.atomic_transaction_composer import AccountTransactionSigner

from beaker.client import ApplicationClient
from beaker import ApplicationState, opt_in, sandbox, consts

from pyteal import *
from beaker.application import Application
from beaker.state import ApplicationStateValue
from beaker.decorators import external, create, Authorize


class AlgoSocial(Application):

    name: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.bytes,
        descr="name of the user",
    )

    tag: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.bytes, descr="user ID / tag / .algo NFD Domain"
    )

    email: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.bytes,
        descr="email of the user",
    )

    age: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.uint64,
        descr="age of the user",
    )

    wallet: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.bytes,
        descr="wallet address of the user",
    )

    intro: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.bytes, descr="Short introduction of the user"
    )

    twitter: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.bytes, descr="User's Twitter URL"
    )

    joined: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.uint64,
        static=True,
        descr="Date when the profile was first created",
    )

    donation_amt: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.uint64,
        descr="amount of donation received and held by the contract",
    )

    @create
    def create(self):
        """create application"""
        return Seq(
            self.initialize_application_state(),
            self.joined.set(Global.latest_timestamp()),
        )

    @external(authorize=Authorize.only(Global.creator_address()))
    def set_name(self, new_name: abi.String):
        return self.name.set(new_name.get())

    @external(authorize=Authorize.only(Global.creator_address()))
    def set_tag(self, new_tag: abi.String):
        return self.tag.set(new_tag.get())

    @external(authorize=Authorize.only(Global.creator_address()))
    def set_email(self, new_email: abi.String):
        return self.email.set(new_email.get())

    @external(authorize=Authorize.only(Global.creator_address()))
    def set_intro(self, new_intro: abi.String):
        return self.intro.set(new_intro.get())

    @external(authorize=Authorize.only(Global.creator_address()))
    def set_twitter(self, new_twitter: abi.String):
        return self.twitter.set(new_twitter.get())

    @external(authorize=Authorize.only(Global.creator_address()))
    def set_age(self, new_age: abi.Uint64):
        return self.age.set(new_age.get())

    @external(authorize=Authorize.only(Global.creator_address()))
    def set_wallet(self, new_wallet: abi.Address):
        return self.wallet.set(new_wallet.get())

    @external
    def donate(self, txn: abi.PaymentTransaction):
        valid_payment_txn = And(
            txn.get().type_enum() == TxnType.Payment,
            # minimum donation 1 Algo
            txn.get().amount() >= consts.Algos(1),
            txn.get().receiver() == Global.current_application_address(),
        )

        return Seq(
            Assert(valid_payment_txn),
            self.donation_amt.set(self.donation_amt + txn.get().amount()),
        )


# def demo():
#     client = sandbox.get_client()

#     accts = sandbox.get_accounts()

#     addr1, sk1 = accts.pop()
#     signer1 = AccountTransactionSigner(sk1)

#     addr2, sk2 = accts.pop()
#     signer2 = AccountTransactionSigner(sk2)

#     # Initialize Application from algosocial.py
#     app = AlgoSocial()

#     # Create an Application client containing both an algod client and my app
#     app_client = ApplicationClient(client, app)

#     # Create the applicatiion on chain, set the app id for the app client
#     app_id, app_addr, txid = app_client.create(signer=signer1)
#     print(f"Created App with id: {app_id} and address addr: {app_addr} in tx: {txid}")

#     app_client1 = app_client.prepare(signer=signer1)
#     app_client2 = app_client.prepare(signer=signer2)

#     app_client1.call(app.set_name, new_name="Chris Kim")
#     app_client1.call(app.set_email, new_email="chris.kim@algorand.com")
#     app_client1.call(app.set_age, new_age=25)
#     app_client1.call(app.set_wallet, new_wallet=addr1)

#     print(f"Current app state {app_client.get_application_state()}")

#     try:
#         app_client2.call(app.set_name, new_name="Morty")
#         app_client2.call(app.set_email, new_email="rick.morty@algorand.com")
#         app_client2.call(app.set_age, new_age=12)
#         app_client2.call(app.set_wallet, new_wallet=addr2)
#     except Exception as e:
#         print(
#             "Failed as expected, only addr1 should be authorized to change profile info"
#         )

#     print(f"Current app state {app_client.get_application_state()}")

#     app_client1.call(app.set_name, new_name="Chris H Kim")
#     app_client1.call(app.set_email, new_email="chris.kim2@algorand.com")
#     app_client1.call(app.set_age, new_age=26)
#     app_client1.call(app.set_wallet, new_wallet=addr2)

#     print(f"Current app state {app_client.get_application_state()}")

#     app_client2.call(
#         app.donate,
#     )


if __name__ == "__main__":
    ca = AlgoSocial()
    print(ca.app_state.schema().__dict__)

    # demo()
