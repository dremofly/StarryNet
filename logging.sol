pragma solidity>=0.4.24 <0.6.11;

// 参考 OK.sol
contract logging {
    struct OpLog {
        string time;
        string operation;
        int parameter1;
        int parameter2;
    }

    struct OpLog2 {
        address user;
        string operation;
    }

    OpLog2[] public pendingLogs; // TODO: 引入lock
    OpLog2[] public submmitedLogs;
    uint256 private pendIndex = 0;

    mapping (address => string[]) public operationLogs;

    mapping (address => OpLog) public UserLog;
    mapping (address => OpLog) public UserLogOne; // 前一个log
    mapping (address => OpLog) public UserLogTwo; // 前两个log

    event SubmitNewLog(address accountAddress, string time, string operation, int p1, int p2);
    event SubmitNewLog2(address accountAddress, string signedMessage);

    event Log21OpError(address accountAddress, string op1, string op2);
    event Log10OpError(address accountAddress, string op0, string op1);
    event Log10P1Error(address accountAddress, int p0, int p1);
    event Log21P1Error(address accountAddress, int p1, int p2);
    event Log10P2Error(address accountAddress, int p0, int p1);
    event Log21P2Error(address accountAddress, int p1, int p2);
    event CheckOk(address accountaAddress);
    event InitVeirify(address accountAddress, string time, string op, int p1, int p2);
    event CheckLog(address accountAddress, string time, string op, int p1, int p2);

    function compareStrings(string memory a, string memory b) public pure returns(bool) {
        // Desc: 比较字符串
        return keccak256(abi.encodePacked(a)) != keccak256(abi.encodePacked(b));
    }

    function SubLog(string time, string operation, int p1, int p2) { 
        // Desc: 用户周期性的提交log
        // UserLog[msg.sender] = UserLog;
        // OpLog one = UserLog;
        UserLogTwo[msg.sender] = OpLog(UserLogOne[msg.sender].time, UserLogOne[msg.sender].operation, UserLogOne[msg.sender].parameter1, UserLogOne[msg.sender].parameter2);
        UserLogOne[msg.sender] = OpLog(UserLog[msg.sender].time, UserLog[msg.sender].operation, UserLog[msg.sender].parameter1, UserLog[msg.sender].parameter2);
        UserLog[msg.sender] = OpLog(time, operation, p1, p2);
        emit SubmitNewLog(msg.sender, time, operation, p1, p2);
        return;
    }

    function ShowLog() {
       emit CheckLog(msg.sender, UserLog[msg.sender].time, UserLog[msg.sender].operation, UserLog[msg.sender].parameter1, UserLog[msg.sender].parameter1); 
       emit CheckLog(msg.sender, UserLogOne[msg.sender].time, UserLogOne[msg.sender].operation, UserLogOne[msg.sender].parameter1, UserLogOne[msg.sender].parameter1); 
       emit CheckLog(msg.sender, UserLogTwo[msg.sender].time, UserLogTwo[msg.sender].operation, UserLogTwo[msg.sender].parameter1, UserLogTwo[msg.sender].parameter1); 
    }

    function VerifyLog(address accountAddress) {
        OpLog logTwo = UserLogTwo[accountAddress];
        OpLog logOne = UserLogOne[accountAddress];
        OpLog log = UserLog[accountAddress];

        emit InitVeirify(accountAddress, log.time, log.operation, log.parameter1, log.parameter2);
        if (compareStrings(logTwo.operation, logOne.operation)) {
            emit Log21OpError(accountAddress, logOne.operation, logTwo.operation);
            return;
        }
        if (compareStrings(log.operation, logOne.operation)) {
            emit Log10OpError(accountAddress, log.operation, logOne.operation);
            return;
        }
        if (log.parameter1 != logOne.parameter1) {
            emit Log10P1Error(accountAddress, log.parameter1, logOne.parameter1); 
            return;
        }
        if (logTwo.parameter1 != logOne.parameter1) {
            emit Log21P1Error(accountAddress, logOne.parameter1, logTwo.parameter1); 
            return;
        }
        if (log.parameter2 != logOne.parameter2) {
            emit Log10P2Error(accountAddress, log.parameter2, logOne.parameter2); 
            return;
        }
        if (logTwo.parameter2 != logOne.parameter2) {
            emit Log21P2Error(accountAddress, logOne.parameter2, logTwo.parameter2); 
            return;
        }
        emit CheckOk(accountAddress);
        return;
    }

    function SubLog2(address account, string signedMessage) {
        // account: 公钥
        // signedMessage: 关键日志信息使用密钥加密的版本，可以用于监控网络，或实现其他功能。
        OpLog2 memory log = OpLog2(account, signedMessage);
        pendingLogs.push(log);
        emit SubmitNewLog2(account, signedMessage);
        return;
    }

    function GetOnePengdingTx() view returns(address, string) {
        OpLog2 memory log = pendingLogs[pendIndex];
        return (log.user, log.operation); 
    }

    function approveLog() {
        OpLog2 memory log = pendingLogs[0];
        submmitedLogs.push(log);
        pendIndex += 1;
        return;
    }

    function abandonLog() {{
        pendIndex += 1;
        return;
    }}

    function GetOneSubmittedLogs(int index) view returns(address, string) {
        OpLog2 memory log = submmitedLogs[0];
        return (log.user, log.operation);
    }

    // function VerifyLog2(address account) view returns(string) {
    //     string[] logs = operationLogs[account]; 
    //     uint lastIndex = logs.length - 1;
    //     return logs[lastIndex];
    // }
}