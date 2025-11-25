import { useState, useEffect } from 'react'
import { api } from '../api'

const SYMBOLS = ['BTC', 'ETH', 'SOL']

export default function PriceCard() {
  const [prices, setPrices] = useState<Record<string, number>>({})
  const [loading, setLoading] = useState(true)
  const [selectedSymbol, setSelectedSymbol] = useState('BTC')

  useEffect(() => {
    loadPrices()
    const interval = setInterval(loadPrices, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  const loadPrices = async () => {
    setLoading(true)
    const newPrices: Record<string, number> = {}
    
    for (const symbol of SYMBOLS) {
      try {
        const data = await api.getPrice(symbol)
        newPrices[symbol] = data.price
      } catch {
        newPrices[symbol] = 0
      }
    }
    
    setPrices(newPrices)
    setLoading(false)
  }

  const formatPrice = (price: number) => {
    if (price >= 1000) {
      return price.toLocaleString('en-US', { maximumFractionDigits: 0 })
    }
    return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">📊 Live Prices</h2>
        <button className="btn btn-outline btn-sm" onClick={loadPrices} disabled={loading}>
          {loading ? '...' : '↻'}
        </button>
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        {SYMBOLS.map(symbol => (
          <button
            key={symbol}
            className={`btn btn-sm ${selectedSymbol === symbol ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setSelectedSymbol(symbol)}
          >
            {symbol}
          </button>
        ))}
      </div>

      <div className="price-display">
        <span className="price-value">
          ${loading ? '...' : formatPrice(prices[selectedSymbol] || 0)}
        </span>
        <span className="price-symbol">USD</span>
      </div>

      <div className="market-stats" style={{ marginTop: '1.5rem' }}>
        {SYMBOLS.filter(s => s !== selectedSymbol).map(symbol => (
          <div key={symbol} className="stat-item">
            <div className="stat-label">{symbol}</div>
            <div className="stat-value">
              ${loading ? '...' : formatPrice(prices[symbol] || 0)}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

