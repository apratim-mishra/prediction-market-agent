import { useState } from 'react'
import { api } from '../api'

interface CreateMarketCardProps {
  disabled?: boolean
}

export default function CreateMarketCard({ disabled }: CreateMarketCardProps) {
  const [symbol, setSymbol] = useState('BTC')
  const [targetPrice, setTargetPrice] = useState('')
  const [duration, setDuration] = useState('24')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ text: string; success: boolean } | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!targetPrice || disabled) return

    setLoading(true)
    setMessage(null)

    try {
      const response = await api.createMarket({
        symbol,
        target_price: parseFloat(targetPrice),
        duration_hours: parseInt(duration),
      })
      setMessage({ text: response.response, success: response.success })
      if (response.success) {
        setTargetPrice('')
      }
    } catch (err) {
      setMessage({ text: 'Failed to create market', success: false })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">🎯 Create Market</h2>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Asset Symbol</label>
            <select 
              className="form-input"
              value={symbol}
              onChange={e => setSymbol(e.target.value)}
              disabled={disabled}
            >
              <option value="BTC">Bitcoin (BTC)</option>
              <option value="ETH">Ethereum (ETH)</option>
              <option value="SOL">Solana (SOL)</option>
              <option value="TSLA">Tesla (TSLA)</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Duration (hours)</label>
            <select
              className="form-input"
              value={duration}
              onChange={e => setDuration(e.target.value)}
              disabled={disabled}
            >
              <option value="1">1 hour</option>
              <option value="6">6 hours</option>
              <option value="12">12 hours</option>
              <option value="24">24 hours</option>
              <option value="48">48 hours</option>
              <option value="168">7 days</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Target Price (USD)</label>
          <input
            type="number"
            className="form-input"
            placeholder="e.g., 100000"
            value={targetPrice}
            onChange={e => setTargetPrice(e.target.value)}
            disabled={disabled}
            step="0.01"
            min="0"
          />
        </div>

        <button 
          type="submit" 
          className="btn btn-primary" 
          style={{ width: '100%' }}
          disabled={disabled || loading || !targetPrice}
        >
          {loading ? 'Creating...' : '🚀 Create Market'}
        </button>
      </form>

      {message && (
        <div className={`response-message ${message.success ? 'success' : 'error'}`}>
          {message.text}
        </div>
      )}
    </div>
  )
}

