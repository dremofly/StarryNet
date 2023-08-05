// SPDX-License-Identifier: MIT

pragma solidity>=0.4.24 <0.6.11;
contract SimpleBank {

    // 定义一个键值对映射来存储每个账户的余额
    mapping (address => uint) private balances;
    
    // 事件：当用户存款或取款时，我们可以记录其发生
    event LogDepositMade(address indexed accountAddress, uint amount);
    event LogWithdrawal(address indexed accountAddress, uint withdrawAmount, uint newBalance);

    // 公开的存款方法，允许用户向其账户存款
    function deposit() public returns (uint) {
        // 用msg.value更新用户的余额
        balances[msg.sender] += 10;

        // 触发存款事件
        emit LogDepositMade(msg.sender, 10);

        return balances[msg.sender];
    }

    // 允许用户从其账户中取款，要求用户必须有足够的余额
    function withdraw() public returns (uint remainingBal) {
        // require(balances[msg.sender] >= 1);
        
        // 减少用户的余额

        balances[msg.sender] -= 1;
        // 将金额返回给用户
        address recipient = msg.sender;
        recipient.transfer(1);

        // 触发取款事件
        emit LogWithdrawal(msg.sender, 1, balances[msg.sender]);

        return balances[msg.sender];
    }

    // 允许用户查询其余额
    function balance() view public returns (uint) {
        return balances[msg.sender];
    }
}


