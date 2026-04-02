// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AgentPaymentLedger
 * @notice On-chain record of x402 agent-to-agent payments in the Golden Codex RAMS.
 * @dev Deployed on Kite Ozone Testnet (Chain ID: 2368).
 *
 * This contract serves as an immutable audit trail for all AP2 (x402) settlements
 * between agents in the Recursive Agent Market Swarm. Each payment is logged with
 * the service provided, enabling:
 *
 * 1. Transparency: Anyone can verify agent payment history
 * 2. Analytics: Dashboard queries for total settlements, per-agent revenue
 * 3. PoAI eligibility: Proof of compute work for Kite reward distribution
 * 4. Dispute resolution: Immutable record of service delivery
 *
 * Payment flow:
 * 1. Thalos Prime (Architect Agent) initiates pipeline job
 * 2. Session Key authorizes budget for this job
 * 3. Each agent completes work and receives USDC via x402
 * 4. Facilitator settles payment and calls recordPayment() here
 * 5. Event emitted for dashboard indexing
 */

contract AgentPaymentLedger {
    /// @notice Total number of recorded payments
    uint256 public totalPayments;

    /// @notice Total USDC settled through this ledger (6 decimals)
    uint256 public totalUsdcSettled;

    /// @notice Per-agent total earnings
    mapping(address => uint256) public agentEarnings;

    /// @notice Per-agent payment count
    mapping(address => uint256) public agentPaymentCount;

    /// @notice Emitted when an x402 payment is recorded
    event PaymentExecuted(
        address indexed from,
        address indexed to,
        uint256 amount,
        string service,
        bytes32 indexed jobId,
        uint256 timestamp
    );

    /// @notice Emitted when a full pipeline job is settled
    event JobSettled(
        bytes32 indexed jobId,
        uint256 totalCostUsdc,
        uint256 agentCount,
        uint256 timestamp
    );

    /**
     * @notice Record a single x402 agent-to-agent payment.
     * @param from Sender (typically Thalos Prime vault address)
     * @param to Recipient agent vault address
     * @param amount USDC amount (6 decimals)
     * @param service Description of service provided (e.g., "nova_enrichment")
     * @param jobId Pipeline job identifier
     */
    function recordPayment(
        address from,
        address to,
        uint256 amount,
        string calldata service,
        bytes32 jobId
    ) external {
        totalPayments++;
        totalUsdcSettled += amount;
        agentEarnings[to] += amount;
        agentPaymentCount[to]++;

        emit PaymentExecuted(from, to, amount, service, jobId, block.timestamp);
    }

    /**
     * @notice Record completion of a full pipeline job.
     * @param jobId Pipeline job identifier
     * @param totalCostUsdc Total USDC spent on all agents for this job
     * @param agentCount Number of agents that participated
     */
    function recordJobCompletion(
        bytes32 jobId,
        uint256 totalCostUsdc,
        uint256 agentCount
    ) external {
        emit JobSettled(jobId, totalCostUsdc, agentCount, block.timestamp);
    }

    // --- View functions for dashboard queries ---

    /**
     * @notice Get total earnings for a specific agent.
     * @param agent The agent vault address
     * @return Total USDC earned (6 decimals)
     */
    function getAgentEarnings(address agent) external view returns (uint256) {
        return agentEarnings[agent];
    }

    /**
     * @notice Get payment count for a specific agent.
     * @param agent The agent vault address
     * @return Number of payments received
     */
    function getAgentPaymentCount(address agent) external view returns (uint256) {
        return agentPaymentCount[agent];
    }

    /**
     * @notice Get global ledger statistics.
     * @return _totalPayments Total payment count
     * @return _totalUsdcSettled Total USDC settled (6 decimals)
     */
    function getStats() external view returns (uint256 _totalPayments, uint256 _totalUsdcSettled) {
        return (totalPayments, totalUsdcSettled);
    }
}
