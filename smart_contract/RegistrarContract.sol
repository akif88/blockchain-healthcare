pragma solidity ^0.4.19;

contract RegistrarContract {

    address public owner;
    mapping (address => uint) public balances;

    struct Patient {
        address patientAddress;
        uint amount; // for transaction
        address summaryContractAddresses;
    }

    // byte32 to provide a unique username
    mapping (bytes32 => Patient) ptt;
    bytes32[] patient;


    event LogAccountAdded(address _patientAddress, bytes32 _username);


    modifier validUser(bytes32 _username){
        require(isUser(_username), "error error");
        _;
    }

    // for sc reference
    //modifier validOwner(address _patientAddress){
        //require(msg.sender == _patientAddress);
    //}

    function RegistrarContract() public {
        owner = msg.sender;
    }


    // amount for the patient to be able to transact the blockchain
    function initialAccount(address _patientAddress, bytes32 _username, uint _amount) public payable
    validUser(_username)
    {
        ptt[_username].patientAddress = _patientAddress;
        ptt[_username].amount = _amount;
        _patientAddress.transfer(_amount);

        patient.push(_username);

        emit LogAccountAdded(_patientAddress, _username);
    }

    function isUser(bytes32 _username) public constant returns(bool){
        for(uint i= 0; i < patient.length; i++){
            if(patient[i] == _username){
                return false;
            }
        }

        return true;
    }

    // It must be arranged together with the SC.
    function summaryContractReference(bytes32 _username, address _summaryContractAddress) public
    validUser(_username)
    {
        ptt[_username].summaryContractAddresses = _summaryContractAddress;
    }

    function getAddress(bytes32 _patientName) public view returns(address) {
        return ptt[_patientName].patientAddress;
    }

}