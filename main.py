import os
import sqlite3
import asyncio
from tonutils.client import TonapiClient
from tonutils.wallet import PreprocessedWalletV2R1
from tonutils.wallet.data import TransferData
from tonutils.client import TonapiClient
from tonutils.wallet import (
    WalletV3R1,
    # Uncomment the following lines to use different wallet versions:
    # WalletV3R2,
    # WalletV4R1,
    # WalletV4R2,
    # WalletV5R1,
    # HighloadWalletV2,
    # HighloadWalletV3,
    # PreprocessedWalletV2,
    # PreprocessedWalletV2R1,
)

# API key for accessing the Tonapi (obtainable from https://tonconsole.com)
API_KEY = "AEXUUXDMF6AZYIIAAAAMJIJXGS7L4QVNYMFNVRXE7K2ZMH4ZEONFROWDBRMT6NK5IH5OTZY"  # Add your API key here.

# Set to True for test network, False for main network
IS_TESTNET = True

async def send(private_key: str, send_to: str, amount: float):
    """
    Sends the specified amount to the given address using the private key.

    Args:
        private_key (str): The private key of the sender's wallet.
        send_to (str): The recipient's wallet address.
        amount (float): The amount to send (in TON).

    Returns:
        None
    """
    client = TonapiClient(api_key=API_KEY, is_testnet=IS_TESTNET)

    # Create a KeyPair from the private key
    keypair = KeyPair(private=private_key)

    # Create the wallet using the keypair
    wallet = PreprocessedWalletV2R1(client=client, keypair=keypair)

    # Perform the transfer
    tx_hash = await wallet.transfer(
        destination=send_to,
        amount=amount,
        body="Transfer from tonutils",
    )

    print("Successfully transferred!")
    print(f"Transaction hash: {tx_hash}")


def create_db():
    """
    Creates a SQLite database 'users.sql' with a table 'users' and columns:
    wallet_id, public_key, private_key, balance.

    Returns:
        None
    """
    conn = sqlite3.connect('users.sql')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            wallet_id TEXT PRIMARY KEY,
            public_key TEXT NOT NULL,
            private_key TEXT NOT NULL,
            balance REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("Database 'users.sql' created with table 'users'.")


def create_wallet(wallet_id: str):
    """
    Generates a mnemonic, creates a wallet using it, saves the keys and mnemonic
    to the 'wallets' folder, and writes wallet details to the database.

    Args:
        wallet_id (str): The unique wallet ID.

    Returns:
        None
    """
    client = TonapiClient(api_key=API_KEY, is_testnet=IS_TESTNET)

    # Generate a new mnemonic and create the wallet
    wallet_class = WalletV3R1
    wallet, public_key, private_key, mnemonic = wallet_class.create(client)

    mnemonic_str = " ".join(mnemonic)

    # Save wallet information to a file
    os.makedirs("wallets", exist_ok=True)
    wallet_file = os.path.join("wallets", f"{wallet.address.to_str()}.txt")
    with open(wallet_file, "w") as file:
        file.write(f"Address: {wallet.address.to_str()}\n")
        file.write(f"Public Key: {public_key}\n")
        file.write(f"Private Key: {private_key}\n")
        file.write(f"Mnemonic: {mnemonic_str}\n")

    print(f"Wallet saved to {wallet_file}")

    # Insert wallet details into the database
    conn = sqlite3.connect('users.sql')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO users (wallet_id, public_key, private_key, balance)
            VALUES (?, ?, ?, ?)
        ''', (wallet_id, public_key, private_key, 0))
        conn.commit()
        print(f"Wallet details inserted into database with wallet_id: {wallet_id}")
    except sqlite3.IntegrityError as e:
        print(f"An error occurred while inserting into the database: {e}")
    finally:
        conn.close()


def main():
    """
    Main function to orchestrate the database creation and wallet creation.
    """
    try:
        # Step 1: Create the database
        create_db()

        # Step 2: Create wallet
        wallet_id = input("Enter a unique wallet ID: ")
        create_wallet(wallet_id)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()