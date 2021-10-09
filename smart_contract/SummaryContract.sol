pragma solidity ^0.4.19;

contract SummaryContract {

    address owner; //provider
    address patientAddress;
    address[] PPRAddress;
    bool status = false;

    modifier isOwner() {
        require(msg.sender == owner);
        _;
    }

    modifier validPatientAddress(address _patientAddress) {
        require(patientAddress == _patientAddress);
        _;
    }

    function SummaryContract(address _patientAddress) public {
        owner = msg.sender;
        patientAddress = _patientAddress;
    }

    function addPPRAddress(address _PPRAddress, address _patientAddress) public
    isOwner validPatientAddress(_patientAddress)
    {
        PPRAddress.push(_PPRAddress);
    }


    function setStatus(address _patientAddress) public isOwner validPatientAddress(_patientAddress) {
        status = true;
    }


    function getProviderAddress() public view returns(address) {
        return owner;
    }

    function getPatientAddress() public view returns(address) {
        return patientAddress;
    }

    function getStatus(address _patientAddress) public view returns(bool) {
        return status;
    }



}