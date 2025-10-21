# Postman Testing Guide for KP MCP Registry

This guide provides step-by-step instructions for testing all API endpoints using Postman.

## 🚀 Prerequisites

1. **Start the Flask server:**
   ```bash
   cd kpmcpg
   uv run python app.py
   ```
   
2. **Verify server is running:**
   - Server should be available at `http://localhost:5000`
   - Look for "🔧 Running in DEVELOPMENT MODE with mock authentication"

3. **Have sample data (optional):**
   ```bash
   uv run python seed.py
   ```

---

## 📋 Postman Collection Setup

### Base Configuration
- **Base URL**: `http://localhost:5000`
- **Environment Variables** (optional):
  - `base_url`: `http://localhost:5000`
  - `token`: (will be set after getting auth token)

---

## 🧪 Test Sequence

### **Step 1: Health Check** ✅
**Purpose**: Verify API is running and check development mode

**Request:**
- **Method**: `GET`
- **URL**: `{{base_url}}/v0/health`
- **Headers**: None required

**Expected Response:**
```json
{
  "status": "healthy",
  "dev_mode": true,
  "mock_user": "dev@kp.com"
}
```

**✅ Success Criteria:**
- Status: `200 OK`
- `dev_mode`: `true`
- `status`: `"healthy"`

---

### **Step 2: Get Mock Authentication Token** 🎫
**Purpose**: Get JWT token for authenticated endpoints

