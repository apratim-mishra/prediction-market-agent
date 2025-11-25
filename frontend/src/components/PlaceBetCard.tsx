import { useState } from 'react'
import { api } from '../api'

interface PlaceBetCardProps {
  disabled?: boolean
}

export default function PlaceBetCard({ disabled }: PlaceBetCardProps) {
  const [marketId, setMarketId] = useState('0')
  const [prediction, setPrediction] = useState<'UP' | 'DOWN'>('UP')
  const [amount, setAmount] = useState('0.01')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ text: string; success: boolean } | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (disabled) return

    setLoading(true)
    setMessage(null)

    try {
      const response = await api.placeBet({
        market_id: parseInt(marketId),
        prediction,
        amount_eth: parseFloat(amount),
      })
      setMessage({ text: response.response, success: response.success })
    } catch (err) {
      setMessage({ text: 'Failed to place bet', success: false })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">🎲 Place Bet</h2>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Market ID</label>
            <input
              type="number"
              className="form-input"
              value={marketId}
              onChange={e => setMarketId(e.target.value)}
              disabled={disabled}
              min="0"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Amount (ETH)</label>
            <input
              type="number"
              className="form-input"
              value={amount}
              onChange={e => setAmount(e.target.value)}
              disabled={disabled}
              step="0.001"
              min="0.001"
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Prediction</label>
          <div className="prediction-buttons">
            <button
              type="button"
              className={`prediction-btn up ${prediction === 'UP' ? 'selected' : ''}`}
              onClick={() => setPrediction('UP')}
              disabled={disabled}
            >
              📈 UP
            </button>
            <button
              type="button"
              className={`prediction-btn down ${prediction === 'DOWN' ? 'selected' : ''}`}
              onClick={() => setPrediction('DOWN')}
              disabled={disabled}
            >
              📉 DOWN
            </button>
          </div>
        </div>

        <button 
          type="submit" 
          className="btn btn-primary" 
          style={{ width: '100%' }}
          disabled={disabled || loading}
        >
          {loading ? 'Placing Bet...' : `Place ${prediction} Bet`}
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

