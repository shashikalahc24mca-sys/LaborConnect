## LaborConnect Backend (FastAPI)

This backend powers the LaborConnect mobile app. It exposes REST endpoints for:

- **Worker listing and profiles**
- **Worker creation and updates**
- **A simple rule-based recommendation endpoint**

### Tech stack

- **FastAPI** for the HTTP API.
- **Firebase Admin SDK** + **Realtime Database** for worker storage.
- **Python** with `uvicorn` for the development server.

### Setup

1. **Create a Firebase project**
   - Enable **Realtime Database** in *test mode* for local development.

2. **Use a Service Account key (not the client config)**
   - The **backend** needs a **Service Account** JSON file. This is **not** the same as:
     - `google-services.json` (Android/client config), or
     - The web config (`apiKey`, `authDomain`, etc.) used in the app.
   - To get the correct file:
     1. Open [Firebase Console](https://console.firebase.google.com) → your project.
     2. Go to **Project settings** (gear) → **Service accounts**.
     3. Click **Generate new private key** and download the JSON.
   - That file contains `"type": "service_account"` and a `private_key`. Set `FIREBASE_CREDENTIALS_PATH` in `.env` to its **absolute path**.

3. **Create a `.env` file**

   At the repository root (next to this `backend` directory), create a `.env` file based on `.env.example`:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set:

   - `FIREBASE_CREDENTIALS_PATH` – absolute path to your **Service Account** JSON (see step 2).
   - `FIREBASE_DB_URL` – your Realtime Database URL (e.g. `https://laborconnect-48765-default-rtdb.firebaseio.com`).
   - `CORS_ORIGINS` – comma-separated origins allowed to call this API (defaults include `http://localhost:8081`, `http://localhost:3000`).

4. **Install dependencies**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

5. **Run the server**

   Use `uvicorn` on a non-5000 port (here we use `8010` to avoid common reserved/conflicting ports on Windows):

   ```bash
   uvicorn backend.main:app --reload --port 8010
   ```

6. **API overview**

- `GET /health` – health check.
- `GET /workers/` – list all workers.
- `POST /workers/` – create a worker (`name`, `skill`, `rating`, `availability`, optional `owner_uid`).
- `GET /workers/{worker_id}` – fetch worker details.
- `PUT /workers/{worker_id}` – update worker fields.
- `DELETE /workers/{worker_id}` – delete a worker (useful during development).
- `GET /workers/recommend?skill=Carpenter&limit=5` – **recommendation endpoint**.

### Recommendation algorithm

The `/workers/recommend` endpoint behaves like a basic machine-learning recommendation system using a clear set of rules:

1. Fetch all workers from Firebase Realtime Database.
2. **Filter** workers whose `skill` matches the requested `skill` (case-insensitive).
3. **Sort** the filtered workers by:
   - Higher **rating** first.
   - Then by **availability** – `Available` workers come before others.
   - Then by **created_at** timestamp – newer profiles first.
4. Return the top `limit` workers (default `5`).

This makes the behavior easy to understand and explain to stakeholders while still feeling like a simple ML-style ranking system.
