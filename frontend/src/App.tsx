import { useState, useEffect } from 'react'
import { api, WalletInfo, HealthResponse } from './api'
import WalletCard from './components/WalletCard'
import PriceCard from './components/PriceCard'
import CreateMarketCard from './components/CreateMarketCard'
import PlaceBetCard from './components/PlaceBetCard'
import MarketInfoCard from './components/MarketInfoCard'
import ChatCard from './components/ChatCard'

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [wallet, setWallet] = useState<WalletInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const healthData = await api.getHealth()
      setHealth(healthData)
      
      if (healthData.agent_ready) {
        const walletData = await api.getWallet()
        setWallet(walletData)
      }
    } catch (err) {
      setError('Failed to connect to API. Make sure the backend is running.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="app">
        <div className="loading" style={{ minHeight: '100vh' }}>
          <div className="spinner"></div>
          Connecting to agent...
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="header">
        <div className="logo">
          <span className="logo-icon">🎯</span>
          <span>Prediction Market</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span className={`status-indicator ${health?.agent_ready ? 'online' : 'offline'}`}></span>
          <span className="network-badge">{health?.network || 'base-sepolia'}</span>
        </div>
      </header>

      <main className="main">
        {error && (
          <div className="card" style={{ marginBottom: '1.5rem', borderColor: 'var(--accent-red)' }}>
            <p style={{ color: 'var(--accent-red)' }}>⚠️ {error}</p>
            <button className="btn btn-outline btn-sm" onClick={loadInitialData} style={{ marginTop: '1rem' }}>
              Retry Connection
            </button>
          </div>
        )}

        <div className="dashboard-grid">
          <WalletCard wallet={wallet} onRefresh={loadInitialData} />
          <PriceCard />
        </div>

        <div className="dashboard-grid">
          <CreateMarketCard disabled={!health?.agent_ready} />
          <PlaceBetCard disabled={!health?.agent_ready} />
        </div>

        <div className="dashboard-grid">
          <MarketInfoCard disabled={!health?.agent_ready} />
          <ChatCard disabled={!health?.agent_ready} />
        </div>
      </main>

      <footer className="footer">
        Built with Coinbase AgentKit • Base Sepolia Testnet
      </footer>
    </div>
  )
}

export default App

