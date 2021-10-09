from solc import compile_source
from web3 import Web3, HTTPProvider
from web3 import admin, personal, eth, miner

import time
import hashlib


def read_smart_contract():
    with open('smart_contract/RegistrarContract.sol') as f:
        smart_contract_rc = f.read()

    with open('smart_contract/SummaryContract.sol') as f:
        smart_contract_sc = f.read()

    with open('smart_contract/PatientProviderRelationship.sol') as f:
        smart_contract_ppr = f.read()

    return smart_contract_rc, smart_contract_sc, smart_contract_ppr


def compile_smart_contract():
    smart_contract_rc, smart_contract_sc, smart_contract_ppr = read_smart_contract()

    compiled_solidity_rc = compile_source(smart_contract_rc)
    contract_interface_rc = compiled_solidity_rc['<stdin>:RegistrarContract']

    compiled_solidity_sc = compile_source(smart_contract_sc)
    contract_interface_sc = compiled_solidity_sc['<stdin>:SummaryContract']

    compiled_solidity_ppr = compile_source(smart_contract_ppr)
    contract_interface_ppr = compiled_solidity_ppr['<stdin>:PatientProviderRelationship']

    return contract_interface_rc, contract_interface_sc, contract_interface_ppr


# ------- start web3 ----------
# used with geth
w3 = Web3(HTTPProvider("http://127.0.0.1:8545"))

# start admin
admin_w3 = admin.Admin(w3)
# start personal to create, list etc.
personal_w3 = personal.Personal(w3)
# start ethereum
eth_w3 = eth.Eth(w3)
# start miner for mining, coinbase, setEtherBase
miner_w3 = miner.Miner(w3)

# all contract interface
contract_interface_rc, contract_interface_sc, contract_interface_ppr = compile_smart_contract()


def create_patient_account(username, password, user):
    eth_addr = personal_w3.newAccount(password)

    # unlock patient account
    personal_w3.unlockAccount(eth_addr, password)

    # add patient to registrar contract
    initial_rc_smart_contract(username, eth_addr, user)


def initial_rc_smart_contract(username, eth_addr, user):
    # Instantiate and deploy contract
    Registrar = eth_w3.contract(abi=contract_interface_rc['abi'], bytecode=contract_interface_rc['bin'])

    # add blockchain new personal with constructor
    tx_hash = Registrar.constructor().transact({"from": eth_w3.accounts[0]})

    # mining registrar constructor block
    mining(tx_hash, user)

    # get block after mining
    tx_receipt = eth_w3.getTransactionReceipt(tx_hash)

    # Create the contract instance with the newly-deployed address with contract address
    registry = eth_w3.contract(
        address=tx_receipt.contractAddress,
        abi=contract_interface_rc['abi']
    )

    # add patient contract and give initial cryptocurrency
    tx_hash = registry.functions.initialAccount(eth_addr, username.encode(), 100).transact(
        {'from': eth_w3.accounts[0],
         'value': w3.toWei(100, 'wei')}
    )

    # mining after added patient in block
    mining(tx_hash, user)

    # get block after mining
    tx_receipt_initial_rc = eth_w3.getTransactionReceipt(tx_hash)

    # add patient to registrar contract
    initial_sc_smart_contract(username, eth_addr, registry, user)


def initial_sc_smart_contract(username, eth_addr, registry, user):
    # Instantiate and deploy contract
    Summary = eth_w3.contract(abi=contract_interface_sc['abi'], bytecode=contract_interface_sc['bin'])

    # add blockchain patient eth address with constructor
    tx_hash = Summary.constructor(eth_addr).transact({'from': eth_w3.accounts[0]})

    # mining summary constructor block
    mining(tx_hash, user)

    # get block after mining
    tx_receipt = eth_w3.getTransactionReceipt(tx_hash)

    # Create the contract instance with the newly-deployed address with contract address
    summary = eth_w3.contract(
        address=tx_receipt.contractAddress,
        abi=contract_interface_sc['abi'],
    )

    # send Registrar Contract Summary Contract Address
    tx_hash = registry.functions.summaryContractReference(username.encode(), summary.address)\
        .transact({'from': eth_w3.accounts[0]})

    # mining after sending summary contract address
    mining(tx_hash, user)

    # get block after mining
    tx_receipt = eth_w3.getTransactionReceipt(tx_hash)



    '''
        this method is used after provider add patient record!!!     
    '''
    # add patient to registrar contract
    #initial_ppr_smart_contract(username, eth_addr, summary, user)


def initial_ppr_smart_contract(username, eth_addr, summary, user):
    # Instantiate and deploy contract
    Relationship = eth_w3.contract(abi=contract_interface_ppr['abi'], bytecode=contract_interface_ppr['bin'])

    # add blockchain patient eth address with constructor
    tx_hash = Relationship.constructor(eth_addr).transact({'from': eth_w3.accounts[0]})

    # mining ppr constructor block
    mining(tx_hash, user)

    # get block after mining
    tx_receipt = eth_w3.getTransactionReceipt(tx_hash)

    # Create the contract instance with the newly-deployed address with contract address
    ppr = eth_w3.contract(
        address=tx_receipt.contractAddress,
        abi=contract_interface_ppr['abi'],
    )

    # send PPR address to summary contract
    tx_hash = summary.functions.addPPRAddress(ppr.address, eth_addr).transact({'from': eth_w3.accounts[0]})

    # mining after adding ppr address and patient address
    mining(tx_hash, user)

    # get block after mining
    tx_receipt = eth_w3.getTransactionReceipt(tx_hash)

    # add ppr patient query, patient address and db info
    access_info = "provider.db"
    db_query = "select created_date, title, note from patient_record where patient_id=" + eth_addr
    db_query_hash = hashlib.sha256(db_query.encode()).hexdigest()
    tx_hash = ppr.functions.addDatabaseInfo(eth_addr, access_info, db_query, db_query_hash).transact(
        {'from': eth_w3.accounts[0]})

    # mining after adding db query fot patient
    mining(tx_hash, user)

    # get block after mining
    tx_receipt = eth_w3.getTransactionReceipt(tx_hash)



    '''
        if miner earn token, how should we arrange PPR!!!
    '''

    # miner address to send smart contract
    block_no = tx_receipt['blockNumber']
    block = eth_w3.getBlock(block_no)
    # print("Miner Address: ", block['miner'])
    miner_address = block['miner']
    tx_hash = ppr.functions.addMinerAddress(eth_addr, miner_address).transact({'from': eth_w3.accounts[0]})

    # mining after adding miner address
    mining(tx_hash, user)

    # get block after mining
    tx_receipt = eth_w3.getTransactionReceipt(tx_hash)


    # add miner db query
    miner_db_query = "select note from patient_record where id > 0 and id < 10"
    tx_hash = ppr.functions.addMiningBounty(miner_db_query, eth_addr, miner_address).transact(
        {'from': eth_w3.accounts[0]})

    mining(tx_hash, user)

    # get block
    tx_receipt = eth_w3.getTransactionReceipt(tx_hash)


# miner use for mining this method
# provider and patient wait mining
def mining(tx_hash=None, user=""):
    if user == 'miner':
        miner_w3.start(8)
        time.sleep(60)
        miner_w3.stop()
    else:
        eth_w3.waitForTransactionReceipt(tx_hash)


