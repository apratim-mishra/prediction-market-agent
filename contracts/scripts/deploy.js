const fs = require("fs");
const path = require("path");
const hre = require("hardhat");

async function main() {
  try {
    const [deployer] = await hre.ethers.getSigners();
    const network = hre.network.name;

    console.log("---- Deploying PredictionMarket ----");
    console.log("Network:", network);
    console.log("Deployer:", await deployer.getAddress());

    const PredictionMarket = await hre.ethers.getContractFactory("PredictionMarket");
    const predictionMarket = await PredictionMarket.deploy();
    await predictionMarket.waitForDeployment();

    const address = await predictionMarket.getAddress();
    console.log("PredictionMarket deployed to:", address);

    // Seed initial market if desired
    const initialSymbol = process.env.INITIAL_SYMBOL || "TSLA";
    const initialTargetCents = parseInt(process.env.INITIAL_TARGET_CENTS || "28000", 10);
    const initialDurationHours = parseInt(process.env.INITIAL_DURATION_HOURS || "24", 10);

    console.log(`Creating initial ${initialSymbol} market...`);
    const tx = await predictionMarket.createMarket(initialSymbol, initialTargetCents, initialDurationHours);
    await tx.wait();
    console.log("Initial market created in tx:", tx.hash);

    // Persist deployment info
    const outputPath = path.join(__dirname, "..", "deployments.json");
    const existing = fs.existsSync(outputPath) ? JSON.parse(fs.readFileSync(outputPath, "utf8")) : {};
    existing[network] = {
      address,
      initialMarket: {
        symbol: initialSymbol,
        targetPriceCents: initialTargetCents,
        durationHours: initialDurationHours,
      },
      deployer: await deployer.getAddress(),
      timestamp: Date.now(),
      txHash: predictionMarket.deploymentTransaction().hash,
    };
    fs.writeFileSync(outputPath, JSON.stringify(existing, null, 2));
    console.log(`Saved deployment info to ${outputPath}`);

    return address;
  } catch (error) {
    console.error("Deployment failed:", error);
    process.exitCode = 1;
  }
}

main();
