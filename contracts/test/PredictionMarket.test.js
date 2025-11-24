const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("PredictionMarket", function () {
  const targetPrice = 1_000; // $10.00 in cents
  const durationHours = 1;

  async function deployFixture() {
    const [owner, alice, bob] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("PredictionMarket", owner);
    const contract = await Factory.deploy();
    await contract.waitForDeployment();
    return { contract, owner, alice, bob };
  }

  async function createMarket(contract) {
    const tx = await contract.createMarket("TEST", targetPrice, durationHours);
    await tx.wait();
    return 0;
  }

  async function fastForward(seconds) {
    await ethers.provider.send("evm_increaseTime", [seconds]);
    await ethers.provider.send("evm_mine");
  }

  it("allows placing an UP bet and updates totals", async function () {
    const { contract, alice } = await deployFixture();
    const marketId = await createMarket(contract);

    const value = ethers.parseEther("0.01");
    await expect(contract.connect(alice).placeBet(marketId, true, { value }))
      .to.emit(contract, "BetPlaced")
      .withArgs(marketId, await alice.getAddress(), value, true);

    const market = await contract.getMarketInfo(marketId);
    expect(market.totalUpBets).to.equal(value);
    expect(market.totalDownBets).to.equal(0);
  });

  it("reverts on too-small bet amount", async function () {
    const { contract, alice } = await deployFixture();
    const marketId = await createMarket(contract);
    await expect(contract.connect(alice).placeBet(marketId, false, { value: 0 }))
      .to.be.revertedWithCustomError(contract, "BetTooSmall");
  });

  it("only owner can resolve", async function () {
    const { contract, alice } = await deployFixture();
    const marketId = await createMarket(contract);
    await fastForward(3600 + 1);

    await expect(contract.connect(alice).resolveMarket(marketId, targetPrice + 1))
      .to.be.revertedWithCustomError(contract, "OwnableUnauthorizedAccount")
      .withArgs(alice.address);
  });

  it("pays winner via settleBet after resolution", async function () {
    const { contract, owner, alice, bob } = await deployFixture();
    const marketId = await createMarket(contract);

    const aliceStake = ethers.parseEther("1");
    const bobStake = ethers.parseEther("0.5");

    await contract.connect(alice).placeBet(marketId, true, { value: aliceStake });
    await contract.connect(bob).placeBet(marketId, false, { value: bobStake });

    await fastForward(3600 + 1);
    await contract.connect(owner).resolveMarket(marketId, targetPrice + 100); // outcome UP

    const before = await ethers.provider.getBalance(alice);
    const tx = await contract.connect(alice).settleBet(marketId);
    const receipt = await tx.wait();
    const gasUsed = receipt.gasUsed * receipt.gasPrice;

    const after = await ethers.provider.getBalance(alice);

    const totalPool = aliceStake + bobStake;
    const expectedGross = (aliceStake * totalPool) / aliceStake; // 1.5 ETH
    const fee = (expectedGross * 2n) / 100n; // 2%
    const expectedNet = expectedGross - fee;

    expect(after - before + gasUsed).to.equal(expectedNet);
  });

  it("prevents double claims", async function () {
    const { contract, owner, alice } = await deployFixture();
    const marketId = await createMarket(contract);

    const stake = ethers.parseEther("0.02");
    await contract.connect(alice).placeBet(marketId, true, { value: stake });
    await fastForward(3600 + 1);
    await contract.connect(owner).resolveMarket(marketId, targetPrice + 1);

    await contract.connect(alice).claimWinnings(marketId);
    await expect(contract.connect(alice).claimWinnings(marketId)).to.be.revertedWithCustomError(
      contract,
      "AlreadyClaimed"
    );
  });

  it("reverts resolveMarket before deadline", async function () {
    const { contract, owner } = await deployFixture();
    const marketId = await createMarket(contract);
    await expect(contract.connect(owner).resolveMarket(marketId, targetPrice + 1)).to.be.revertedWithCustomError(
      contract,
      "MarketNotExpired"
    );
  });
});
