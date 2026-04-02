// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AeternumProvenanceSchema
 * @notice EAS schema registration helper for Golden Codex provenance attestations on Kite chain.
 * @dev Registers and manages the Soulprint attestation schema on Ethereum Attestation Service (EAS).
 *
 * Schema: (bytes32 soulmark, string arweaveCid, address[] agentSwarm, uint256 totalComputeCostUsdc)
 *
 * - soulmark: SHA-256 hash of the final artifact (strip-proof identity)
 * - arweaveCid: Arweave Content ID for permanent storage verification
 * - agentSwarm: Ordered list of agent vault addresses that processed this artwork
 * - totalComputeCostUsdc: Total x402 settlement cost in USDC (6 decimals)
 *
 * Kite integration:
 * - Deployed on Kite Ozone Testnet (Chain ID: 2368)
 * - Atlas agent calls registerProvenance() after metadata infusion
 * - PoAI rewards accrue to the agent swarm for attested compute
 */

/// @dev Interface for Kite's EAS SchemaRegistry (compatible with standard EAS)
interface ISchemaRegistry {
    function register(
        string calldata schema,
        address resolver,
        bool revocable
    ) external returns (bytes32);
}

/// @dev Interface for Kite's EAS instance
interface IEAS {
    struct AttestationRequestData {
        address recipient;
        uint64 expirationTime;
        bool revocable;
        bytes32 refUID;
        bytes data;
        uint256 value;
    }

    struct AttestationRequest {
        bytes32 schema;
        AttestationRequestData data;
    }

    function attest(AttestationRequest calldata request) external payable returns (bytes32);
}

contract AeternumProvenanceSchema {
    /// @notice The registered EAS schema UID
    bytes32 public schemaUID;

    /// @notice EAS contract address on Kite (set during deployment)
    IEAS public immutable eas;

    /// @notice Schema registry on Kite
    ISchemaRegistry public immutable schemaRegistry;

    /// @notice Schema definition string
    string public constant SCHEMA = "bytes32 soulmark, string arweaveCid, address[] agentSwarm, uint256 totalComputeCostUsdc";

    /// @notice Emitted when a provenance attestation is created
    event ProvenanceAttested(
        bytes32 indexed attestationUID,
        bytes32 indexed soulmark,
        string arweaveCid,
        address[] agentSwarm,
        uint256 totalComputeCostUsdc
    );

    constructor(address _eas, address _schemaRegistry) {
        eas = IEAS(_eas);
        schemaRegistry = ISchemaRegistry(_schemaRegistry);
    }

    /**
     * @notice Register the Aeternum Provenance schema with EAS.
     * @dev Should be called once after deployment. Schema is non-revocable.
     */
    function registerSchema() external returns (bytes32) {
        schemaUID = schemaRegistry.register(
            SCHEMA,
            address(0), // No resolver — attestations are self-validating
            false        // Non-revocable — provenance is permanent
        );
        return schemaUID;
    }

    /**
     * @notice Create a provenance attestation for a processed artwork.
     * @param soulmark SHA-256 hash of the final artifact
     * @param arweaveCid Arweave content identifier
     * @param agentSwarm Ordered list of agent addresses that processed this artwork
     * @param totalComputeCostUsdc Total pipeline cost in USDC (6 decimals)
     * @return attestationUID The EAS attestation UID
     */
    function registerProvenance(
        bytes32 soulmark,
        string calldata arweaveCid,
        address[] calldata agentSwarm,
        uint256 totalComputeCostUsdc
    ) external returns (bytes32 attestationUID) {
        require(schemaUID != bytes32(0), "Schema not registered");
        require(agentSwarm.length > 0, "Agent swarm cannot be empty");

        attestationUID = eas.attest(
            IEAS.AttestationRequest({
                schema: schemaUID,
                data: IEAS.AttestationRequestData({
                    recipient: address(0), // No specific recipient — public attestation
                    expirationTime: 0,     // Never expires
                    revocable: false,
                    refUID: bytes32(0),
                    data: abi.encode(soulmark, arweaveCid, agentSwarm, totalComputeCostUsdc),
                    value: 0
                })
            })
        );

        emit ProvenanceAttested(attestationUID, soulmark, arweaveCid, agentSwarm, totalComputeCostUsdc);
    }
}
