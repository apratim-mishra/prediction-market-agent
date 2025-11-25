const API_BASE = '/api';

export interface WalletInfo {
  address: string;
  network: string;
  balance?: string;
}

export interface PriceResponse {
  symbol: string;
  price: number;
  source: string;
}

export interface ChatResponse {
  response: string;
  success: boolean;
}

export interface HealthResponse {
  status: string;
  agent_ready: boolean;
  network: string;
}

export interface CreateMarketParams {
  symbol: string;
  target_price: number;
  duration_hours: number;
}

export interface PlaceBetParams {
  market_id: number;
  prediction: 'UP' | 'DOWN';
  amount_eth: number;
}

class ApiClient {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || 'Request failed');
    }

    return response.json();
  }

  async getHealth(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health');
  }

  async getWallet(): Promise<WalletInfo> {
    return this.request<WalletInfo>('/wallet');
  }

  async getPrice(symbol: string): Promise<PriceResponse> {
    return this.request<PriceResponse>(`/price/${symbol}`);
  }

  async chat(message: string): Promise<ChatResponse> {
    return this.request<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  }

  async createMarket(params: CreateMarketParams): Promise<ChatResponse> {
    return this.request<ChatResponse>('/market/create', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async placeBet(params: PlaceBetParams): Promise<ChatResponse> {
    return this.request<ChatResponse>('/market/bet', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async getMarket(marketId: number): Promise<ChatResponse> {
    return this.request<ChatResponse>(`/market/${marketId}`);
  }

  async claimWinnings(marketId: number): Promise<ChatResponse> {
    return this.request<ChatResponse>(`/market/${marketId}/claim`, {
      method: 'POST',
    });
  }

  async requestFaucet(): Promise<ChatResponse> {
    return this.request<ChatResponse>('/faucet', {
      method: 'POST',
    });
  }
}

export const api = new ApiClient();

