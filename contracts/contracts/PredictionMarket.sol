// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/// @title PredictionMarket
/// @notice Simple up/down prediction market for an asset price on a future timestamp.
/// @dev Designed for Base Sepolia deployment. Minimizes external calls and uses OZ guards.
contract PredictionMarket is Ownable, ReentrancyGuard {
    /// ------------------------------------------------------------
    /// Errors
    /// ------------------------------------------------------------
    error InvalidDuration();
    error InvalidTarget();
    error InvalidFinalPrice();
    error MarketNotFound();
    error MarketExpired();
    error MarketNotExpired();
    error MarketNotResolved();
    error MarketAlreadyResolved();
    error BetTooSmall();
    error AlreadyPlacedBet();
    error NoBetPlaced();
    error AlreadyClaimed();
    error NotWinner();

    /// ------------------------------------------------------------
    /// Data structures
    /// ------------------------------------------------------------
    struct Market {
        string symbol; // Asset symbol (e.g., "TSLA")
        uint256 targetPrice; // Target price in USD cents
        uint256 deadline; // Unix timestamp for market expiration
        uint256 totalUpBets; // Total ETH bet on UP
        uint256 totalDownBets; // Total ETH bet on DOWN
        bool resolved; // Has the market been resolved?
        bool outcome; // true = price went UP, false = DOWN
        uint256 finalPrice; // Final price when resolved (USD cents)
    }

    struct Bet {
        uint256 amount;
        bool prediction; // true = UP, false = DOWN
        bool claimed;
    }

    /// ------------------------------------------------------------
    /// Storage
    /// ------------------------------------------------------------
    uint256 public marketCounter;
    mapping(uint256 => Market) public markets;
    mapping(uint256 => mapping(address => Bet)) public bets;
    mapping(uint256 => address[]) public participants; // helpful for indexing off-chain

    uint256 public constant MIN_BET = 0.001 ether;
    uint256 public constant FEE_PERCENTAGE = 2; // 2% platform fee

    /// ------------------------------------------------------------
    /// Events
    /// ------------------------------------------------------------
    event MarketCreated(uint256 indexed marketId, string symbol, uint256 targetPrice, uint256 deadline);
    event BetPlaced(uint256 indexed marketId, address indexed user, uint256 amount, bool prediction);
    event MarketResolved(uint256 indexed marketId, bool outcome, uint256 finalPrice);
    event WinningsClaimed(uint256 indexed marketId, address indexed user, uint256 amount);
    event FeesWithdrawn(address indexed to, uint256 amount);

    /// ------------------------------------------------------------
    /// Modifiers
    /// ------------------------------------------------------------
    modifier validMarket(uint256 _marketId) {
        if (_marketId >= marketCounter) revert MarketNotFound();
        _;
    }

    constructor() Ownable(msg.sender) {}

    /// @notice Create a new prediction market.
    /// @param _symbol Asset symbol (e.g., "TSLA").
    /// @param _targetPrice Target price in USD cents.
    /// @param _durationHours Duration the market stays open, in hours (1-168).
    function createMarket(
        string memory _symbol,
        uint256 _targetPrice,
        uint256 _durationHours
    ) external onlyOwner returns (uint256) {
        if (_durationHours == 0 || _durationHours > 168) revert InvalidDuration();
        if (_targetPrice == 0) revert InvalidTarget();

        uint256 marketId = marketCounter;
        unchecked {
            marketCounter = marketCounter + 1;
        }

        markets[marketId] = Market({
            symbol: _symbol,
            targetPrice: _targetPrice,
            deadline: block.timestamp + (_durationHours * 1 hours),
            totalUpBets: 0,
            totalDownBets: 0,
            resolved: false,
            outcome: false,
            finalPrice: 0
        });

        emit MarketCreated(marketId, _symbol, _targetPrice, markets[marketId].deadline);
        return marketId;
    }

    /// @notice Place a bet on whether the price will be above the target at expiry.
    /// @param _marketId ID of the market.
    /// @param _prediction true for UP, false for DOWN.
    function placeBet(uint256 _marketId, bool _prediction) external payable nonReentrant validMarket(_marketId) {
        Market storage market = markets[_marketId];
        if (block.timestamp >= market.deadline) revert MarketExpired();
        if (market.resolved) revert MarketAlreadyResolved();
        if (msg.value < MIN_BET) revert BetTooSmall();

        Bet storage userBet = bets[_marketId][msg.sender];
        if (userBet.amount != 0) revert AlreadyPlacedBet();

        userBet.amount = msg.value;
        userBet.prediction = _prediction;

        participants[_marketId].push(msg.sender);

        if (_prediction) {
            market.totalUpBets += msg.value;
        } else {
            market.totalDownBets += msg.value;
        }

        emit BetPlaced(_marketId, msg.sender, msg.value, _prediction);
    }

    /// @notice Resolve a market after expiry with the observed final price.
    /// @param _marketId ID of the market.
    /// @param _finalPrice Final price in USD cents.
    function resolveMarket(uint256 _marketId, uint256 _finalPrice) external onlyOwner validMarket(_marketId) {
        Market storage market = markets[_marketId];
        if (block.timestamp < market.deadline) revert MarketNotExpired();
        if (market.resolved) revert MarketAlreadyResolved();
        if (_finalPrice == 0) revert InvalidFinalPrice();

        market.resolved = true;
        market.finalPrice = _finalPrice;
        market.outcome = _finalPrice > market.targetPrice;

        emit MarketResolved(_marketId, market.outcome, _finalPrice);
    }

    /// @notice Claim winnings for a resolved market. Callable by the bettor.
    function claimWinnings(uint256 _marketId) external nonReentrant validMarket(_marketId) returns (uint256) {
        return _claim(_marketId, msg.sender);
    }

    /// @notice Alias for claimWinnings to match “settleBet” semantics.
    function settleBet(uint256 _marketId) external nonReentrant validMarket(_marketId) returns (uint256) {
        return _claim(_marketId, msg.sender);
    }

    /// @dev Internal claim logic reused by both claim entrypoints.
    function _claim(uint256 _marketId, address _user) internal returns (uint256) {
        Market storage market = markets[_marketId];
        if (!market.resolved) revert MarketNotResolved();

        Bet storage bet = bets[_marketId][_user];
        if (bet.amount == 0) revert NoBetPlaced();
        if (bet.claimed) revert AlreadyClaimed();
        if (bet.prediction != market.outcome) revert NotWinner();

        bet.claimed = true;

        uint256 totalPool = market.totalUpBets + market.totalDownBets;
        uint256 winningPool = market.outcome ? market.totalUpBets : market.totalDownBets;
        // winningPool cannot be zero when there is a winning bet, but guard anyway
        if (winningPool == 0) revert InvalidFinalPrice();

        uint256 winnings = (bet.amount * totalPool) / winningPool;
        uint256 fee = (winnings * FEE_PERCENTAGE) / 100;
        uint256 payout = winnings - fee;

        (bool sent, ) = _user.call{value: payout}("");
        require(sent, "Transfer failed");

        emit WinningsClaimed(_marketId, _user, payout);
        return payout;
    }

    /// @notice Get market information.
    function getMarketInfo(
        uint256 _marketId
    )
        external
        view
        validMarket(_marketId)
        returns (
            string memory symbol,
            uint256 targetPrice,
            uint256 deadline,
            uint256 totalUpBets,
            uint256 totalDownBets,
            bool resolved,
            bool outcome,
            uint256 finalPrice
        )
    {
        Market storage market = markets[_marketId];
        return (
            market.symbol,
            market.targetPrice,
            market.deadline,
            market.totalUpBets,
            market.totalDownBets,
            market.resolved,
            market.outcome,
            market.finalPrice
        );
    }

    /// @notice Return user bet details for a given market.
    function getUserBet(
        uint256 _marketId,
        address _user
    ) external view validMarket(_marketId) returns (uint256 amount, bool prediction, bool claimed) {
        Bet storage bet = bets[_marketId][_user];
        return (bet.amount, bet.prediction, bet.claimed);
    }

    /// @notice Withdraw platform fees to the owner.
    function withdrawFees() external onlyOwner nonReentrant {
        uint256 balance = address(this).balance;
        (bool sent, ) = owner().call{value: balance}("");
        require(sent, "Withdraw failed");
        emit FeesWithdrawn(owner(), balance);
    }
}
