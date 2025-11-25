import { useState } from 'react'
import { api, WalletInfo } from '../api'

interface WalletCardProps {
  wallet: WalletInfo | null
  onRefresh: () => void
}

export default function WalletCard({ wallet, onRefresh }: WalletCardProps) {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ text: string; success: boolean } | null>(null)

  const handleFaucet = async () => {
    setLoading(true)
    setMessage(null)
    
    try {
      const response = await api.requestFaucet()
      setMessage({ text: response.response, success: response.success })
    } catch (err) {
      setMessage({ text: 'Failed to request faucet', success: false })
    } finally {
      setLoading(false)
    }
  }

  const copyAddress = () => {
    if (wallet?.address) {
      navigator.clipboard.writeText(wallet.address)
      setMessage({ text: 'Address copied!', success: true })
      setTimeout(() => setMessage(null), 2000)
    }
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">💰 Wallet</h2>
        <button className="btn btn-outline btn-sm" onClick={onRefresh}>
          Refresh
        </button>
      </div>

      {wallet ? (
        <>
          <div className="wallet-address" onClick={copyAddress} style={{ cursor: 'pointer' }}>
            {wallet.address}
          </div>
          
          <div className="wallet-actions">
            <button className="btn btn-primary" onClick={handleFaucet} disabled={loading}>
              {loading ? 'Requesting...' : '🚰 Request Faucet'}
            </button>
            <button className="btn btn-outline" onClick={copyAddress}>
              📋 Copy
            </button>
          </div>
        </>
      ) : (
        <p style={{ color: 'var(--text-muted)' }}>
          Agent not connected. Start the backend to view wallet.
        </p>
      )}

      {message && (
        <div className={`response-message ${message.success ? 'success' : 'error'}`}>
          {message.text}
        </div>
      )}
    </div>
  )
}

