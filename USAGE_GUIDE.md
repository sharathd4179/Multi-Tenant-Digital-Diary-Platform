# How to Use the Multi-Tenant Diary Assistant

## 🚀 Quick Start

### 1. Access the Application

The application is already running! Access it at:

- **Streamlit Frontend (Web UI)**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Backend API**: http://localhost:8000

---

## 📝 Step-by-Step Usage Guide

### Step 1: Create Your First Tenant (Organization)

Since this is a multi-tenant system, you need to create a tenant first. You can do this via the API:

#### Option A: Using the API Documentation (Easiest)

1. Go to http://localhost:8000/docs
2. Find the `/auth/register-tenant` endpoint
3. Click "Try it out"
4. Generate a UUID for `tenant_id` (you can use an online UUID generator or use this example format)
5. Fill in the request body:

```json
{
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "admin",
  "email": "admin@example.com",
  "password": "admin123",
  "role": "admin"
}
```

6. Click "Execute"
7. Save the `tenant_id` - you'll need it to login!

#### Option B: Using curl (Command Line)

```bash
curl -X POST "http://localhost:8000/auth/register-tenant" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin123",
    "role": "admin"
  }'
```

**Note**: Replace the `tenant_id` with your own UUID. The first user created for a tenant is automatically assigned the `admin` role.

---

### Step 2: Login via Web UI

1. Open http://localhost:8501 in your browser
2. You'll see a login form with three fields:
   - **Tenant ID**: Enter the UUID you used when creating the tenant
   - **Username**: Enter the username you created (e.g., "admin")
   - **Password**: Enter the password you set
3. Click "Login"
4. You'll be redirected to the Dashboard

---

### Step 3: Using the Application Features

Once logged in, you'll see a sidebar with navigation options:

#### 📊 Dashboard
- View statistics: Total notes, total tasks
- See note frequency over time (line chart)
- Quick overview of your activity

#### 📔 Diary
- **View Notes**: See all your diary entries in expandable cards
- **Create New Note**:
  - Enter a title (optional)
  - Write your content (supports markdown)
  - Add tags (comma-separated, e.g., "work, personal, ideas")
  - Click "Create Note"

#### 🔍 Search
- **Semantic Search**: Ask natural language questions
  - Example queries:
    - "What did I write about meetings?"
    - "Show me notes about Python"
    - "What tasks did I mention?"
- **Results**:
  - **Answer**: AI-generated summary based on relevant notes
  - **Top Chunks**: Relevant text snippets with similarity scores
  - **Extracted Tasks**: Automatically identified tasks from your notes

**Note**: Semantic search requires FAISS indexes. If you get an error, you need to build indexes first (see "Building FAISS Indexes" below).

#### ✅ Tasks
- View all tasks extracted from your notes
- Filter by status: "all", "open", or "completed"
- Mark tasks as complete by clicking the "Complete" button

---

## 🔧 Advanced Usage

### Creating Additional Users

To add more users to your tenant:

1. Go to http://localhost:8000/docs
2. Use the `/auth/signup` endpoint
3. Provide:
   - Same `tenant_id` as your organization
   - New `username`, `email`, `password`
   - `role`: "user" or "admin"

**Note**: Only admins can create notes for other users. Regular users can only manage their own notes.

### Using the API Directly

#### Get Your Access Token

First, login to get a token:

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "admin",
    "password": "admin123"
  }'
```

Response will include an `access_token`. Use this in subsequent requests:

```bash
TOKEN="your_access_token_here"
```

#### Create a Note

```bash
curl -X POST "http://localhost:8000/notes/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "your_user_id_from_token",
    "title": "My First Note",
    "content": "This is a test note with some content.",
    "tags": ["test", "demo"]
  }'
```

#### List Notes

```bash
curl -X GET "http://localhost:8000/notes/" \
  -H "Authorization: Bearer $TOKEN"
```

#### Search Notes

```bash
curl -X GET "http://localhost:8000/search/?q=meetings&top_k=5" \
  -H "Authorization: Bearer $TOKEN"
