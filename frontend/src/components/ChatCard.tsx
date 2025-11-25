import { useState, useRef, useEffect } from 'react'
import { api } from '../api'

interface Message {
  role: 'user' | 'agent'
  content: string
}

interface ChatCardProps {
  disabled?: boolean
}

export default function ChatCard({ disabled }: ChatCardProps) {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'agent', content: 'Hello! I can help you interact with the prediction market. Try asking about your wallet, creating markets, or placing bets.' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || disabled || loading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const response = await api.chat(userMessage)
      setMessages(prev => [...prev, { role: 'agent', content: response.response }])
    } catch {
      setMessages(prev => [...prev, { role: 'agent', content: 'Sorry, something went wrong. Please try again.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">💬 Chat with Agent</h2>
        <button 
          className="btn btn-outline btn-sm" 
          onClick={() => setMessages([{ role: 'agent', content: 'Chat cleared. How can I help you?' }])}
        >
          Clear
        </button>
      </div>

      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-message ${msg.role}`}>
              {msg.content}
            </div>
          ))}
          {loading && (
            <div className="chat-message agent">
              <div className="spinner" style={{ width: '16px', height: '16px', display: 'inline-block', marginRight: '0.5rem' }}></div>
              Thinking...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="chat-input-row">
          <input
            type="text"
            className="form-input"
            placeholder={disabled ? 'Agent not connected' : 'Ask anything...'}
            value={input}
            onChange={e => setInput(e.target.value)}
            disabled={disabled || loading}
          />
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={disabled || loading || !input.trim()}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  )
}

