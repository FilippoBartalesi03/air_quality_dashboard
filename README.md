# Air Quality Monitor

Mini-app per monitorare la qualità dell'aria dalle stazioni ZeroC.

## Versioni Python e Node.js utilizzate

- **Python**: 3.14.0
- **Node.js**: 18+

## Avvio Backend

```bash
cd backend
../source/bin/python app.py
```

Il backend sarà disponibile su: **http://localhost:5001**

### Variabili d'ambiente Backend

- `BACKEND_PORT`: Porta del server (default: `5001`)
- `API_BASE_URL`: URL base API upstream (default: `https://api.zeroc.green/v1`)

## Avvio Frontend

```bash
cd frontend
npm run dev
```

Il frontend sarà disponibile su: **http://localhost:3000**

### Variabili d'ambiente Frontend

- `BACKEND_URL`: URL del backend `http://localhost:3000`