```

#### Get Tasks

```bash
curl -X GET "http://localhost:8000/tasks/" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🗄️ Seeding Demo Data (Optional)

To populate the database with sample data for testing:

1. Make sure the database is running
2. Run the seed script:

```bash
# From the project root directory
cd multi-tenant-diary-assistant
python scripts/seed_demo_data.py
```

This creates:
- 4 sample tenants (Acme Corp, Globex, Umbrella, Initech)
- 5 users per tenant (alice, bob, carol, dave, eve)
- 5 notes per user with sample content
- All users have password: "password"
- "alice" is the admin for each tenant

**Login Example**:
- Tenant ID: (check the database or use one from the seed output)
- Username: `alice`
- Password: `password`

---

## 🔍 Building FAISS Indexes for Semantic Search

Semantic search requires FAISS vector indexes. To build them:

1. Make sure you have notes in the database
2. Set your `OPENAI_API_KEY` in the `.env` file
3. Run the index creation script:

```bash
# From the project root
python scripts/create_faiss_index.py --db-url="postgresql://postgres:postgres@localhost:5432/diarydb" --openai-api-key="your_key_here"
```

Or if using environment variables:

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/diarydb"
export OPENAI_API_KEY="your_key_here"
python scripts/create_faiss_index.py
```

This creates FAISS indexes in the `vector_indexes/` directory for each tenant.

**Note**: The indexes need to be accessible to the backend. If running in Docker, you may need to mount the `vector_indexes/` directory as a volume.

---

## 🧪 Testing the Application

Run the test suite:

```bash
# From the project root
cd multi-tenant-diary-assistant
pytest backend/app/tests/ -v
```

---

## 📚 API Endpoints Summary

### Authentication
- `POST /auth/register-tenant` - Create a new tenant and admin user
- `POST /auth/signup` - Register a new user under existing tenant
- `POST /auth/login` - Login and get JWT tokens

### Notes
- `GET /notes/` - List notes (with filters: date, tags, pagination)
- `POST /notes/` - Create a new note
- `GET /notes/{note_id}` - Get a specific note
- `PUT /notes/{note_id}` - Update a note
- `DELETE /notes/{note_id}` - Delete a note

### Tasks
- `GET /tasks/` - List tasks (filter by status)
- `POST /tasks/{task_id}/complete` - Mark a task as completed

### Search
- `GET /search/?q={query}&top_k={number}` - Semantic search across notes

---

## 🔐 Security Notes

- **JWT Tokens**: All API requests (except login/signup) require a Bearer token in the Authorization header
- **Tenant Isolation**: Users can only access data from their own tenant
- **Role-Based Access**: 
  - Admins can see all notes in their tenant
  - Regular users can only see their own notes
- **Token Expiration**: Access tokens expire after 30 minutes (configurable)

---

## 🐛 Troubleshooting

### "Index for tenant not found" error
- Build FAISS indexes using the script above
- Make sure indexes are in the `vector_indexes/` directory

### "Invalid authentication credentials"
- Check that your token hasn't expired
- Make sure you're using the correct tenant_id
- Verify the token is in the format: `Bearer <token>`

### "Tenant not found"
- Make sure you're using the correct tenant_id UUID
- Verify the tenant exists in the database

### Frontend not loading
- Check that the backend is running: http://localhost:8000/docs
- Verify the frontend container is running: `docker-compose ps`

---

## 💡 Tips

1. **Use UUIDs for tenant_id**: Generate unique UUIDs for each organization
2. **Tags are useful**: Use consistent tags to organize notes (e.g., "work", "personal", "ideas")
3. **Semantic search is powerful**: Ask questions in natural language, not just keywords
4. **Tasks are auto-extracted**: The system automatically finds tasks in your notes
5. **Admins have more access**: Admins can see all notes in their tenant

---

## 📞 Need Help?

- Check the API documentation at http://localhost:8000/docs
- Review the README.md for architecture details
- Check container logs: `docker-compose logs backend` or `docker-compose logs frontend`



