# System Architecture

This document describes the architecture of the Forex Prediction Analytics Platform.

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FOREX ANALYTICS PLATFORM                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐              │
│  │   Frontend   │      │   Backend    │      │   Database   │              │
│  │   (Next.js)  │◄────►│  (FastAPI)   │◄────►│ (PostgreSQL) │              │
│  │   Port 3000  │ REST │   Port 8000  │  SQL │   Port 5432  │              │
│  └──────────────┘      └──────────────┘      └──────────────┘              │
│         │                     │                                             │
│         │                     ▼                                             │
│         │              ┌──────────────┐                                    │
│         │              │  ML Models   │                                    │
│         │              │ (TensorFlow) │                                    │
│         │              │  CNN/RNN/TCN │                                    │
│         │              └──────────────┘                                    │
│         │                     │                                             │
│         │                     ▼                                             │
│         │              ┌──────────────┐                                    │
│         │              │  Model Files │                                    │
│         │              │  (.h5/.json) │                                    │
│         │              └──────────────┘                                    │
│         │                                                                   │
│         ▼                                                                   │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         Docker Compose                                │  │
│  │   Orchestrates all services with networking and volume management    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (Next.js 14)

**Purpose**: Provides the user interface for interacting with the prediction system.

**Technology Stack**:
- Next.js 14 with App Router
- React 18 with TypeScript
- Tailwind CSS for styling
- shadcn/ui component library
- Recharts for data visualization

**Key Features**:
- Server-side rendering for SEO and performance
- Centralized API client for backend communication
- Real-time chart updates
- Responsive dashboard design

**Directory Structure**:
```
frontend/src/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Dashboard home
│   ├── predictions/       # Predictions view
│   ├── backtest/          # Backtesting interface
│   └── layout.tsx         # Root layout
├── components/
│   ├── ui/                # Base UI components (shadcn/ui)
│   ├── charts/            # Chart components
│   │   ├── PriceChart.tsx
│   │   └── PerformanceChart.tsx
│   ├── PredictionForm.tsx
│   ├── BacktestForm.tsx
│   └── TradeTable.tsx
├── lib/
│   └── api.ts             # Centralized API client
└── hooks/
    ├── usePrediction.ts
    └── useBacktest.ts
```

### Backend (FastAPI)

**Purpose**: Provides REST API for predictions, backtesting, and data management.

**Technology Stack**:
- FastAPI for high-performance async API
- SQLAlchemy 2.0 for ORM
- Pydantic v2 for data validation
- TensorFlow/Keras for ML inference
- Alembic for database migrations

**Key Features**:
- OpenAPI documentation auto-generation
- Async database operations
- Model hot-reloading
- Comprehensive error handling

**Directory Structure**:
```
backend/app/
├── main.py                 # FastAPI application entry
├── api/
│   ├── routes/
│   │   ├── predictions.py  # Prediction endpoints
│   │   ├── trades.py       # Trade management
│   │   ├── indicators.py   # Technical indicators
│   │   └── models.py       # Model management
│   └── dependencies.py     # Dependency injection
├── ml/
│   ├── base_model.py       # Abstract model interface
│   ├── cnn_model.py        # CNN implementation
│   ├── rnn_model.py        # RNN/LSTM implementation
│   ├── tcn_model.py        # TCN implementation
│   └── inference.py        # Inference engine
├── indicators/
│   └── technical.py        # 28 technical indicators
├── trading/
│   └── simulator.py        # Backtesting engine
├── db/
│   ├── database.py         # Database connection
│   ├── models.py           # SQLAlchemy models
│   └── schemas.py          # Pydantic schemas
├── core/
│   └── config.py           # Configuration
└── tests/
    ├── conftest.py         # Test fixtures
    ├── test_predictions.py
    ├── test_trades.py
    └── test_integration.py
```

### Database (PostgreSQL)

**Purpose**: Persistent storage for predictions, trades, and backtesting results.

**Schema Design**:

```sql
┌─────────────────────┐     ┌─────────────────────┐
│     predictions     │     │       trades        │
├─────────────────────┤     ├─────────────────────┤
│ id (UUID, PK)       │     │ id (UUID, PK)       │
│ currency_pair       │◄────│ prediction_id (FK)  │
│ timeframe           │     │ entry_price         │
│ predicted_price     │     │ exit_price          │
│ predicted_direction │     │ profit_loss         │
│ confidence          │     │ status              │
│ model_type          │     │ created_at          │
│ model_version       │     │ closed_at           │
│ created_at          │     └─────────────────────┘
└─────────────────────┘
         │
         │
         ▼
┌─────────────────────┐     ┌─────────────────────┐
│   backtest_runs     │     │   market_data       │
├─────────────────────┤     ├─────────────────────┤
│ id (UUID, PK)       │     │ id (BIGSERIAL, PK)  │
│ parameters (JSON)   │     │ currency_pair       │
│ results (JSON)      │     │ timeframe           │
│ created_at          │     │ timestamp           │
└─────────────────────┘     │ open, high, low     │
                            │ close, volume       │
                            └─────────────────────┘
```

**Environment Support**:
- **Development**: SQLite for simplicity
- **Production**: PostgreSQL for performance and reliability

### ML Models

**Model Types**:

1. **CNN (Convolutional Neural Network)**
   - Input: 28x28x1 images (28 timeframes × 28 indicators)
   - Architecture: 3 Conv blocks (16→32→64 filters) + Dense layers
   - Output: Single price prediction

