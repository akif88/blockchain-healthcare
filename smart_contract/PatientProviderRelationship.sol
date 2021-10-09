pragma solidity ^0.4.19;


contract PatientProviderRelationship {

    address owner; // stewardship
    address patientAddress; // ownership

    // provider db info (i.e. hostname, port in standard network)
    string accessInfo;
    string dbQuery;
    string dbQueryHash; // to guarantee that data have not been altered

    address[] permissionsAddress; // for viewing other providers
    address minerAddress; // for viewing bounty db info
    string miningBounty; //block's miner as the owner of the bounty query

    modifier isOwner() {
        require(msg.sender == owner);
        _;
    }

    modifier validPatientAddress(address _patientAddress) {
        require(patientAddress == _patientAddress);
        _;
    }

    modifier validMinerAddress(address _minerAddress) {
        require(minerAddress == _minerAddress);
        _;
    }

    function PatientProviderRelationship(address _patientAddress) public {
        owner = msg.sender;
        patientAddress = _patientAddress;
    }

    function addDatabaseInfo(address _patientAddress, string _accessInfo, string _dbQuery, string _dbQueryHash )
    public isOwner validPatientAddress(_patientAddress)
    {
        accessInfo = _accessInfo; // provider network; hostname, port in a standard network
        dbQuery = _dbQuery;
        dbQueryHash = _dbQueryHash;
    }

    function addPermissionsAddress(address _providerAddress, address _patientAddress) public
    validPatientAddress(_patientAddress)
    {
        permissionsAddress.push(_providerAddress);
    }

  //  function removePermissionsAddress(address _providerAddress, address _patientAddress) public
   // validPatientAddress(_patientAddress)
    //{
     //   delete(permissionsAddress[_providerAddress]);
    //}

    function addMinerAddress(address _patientAddress, address _minerAddress) public
    isOwner validPatientAddress(_patientAddress)
    {
        minerAddress = _minerAddress;
    }

    function addMiningBounty(string _bountyQuery, address _patientAddress, address _minerAddress) public
    isOwner validPatientAddress(_patientAddress) validMinerAddress(_minerAddress)
    {
        miningBounty = _bountyQuery;
    }

    function getLenPermissionsAddress() public returns(uint) {
        return permissionsAddress.length;
    }

    function getPermissionsAddress(uint lenPermissionsAddress) returns(address) {
        return permissionsAddress[lenPermissionsAddress];
    }

}