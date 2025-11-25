import { useState } from 'react'
import { api } from '../api'

interface MarketInfoCardProps {
  disabled?: boolean
}

export default function MarketInfoCard({ disabled }: MarketInfoCardProps) {
  const [marketId, setMarketId] = useState('0')
  const [loading, setLoading] = useState(false)
  const [claiming, setClaiming] = useState(false)
  const [marketInfo, setMarketInfo] = useState<string | null>(null)
  const [message, setMessage] = useState<{ text: string; success: boolean } | null>(null)

  const handleGetInfo = async () => {
    if (disabled) return

    setLoading(true)
    setMessage(null)

    try {
      const response = await api.getMarket(parseInt(marketId))
      setMarketInfo(response.response)
    } catch (err) {
      setMessage({ text: 'Failed to get market info', success: false })
    } finally {
      setLoading(false)
    }
  }

  const handleClaim = async () => {
    if (disabled) return

    setClaiming(true)
    setMessage(null)

    try {
      const response = await api.claimWinnings(parseInt(marketId))
      setMessage({ text: response.response, success: response.success })
    } catch (err) {
      setMessage({ text: 'Failed to claim winnings', success: false })
    } finally {
      setClaiming(false)
    }
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">📋 Market Info</h2>
      </div>

      <div className="form-group">
        <label className="form-label">Market ID</label>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <input
            type="number"
            className="form-input"
            value={marketId}
            onChange={e => setMarketId(e.target.value)}
            disabled={disabled}
            min="0"
            style={{ flex: 1 }}
          />
          <button 
            className="btn btn-primary"
            onClick={handleGetInfo}
            disabled={disabled || loading}
          >
            {loading ? '...' : '🔍 Get Info'}
          </button>
        </div>
      </div>

      {marketInfo && (
        <div style={{ 
          background: 'var(--bg-tertiary)', 
          padding: '1rem', 
          borderRadius: '10px',
          marginTop: '1rem',
          whiteSpace: 'pre-wrap',
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: '0.85rem',
        }}>
          {marketInfo}
        </div>
      )}

      <button
        className="btn btn-success"
        onClick={handleClaim}
        disabled={disabled || claiming}
        style={{ width: '100%', marginTop: '1rem' }}
      >
        {claiming ? 'Claiming...' : '💰 Claim Winnings'}
      </button>

      {message && (
        <div className={`response-message ${message.success ? 'success' : 'error'}`}>
          {message.text}
        </div>
      )}
    </div>
  )
}