2. **RNN (LSTM)**
   - Input: Sequence of 28 timesteps
   - Architecture: 2 stacked LSTM layers (128 units each)
   - Output: Single price prediction

3. **TCN (Temporal Convolutional Network)**
   - Input: 784-dimensional flattened vector
   - Architecture: 7 layers with dilated convolutions
   - Output: Single price prediction

**Model Storage**:
```
models/
├── CNN/
│   ├── CNN_architecture.json
│   └── CNN_weights.h5
├── RNN/
│   ├── RNN_architecture.json
│   └── RNN_weights.h5
└── TCN/
    ├── TCN_architecture.json
    └── TCN_weights.h5
```

## Data Flow

### Prediction Flow

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Client  │───►│ Frontend │───►│ Backend  │───►│ ML Model │
│          │    │          │    │          │    │          │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     ▲               │               │               │
     │               │               ▼               │
     │               │         ┌──────────┐         │
     │               │         │ Database │◄────────┘
     │               │         │          │  (store prediction)
     │               │         └──────────┘
     │               │               │
     └───────────────┴───────────────┘
              (response with prediction)
```

1. User submits prediction request via frontend
2. Frontend sends POST to `/api/predictions`
3. Backend loads appropriate ML model
4. Model generates prediction from input data
5. Prediction stored in database
6. Response returned to frontend
7. Frontend displays prediction on dashboard

### Backtesting Flow

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Client  │───►│ Frontend │───►│ Backend  │───►│Simulator │
│          │    │          │    │          │    │          │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     ▲                               │               │
     │                               ▼               │
     │                         ┌──────────┐         │
     │                         │ ML Model │◄────────┤
     │                         │          │         │
     │                         └──────────┘         │
     │                               │               │
     │                               ▼               │
     │                         ┌──────────┐         │
     │                         │ Database │◄────────┘
     │                         │          │
     │                         └──────────┘
     │                               │
     └───────────────────────────────┘
               (backtest results)
```

## Containerization

### Docker Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                   (forex-network)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  frontend   │  │   backend   │  │     db      │     │
│  │  (Next.js)  │  │  (FastAPI)  │  │ (PostgreSQL)│     │
│  │   :3000     │  │    :8000    │  │    :5432    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│         │                │                │              │
│         └────────────────┼────────────────┘              │
│                          │                               │
│                    ┌─────────────┐                       │
│                    │   volumes   │                       │
│                    │ postgres_data│                      │
│                    │ model_files │                       │
│                    └─────────────┘                       │
└─────────────────────────────────────────────────────────┘
              │              │
              ▼              ▼
         Host :3000     Host :8000
         (Frontend)     (API Docs)
```

### Service Definitions

| Service | Image | Ports | Dependencies |
|---------|-------|-------|--------------|
| db | postgres:15 | 5432 | - |
| backend | custom (Python 3.11) | 8000 | db |
| frontend | custom (Node 20) | 3000 | backend |

## CI/CD Pipeline

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           GitHub Actions                                  │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                  │
│  │   Trigger   │───►│   CI Jobs   │───►│  CD Jobs    │                  │
│  │ (push/PR)   │    │             │    │             │                  │
│  └─────────────┘    └─────────────┘    └─────────────┘                  │
│                            │                   │                         │
│           ┌────────────────┼───────────────────┤                         │
│           ▼                ▼                   ▼                         │
│    ┌─────────────┐  ┌─────────────┐    ┌─────────────┐                  │
│    │ Lint/Format │  │    Test     │    │   Deploy    │                  │
│    │ - Ruff      │  │ - pytest    │    │ - Railway   │                  │
│    │ - ESLint    │  │ - Jest      │    │ - Render    │                  │
│    │ - mypy      │  │ - Coverage  │    │             │                  │
│    └─────────────┘  └─────────────┘    └─────────────┘                  │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

### Railway Deployment

```
┌─────────────────────────────────────────────────────────┐
│                    Railway Project                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  Frontend   │  │   Backend   │  │  PostgreSQL │     │
│  │  Service    │  │   Service   │  │   Plugin    │     │
│  │             │  │             │  │             │     │
│  │ forex.up.   │  │ api.forex.  │  │ (internal)  │     │
│  │ railway.app │  │ up.railway. │  │             │     │
│  │             │  │ app         │  │             │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Environment Variables

| Service | Variable | Description |
|---------|----------|-------------|
| Backend | DATABASE_URL | PostgreSQL connection string |
| Backend | SECRET_KEY | JWT signing key |
| Backend | MODEL_PATH | Path to model files |
| Frontend | NEXT_PUBLIC_API_URL | Backend API URL |

## Security Considerations

1. **API Security**: JWT-based authentication for protected endpoints
2. **CORS**: Configured to allow only trusted origins
3. **Input Validation**: Pydantic schemas validate all inputs
4. **SQL Injection**: SQLAlchemy ORM prevents injection attacks
5. **Secrets Management**: Environment variables for sensitive data

## Performance Optimizations

1. **Model Caching**: ML models loaded once at startup
2. **Database Pooling**: Connection pool for PostgreSQL
3. **Async Operations**: Non-blocking I/O for API endpoints
4. **Frontend Caching**: Next.js static generation where possible
5. **Docker Layer Caching**: Optimized Dockerfiles for faster builds

## Monitoring & Observability

- **Health Checks**: `/health` endpoint for container orchestration
- **Logging**: Structured JSON logging with request tracing
- **Metrics**: Prometheus-compatible metrics endpoint (planned)
- **Error Tracking**: Sentry integration (planned)
