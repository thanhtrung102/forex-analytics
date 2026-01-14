# Forex Prediction Analytics Platform

A full-stack data engineering application for forex market prediction using deep learning models. This system provides real-time predictions, backtesting capabilities, and comprehensive trading analytics through an intuitive dashboard.

## Problem Statement

Foreign exchange (forex) markets are highly volatile and complex, making accurate price prediction challenging. Traditional technical analysis methods often fail to capture the intricate patterns in financial time series data. This platform addresses these challenges by:

1. **Leveraging Deep Learning**: Utilizing CNN, RNN (LSTM), and Temporal Convolutional Networks (TCN) to capture complex temporal patterns in forex data
2. **Providing Real-time Predictions**: Exposing trained models via a REST API for on-demand price predictions
3. **Enabling Backtesting**: Simulating trading strategies on historical data to evaluate model performance
4. **Visualizing Results**: Offering an interactive dashboard for monitoring predictions, trades, and performance metrics

## System Functionality

### Core Features

- **Multi-Model Predictions**: Choose from CNN, RNN, or TCN models for price predictions
- **28 Technical Indicators**: Comprehensive feature engineering including EMAs, RSI, MACD, Bollinger Bands, and more
- **Trading Simulation**: Event-based backtesting engine with leverage, margin, and risk management
- **Performance Analytics**: Track win rates, drawdowns, and profit/loss metrics
- **RESTful API**: OpenAPI-compliant endpoints for integration with external systems

### Supported Currency Pairs

EURUSD, GBPUSD, USDJPY, AUDUSD, USDCHF, USDCAD, NZDUSD, EURGBP, EURJPY, GBPJPY, AUDJPY

### Supported Timeframes

1 Minute (M1), 5 Minutes (M5), 15 Minutes (M15), 30 Minutes (M30), 1 Hour (H1), 4 Hours (H4), Daily (D1)

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI (Python 3.11) |
| **Frontend** | Next.js 14 (React, TypeScript) |
| **Database** | PostgreSQL (production), SQLite (development) |
| **ML Framework** | TensorFlow 2.x / Keras |
| **Containerization** | Docker & Docker Compose |
| **CI/CD** | GitHub Actions |
| **Deployment** | Railway / Render |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Run with Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/forex-analytics.git
cd forex-analytics

# Start all services
docker compose up --build

# Access the application
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
# API: http://localhost:8000/api
```

### Local Development

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/models` | GET | List available trained models |
| `/api/models/{model_id}` | GET | Get model metadata |
| `/api/predictions` | POST | Generate price predictions |
| `/api/predictions/{id}` | GET | Get prediction by ID |
| `/api/backtest` | POST | Run trading simulation |
| `/api/backtest/{id}/results` | GET | Get backtest results |
| `/api/indicators/{pair}/{timeframe}` | GET | Calculate technical indicators |
| `/api/trades` | GET | List all trades |
| `/api/metrics` | GET | Get performance metrics |
| `/health` | GET | Health check |

Full API documentation available at `/docs` (Swagger UI) or `/redoc` (ReDoc).

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run only unit tests
pytest -v -m "not integration"

# Run only integration tests
pytest -v -m integration
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

## Project Structure

```
forex-analytics/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── ml/             # ML model wrappers
│   │   ├── indicators/     # Technical indicators
│   │   ├── trading/        # Trading simulation
│   │   ├── db/             # Database models
│   │   ├── core/           # Configuration
│   │   └── tests/          # Test suite
│   ├── alembic/            # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Pages
│   │   ├── components/    # React components
│   │   ├── lib/           # API client
│   │   └── hooks/         # Custom hooks
│   ├── __tests__/         # Test suite
│   ├── package.json
│   └── Dockerfile
├── data/                   # Sample forex data
├── models/                 # Trained model weights
├── docker-compose.yml
├── .github/workflows/      # CI/CD pipelines
├── README.md
├── AGENTS.md              # AI development docs
└── ARCHITECTURE.md        # System architecture
```

## Deployment

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway up
```

### Render

1. Connect your GitHub repository to Render
2. Create a new Web Service for the backend
3. Create a new Static Site for the frontend
4. Add a PostgreSQL database
5. Configure environment variables

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed deployment instructions.

## Environment Variables

### Backend

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./forex.db` |
| `SECRET_KEY` | JWT secret key | (required in production) |
| `CORS_ORIGINS` | Allowed CORS origins | `*` |
| `MODEL_PATH` | Path to trained models | `./models` |

### Frontend

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Original ML research from [PredictionModelsInForexMarkets](https://github.com/alessandrobaldo/PredictionModelsInForexMarkets)
- TensorFlow and Keras teams for the deep learning framework
- FastAPI for the excellent Python web framework