**Request:**
- **Method**: `GET`
- **URL**: `{{base_url}}/dev/token`
- **Headers**: None required

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_email": "dev@kp.com",
  "expires_in": 3600,
  "usage": "Set as KP_MCP_TOKEN environment variable",
  "example": "export KP_MCP_TOKEN=\"eyJ0eXAiOiJKV1Qi...\""
}
```

**✅ Success Criteria:**
- Status: `200 OK`
- Copy the `access_token` value for next steps

**💡 Tip**: Save the token in Postman environment variable:
- Go to Environment → Add variable
- Name: `token`
- Value: `<paste the access_token here>`

---

### **Step 3: List Servers (No Auth Required)** 📋
**Purpose**: Get all servers in the registry

**Request:**
- **Method**: `GET`
- **URL**: `{{base_url}}/v0/servers`
- **Headers**: None required
- **Query Parameters** (optional):
  - `limit`: `10`
  - `offset`: `0`
  - `q`: `github` (for search)
  - `tools`: `send_message` (for tool filtering)

**Expected Response:**
```json
{
  "servers": [
    {
      "id": "kp.internal.example/github-integration",
      "name": "GitHub Integration",
      "description": "Access GitHub repositories, issues, and pull requests",
      "version": "1.0.0",
      "endpoint": "https://github-mcp.kp.com",
      "tools": [
        {"name": "list_repos", "description": "List user repositories"}
      ],
      "auth_methods": ["bearer"],
      "owner": "platform@kp.com",
      "team": "Platform Team",
      "tags": ["git", "development", "api"],
      "created_at": "2025-10-12T...",
      "updated_at": "2025-10-12T...",
      "is_public": false
    }
  ],
  "total": 3,
  "offset": 0,
  "limit": 20
}
```

**✅ Success Criteria:**
- Status: `200 OK`
- Should see seeded servers if you ran seed.py

---

### **Step 4: Get Specific Server** 🔍
**Purpose**: Get detailed information about a specific server

**Request:**
- **Method**: `GET`
- **URL**: `{{base_url}}/v0/servers/kp.internal.example/github-integration`
- **Headers**: None required

**Expected Response:**
```json
{
  "id": "kp.internal.example/github-integration",
  "name": "GitHub Integration",
  "description": "Access GitHub repositories, issues, and pull requests",
  // ... full server details including metadata
}
```

**✅ Success Criteria:**
- Status: `200 OK` (if server exists)
- Status: `404 Not Found` (if server doesn't exist)

---

### **Step 5: Publish New Server** 📤
**Purpose**: Create a new server (requires authentication)

**Request:**
- **Method**: `POST`
- **URL**: `{{base_url}}/v0/servers`
- **Headers**: 
  ```
  Authorization: Bearer {{token}}
  Content-Type: application/json
  ```
- **Body** (JSON):
```json
{
  "id": "kp.internal.test/postman-server",
  "name": "Postman Test Server",
  "description": "A test server created via Postman",
  "version": "1.0.0",
  "endpoint": "https://postman-test.kp.com",
  "tools": [
    {
      "name": "test_endpoint",
      "description": "Test endpoint functionality"
    },
    {
      "name": "validate_data",
      "description": "Validate input data"
    }
  ],
  "auth_methods": ["bearer"],
  "team": "QA Team",
  "tags": ["testing", "postman"],
  "metadata": {
    "name": "Postman Test Server",
    "endpoint": "https://postman-test.kp.com",
    "tools": [
      {"name": "test_endpoint"},
      {"name": "validate_data"}
    ],
    "auth_methods": ["bearer"]
  }
}
```

**Expected Response:**
```json
{
  "id": "kp.internal.test/postman-server",
  "message": "Published"
}
```

**✅ Success Criteria:**
- Status: `201 Created`
- Response contains the server ID

**❌ Common Errors:**
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Invalid namespace or ownership issue
- `400 Bad Request`: Invalid JSON or missing required fields

---

### **Step 6: Update Server** ✏️
**Purpose**: Update an existing server (requires authentication)

**Request:**
- **Method**: `PUT`
- **URL**: `{{base_url}}/v0/servers/kp.internal.test/postman-server`
- **Headers**:
  ```
  Authorization: Bearer {{token}}
  Content-Type: application/json
  ```
- **Body** (JSON):
```json
{
  "version": "1.1.0",
  "description": "Updated test server created via Postman",
  "tags": ["testing", "postman", "updated"]
}
```

**Expected Response:**
```json
{
  "message": "Updated"
}
```

**✅ Success Criteria:**
- Status: `200 OK`
- Server should be updated (verify with GET request)

---

### **Step 7: Alternative Auth Token Method** 🔐
**Purpose**: Test the standard auth endpoint

**Request:**
- **Method**: `POST`
- **URL**: `{{base_url}}/auth/token`
- **Headers**: 
  ```
  Content-Type: application/json
  ```
- **Body** (JSON):
```json
{
  "code": "mock-auth-code"
}
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_email": "dev@kp.com",
  "dev_mode": true,
  "message": "Mock token generated for development"
}
```

---

### **Step 8: Search and Filter Tests** 🔍

#### **8a: Text Search**
- **Method**: `GET`
- **URL**: `{{base_url}}/v0/servers?q=github`

#### **8b: Tool Filter**
- **Method**: `GET`
- **URL**: `{{base_url}}/v0/servers?tools=send_message,list_repos`

#### **8c: Pagination**
- **Method**: `GET`
- **URL**: `{{base_url}}/v0/servers?limit=2&offset=1`

#### **8d: Combined Search**
- **Method**: `GET`
- **URL**: `{{base_url}}/v0/servers?q=integration&tools=list_repos&limit=5`

---

### **Step 9: Delete Server** 🗑️
**Purpose**: Remove a server (requires authentication)

**Request:**
- **Method**: `DELETE`
- **URL**: `{{base_url}}/v0/servers/kp.internal.test/postman-server`
- **Headers**:
  ```
  Authorization: Bearer {{token}}
  ```

**Expected Response:**
```json
{
  "message": "Deleted"
}
```

**✅ Success Criteria:**
- Status: `200 OK`
- Server should be removed (verify with GET request returns 404)

---

### **Step 10: Error Testing** ❌

#### **10a: Unauthorized Access**
- Try Step 5 (POST) without Authorization header
- **Expected**: `401 Unauthorized`

#### **10b: Invalid Server ID**
- **Method**: `GET`
- **URL**: `{{base_url}}/v0/servers/invalid-server-id`
- **Expected**: `404 Not Found`

#### **10c: Invalid JSON**
- Try Step 5 (POST) with malformed JSON
- **Expected**: `400 Bad Request`

#### **10d: Invalid Namespace**
- Try Step 5 (POST) with ID starting with `invalid.namespace/test`
- **Expected**: `403 Forbidden`

---

## 📊 Testing Checklist

- [ ] **Health Check**: API is running in dev mode
- [ ] **Get Token**: Successfully obtained JWT token
- [ ] **List Servers**: Can retrieve server list
- [ ] **Get Server**: Can retrieve specific server details
- [ ] **Publish Server**: Can create new server with auth
- [ ] **Update Server**: Can modify existing server
- [ ] **Delete Server**: Can remove server
- [ ] **Search**: Text search works
- [ ] **Filter**: Tool filtering works
- [ ] **Pagination**: Limit/offset works
- [ ] **Error Handling**: Proper error responses

---

## 🔧 Troubleshooting

### **Server Not Starting:**
```bash
cd kpmcpg
uv run python app.py
```
Look for: "🔧 Running in DEVELOPMENT MODE"

### **Token Issues:**
- Make sure to copy the full `access_token` value
- Check that Authorization header format is: `Bearer <token>`
- Tokens expire after 1 hour, get a new one if needed

### **404 Errors:**
- Check that server is running on `http://localhost:5000`
- Verify endpoint URLs are correct
- For server-specific endpoints, ensure the server exists

### **Database Issues:**
- Run `uv run python seed.py` to populate test data
- Check MongoDB connection in console output

---

## 📁 Postman Collection Export

You can import this as a Postman collection by creating these requests manually or using the Postman API to import them programmatically.

**Recommended Testing Order:**
1. Health → Get Token → List → Get Specific → Publish → Update → Delete
2. Then test search/filter variations
3. Finally test error scenarios

Happy testing! 🎉
