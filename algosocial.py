from typing import Final

from beaker.client import ApplicationClient
from beaker import ApplicationState, internal, opt_in, sandbox, consts

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

    @external
    def initialize(self, txn: abi.PaymentTransaction):
        """Send Algos to cover Minimum_balance"""

        valid_txn = [
            txn.get().type_enum() == TxnType.Payment,
            txn.get().amount() == Global.min_balance(),
            txn.get().receiver() == self.address,
        ]

        return Seq(Assert(*valid_txn))

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

    # Donation Features

    @external
    def donate(self, txn: abi.PaymentTransaction):
        valid_payment_txn = [
            txn.get().type_enum() == TxnType.Payment,
            # minimum donation 1 Algo
            txn.get().amount() >= consts.Algos(1),
            txn.get().receiver() == self.address,
        ]

        return Seq(
            Assert(*valid_payment_txn),
            self.donation_amt.set(self.donation_amt + txn.get().amount()),
        )

    @external(authorize=Authorize.only(Global.creator_address()))
    def withdraw(self):
        return Seq(
            [
                InnerTxnBuilder.Begin(),
                InnerTxnBuilder.SetFields(
                    {
                        TxnField.type_enum: TxnType.Payment,
                        TxnField.amount: self.donation_amt - Global.min_txn_fee(),
                        TxnField.receiver: self.wallet,
                    }
                ),
                InnerTxnBuilder.Submit(),
                self.donation_amt.set(
                    self.donation_amt - InnerTxn.amount() - Global.min_txn_fee()
                ),
            ]
        )

    # Following / Follwer Functionalities

    def follower_optin(self):
        """when someone want to follow this profile, they opt in to this contract. Follower count goes up by one"""
        valid_account = []


if __name__ == "__main__":
    ca = AlgoSocial()
    print(ca.app_state.schema().__dict__)
