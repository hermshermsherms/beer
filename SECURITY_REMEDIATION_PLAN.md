# Security Remediation Plan - Beer App

**Date:** 2026-01-03
**Priority:** CRITICAL
**Estimated Time:** 2-4 hours

---

## Executive Summary

This document outlines critical security vulnerabilities discovered in the Beer App and provides a step-by-step remediation plan. **All issues listed are actively exploitable and should be addressed immediately.**

### Critical Issues Found:
1. Exposed Supabase credentials in source code
2. Broken authentication system (forgeable tokens)
3. Weak password hashing (SHA256)
4. Row Level Security (RLS) bypass
5. Anonymous storage uploads enabled

---

## Pre-Remediation Checklist

**⚠️ COMPLETE THESE BEFORE STARTING CODE CHANGES:**

- [ ] **ROTATE SUPABASE CREDENTIALS** **(IN PROGRESS)**
  - Go to Supabase Dashboard → Settings → API
  - Click "Generate new anon key"
  - Save the new credentials securely (password manager)
  - **DO NOT commit these to git**

- [ ] **Audit database access logs** (if available)
  - Check for suspicious queries
  - Look for unusual data access patterns
  - Verify no unauthorized users were created

- [ ] **Review storage bucket**
  - Check for suspicious/unauthorized file uploads
  - Delete any spam or inappropriate content
  - Note storage usage for billing concerns

- [ ] **Backup current database**
  - Export all tables from Supabase
  - Store backup securely offline

---

## Remediation Plan

### Phase 1: Credential Security (IMMEDIATE - 15 minutes) ✅ **COMPLETED**

#### Step 1.1: Remove Hardcoded Credentials ✅ **COMPLETED**

**Files to modify:**
- `/api/all-beers.py` ✅
- `/api/delete-beer.py` ✅
- `/api/beers.py` ✅
- `/api/login.py` ✅
- `/api/leaderboard.py` ✅
- `/api/my-beers.py` ✅
- `/api/register.py` ✅
- `/api/beers/[id].py` ✅
- `/backend/simple_main.py` ✅
- `/frontend/src/config.ts` ✅

**Action:** Replace hardcoded credentials with environment variables. ✅ **COMPLETED**

**Example for `/api/login.py`:**
```python
# BEFORE (INSECURE):
SUPABASE_URL = "https://rczatkqbmclnuwtanonj.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# AFTER (SECURE):
import os
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")
```

**Repeat for all 7 API files.**

#### Step 1.2: Update Frontend Config ✅ **COMPLETED**

**File:** `/frontend/src/config.ts` ✅

```typescript
// BEFORE (INSECURE):
export const SUPABASE_CONFIG = {
  url: 'https://rczatkqbmclnuwtanonj.supabase.co',
  anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
}

// AFTER (SECURE):
export const SUPABASE_CONFIG = {
  url: import.meta.env.VITE_SUPABASE_URL || '',
  anonKey: import.meta.env.VITE_SUPABASE_ANON_KEY || ''
}
```

#### Step 1.3: Configure Environment Variables 🔄 **IN PROGRESS**

**For Vercel (Frontend + API):** 🔄 **NEEDS NEW ROTATED CREDENTIALS**
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add:
   - `SUPABASE_URL` = your_new_supabase_url
   - `SUPABASE_ANON_KEY` = your_new_anon_key
   - `VITE_SUPABASE_URL` = your_new_supabase_url (for frontend build)
   - `VITE_SUPABASE_ANON_KEY` = your_new_anon_key (for frontend build)
3. Apply to: Production, Preview, and Development

**For Local Development:**
Create `/frontend/.env`:
```bash
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
```

**Verify `.gitignore` includes:**
```
.env
.env.*
!.env.example
```

#### Step 1.4: Test After Credential Removal ✅ **COMPLETED**
```bash
# Verify no credentials in code
grep -r "rczatkqbmclnuwtanonj" . --exclude-dir=.git --exclude-dir=node_modules
grep -r "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" . --exclude-dir=.git --exclude-dir=node_modules

# ✅ VERIFIED: Returns NO results (except .env files and this plan document)
```

**✅ Git Commit:** Security fixes committed to main branch (commit: 2854e88)

---

### Phase 2: Fix Authentication System (HIGH PRIORITY - 60-90 minutes) ⏳ **PENDING**

**Decision Point:** Choose ONE authentication approach. ✅ **ANALYSIS COMPLETED - RECOMMEND OPTION A**

**✅ EVALUATION:** Existing `/backend/main.py` already implements secure Supabase Auth with proper JWT validation.

#### Option A: Use Proper Supabase Auth (RECOMMENDED) ✅ **BACKEND READY**

**Advantages:**
- Cryptographically secure JWT tokens
- Built-in token expiration
- Works with RLS policies
- Industry standard

**✅ STATUS:** `/backend/main.py` already implements this correctly!

**Implementation:**

1. **Delete the insecure `/api` directory entirely**
   ```bash
   rm -rf /home/user/beer/api
   ```

2. **Use the existing `/backend/main.py`** (already has correct auth)
   - Already uses `supabase.auth.sign_up()` - line 55
   - Already uses `supabase.auth.sign_in_with_password()` - line 83
   - Already validates tokens properly - line 100

3. **Update deployment to use FastAPI backend**
   - Deploy `backend/main.py` to Railway/Heroku
   - Update Vercel to proxy API calls to Railway

4. **Update database schema** (no changes needed - already correct)

5. **Update frontend** (minimal changes needed)
   - Frontend already expects proper tokens
   - Just update API endpoints if backend URL changes

#### Option B: Fix Custom Auth (NOT RECOMMENDED - Keep only if necessary)

If you must keep the serverless `/api` functions, implement proper JWT signing:

**Install dependencies:**
```bash
pip install pyjwt cryptography
```

**Create `/api/auth_utils.py`:**
```python
import jwt
import os
from datetime import datetime, timedelta

SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY must be set")

def create_token(user_id: str, expiration_hours: int = 24) -> str:
    """Create a cryptographically signed JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=expiration_hours),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token: str) -> dict:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return {'valid': True, 'user_id': payload['user_id']}
    except jwt.ExpiredSignatureError:
        return {'valid': False, 'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'valid': False, 'error': 'Invalid token'}
```

**Update `/api/login.py`:**
```python
from auth_utils import create_token

# In the login handler, replace line 55:
# OLD: "access_token": f"token_{user['id']}"
# NEW:
"access_token": create_token(user['id'])
```

**Update `/api/beers.py` (and all other protected endpoints):**
```python
from auth_utils import verify_token

# Replace lines 129-142:
token = authorization[7:]  # Remove 'Bearer ' prefix
token_data = verify_token(token)

if not token_data['valid']:
    result = {"error": token_data.get('error', 'Invalid token')}
    # ... send 401 response
    return

user_id = token_data['user_id']
```

**Add environment variable:**
- Generate: `openssl rand -hex 32`
- Add `JWT_SECRET_KEY` to Vercel environment variables

---

### Phase 3: Fix Password Hashing (HIGH PRIORITY - 30 minutes)

**Only needed if keeping custom auth (Option B above). Skip if using Supabase Auth.**

#### Step 3.1: Install bcrypt
```bash
pip install bcrypt
```

#### Step 3.2: Update Registration (`/api/register.py`)

```python
import bcrypt

# Replace line 34:
# OLD: password_hash = hashlib.sha256(password.encode()).hexdigest()
# NEW:
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
```

#### Step 3.3: Update Login (`/api/login.py`)

```python
import bcrypt

# Replace lines 36-41:
# OLD: password_hash = hashlib.sha256(password.encode()).hexdigest()
#      Query with password_hash equality

# NEW:
# First, fetch user by email only
req = urllib.request.Request(
    f"{SUPABASE_URL}/rest/v1/users?email=eq.{email}&select=id,email,name,password_hash",
    headers={
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}'
    }
)

with urllib.request.urlopen(req) as response:
    users = json.loads(response.read().decode('utf-8'))

if users and len(users) > 0:
    user = users[0]
    # Verify password with bcrypt
    if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        # Password correct - proceed with login
        result = {
            "access_token": create_token(user['id']),  # Use JWT from Phase 2
            "user_id": user['id'],
            "message": "Logged in successfully"
        }
        # ... send success response
    else:
        # Password incorrect
        result = {"error": "Wrong email or password"}
        # ... send 401 response
else:
    result = {"error": "Wrong email or password"}
    # ... send 401 response
```

#### Step 3.4: Migrate Existing Passwords

**⚠️ IMPORTANT:** Existing user passwords are hashed with SHA256 and cannot be migrated.

**Options:**
1. **Force password reset** for all existing users
2. **Dual verification** (try bcrypt first, fallback to SHA256, then re-hash with bcrypt on success)
3. **Fresh start** (if no production users yet)

**Recommended: Dual verification approach:**
```python
# In login endpoint:
if users and len(users) > 0:
    user = users[0]
    password_correct = False
    needs_rehash = False

    # Try bcrypt first (new format)
    try:
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            password_correct = True
    except:
        # Not bcrypt format, try SHA256 (old format)
        sha256_hash = hashlib.sha256(password.encode()).hexdigest()
        if user['password_hash'] == sha256_hash:
            password_correct = True
            needs_rehash = True

    if password_correct:
        # If using old hash, upgrade to bcrypt
        if needs_rehash:
            new_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            # Update user's password_hash in database
            # ... (update query here)

        # Proceed with login
        # ...
```

---

### Phase 4: Fix Row Level Security (MEDIUM PRIORITY - 30 minutes)

#### If using Supabase Auth (Option A from Phase 2):

**Database schema is already correct!** (`database-schema.sql` lines 14-43)

RLS policies use `auth.uid()` which works with Supabase Auth tokens.

**No changes needed.**

#### If using Custom Auth (Option B from Phase 2):

**Problem:** `auth.uid()` only works with Supabase Auth JWTs, not custom tokens.

**Solution:** Disable RLS and handle authorization in application code.

**⚠️ WARNING:** This is less secure. Strongly recommend using Supabase Auth instead.

```sql
-- Disable RLS on tables
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE beers DISABLE ROW LEVEL SECURITY;
ALTER TABLE storage.objects DISABLE ROW LEVEL SECURITY;
```

**Then ensure every API endpoint checks authorization:**
```python
# Example: In delete-beer.py, lines 56-76 already do this
# Verify beer belongs to user before deleting
verify_req = urllib.request.Request(
    f"{SUPABASE_URL}/rest/v1/beers?id=eq.{beer_id}&user_id=eq.{user_id}",
    ...
)
```

**Must add similar checks to ALL endpoints.**

---

### Phase 5: Fix Storage Security (MEDIUM PRIORITY - 15 minutes)

#### Step 5.1: Remove Anonymous Upload Policy

**Run in Supabase SQL Editor:**
```sql
-- Remove the insecure anonymous upload policy
DROP POLICY IF EXISTS "Anonymous users can upload images" ON storage.objects;
DROP POLICY IF EXISTS "Anyone can view images anon" ON storage.objects;
```

#### Step 5.2: Implement Proper Storage Policies

**If using Supabase Auth:**
```sql
-- Allow authenticated users to upload to their own folder
CREATE POLICY "Users can upload own images" ON storage.objects
  FOR INSERT TO authenticated
  WITH CHECK (
    bucket_id = 'beer-images'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );

-- Allow authenticated users to view all images
CREATE POLICY "Authenticated users can view images" ON storage.objects
  FOR SELECT TO authenticated
  USING (bucket_id = 'beer-images');

-- Allow users to delete only their own images
CREATE POLICY "Users can delete own images" ON storage.objects
  FOR DELETE TO authenticated
  USING (
    bucket_id = 'beer-images'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );
```

**If using custom auth:**

Unfortunately, storage policies can't validate custom JWTs. Options:
1. Keep application-level checks (current approach in `beers.py:79-104`)
2. Switch to Supabase Auth (recommended)
3. Use signed URLs with expiration

---

### Phase 6: Additional Security Hardening (LOW PRIORITY - 30 minutes)

#### 6.1: Remove Test HTML File

```bash
rm /home/user/beer/index.html
# Or remove the hardcoded test password from line 60
```

#### 6.2: Implement Rate Limiting

**For Vercel API routes:**

Create `/api/middleware/rate_limit.py`:
```python
from collections import defaultdict
from datetime import datetime, timedelta
import functools

# Simple in-memory rate limiter (use Redis in production)
request_counts = defaultdict(list)

def rate_limit(max_requests=10, window_minutes=1):
    def decorator(handler_class):
        original_handler = handler_class.handler

        @functools.wraps(original_handler)
        def wrapper(self):
            client_ip = self.headers.get('x-forwarded-for', 'unknown')
            now = datetime.utcnow()
            cutoff = now - timedelta(minutes=window_minutes)

            # Clean old requests
            request_counts[client_ip] = [
                req_time for req_time in request_counts[client_ip]
                if req_time > cutoff
            ]

            # Check rate limit
            if len(request_counts[client_ip]) >= max_requests:
                self.send_response(429)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "Rate limit exceeded"
                }).encode())
                return

            # Add this request
            request_counts[client_ip].append(now)

            # Call original handler
            return original_handler(self)

        handler_class.handler = wrapper
        return handler_class
    return decorator
```

**Apply to login endpoint:**
```python
from middleware.rate_limit import rate_limit

@rate_limit(max_requests=5, window_minutes=1)
class handler(BaseHTTPRequestHandler):
    # ... existing login code
```

#### 6.3: Tighten CORS Policy

**File:** `/backend/main.py` (line 17)

```python
# BEFORE:
allow_origins=["http://localhost:3000"],

# AFTER (add your production domain):
allow_origins=[
    "http://localhost:3000",
    "https://your-production-domain.vercel.app"
],
```

#### 6.4: Add Security Headers

**For Vercel, create `/vercel.json`** (or update existing):
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Strict-Transport-Security",
          "value": "max-age=31536000; includeSubDomains"
        }
      ]
    }
  ],
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/$1"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

---

## Testing Plan

### After Phase 1 (Credentials):
```bash
# Test environment variables are working
curl https://your-api.vercel.app/api/beers/all
# Should return data (not error about missing credentials)
```

### After Phase 2 (Auth):
```bash
# Test registration
curl -X POST https://your-api.vercel.app/api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","name":"Test"}'

# Should return proper JWT token, not "token_<uuid>"

# Test token validation
curl https://your-api.vercel.app/api/beers/my \
  -H "Authorization: Bearer token_fake-uuid-12345"

# Should return 401 Unauthorized (proves forged tokens don't work)
```

### After Phase 3 (Passwords):
```bash
# Create test user
# Try logging in with wrong password
# Should fail

# Try logging in with correct password
# Should succeed
```

### After Phase 5 (Storage):
```bash
# Try uploading without authentication
# Should fail with 403 Forbidden
```

---

## Deployment Checklist

- [ ] All changes tested locally
- [ ] Environment variables configured in Vercel
- [ ] Environment variables configured in Railway/Heroku (if using)
- [ ] Database migrations run (if any)
- [ ] Frontend builds successfully
- [ ] Backend starts without errors
- [ ] All API endpoints return expected responses
- [ ] Authentication flow works end-to-end
- [ ] No credentials in git history (`git log -p | grep -i "supabase"`)
- [ ] New credentials are rotated and secure
- [ ] `.env` files are in `.gitignore`
- [ ] Storage policies tested
- [ ] Rate limiting tested (optional)

---

## Git Commit Strategy

**⚠️ IMPORTANT:** Your current git history contains exposed credentials.

### Option A: Clean History (RECOMMENDED for public repos)

```bash
# Create new branch for clean history
git checkout --orphan security-fixes

# Add all files
git add .

# Commit with clean history
git commit -m "Security hardening: Remove credentials, fix auth, update dependencies"

# Force push to new branch
git push -u origin security-fixes -f

# Later: Make this the main branch after verification
```

### Option B: Standard Commit (OK for private repos)

```bash
git checkout -b security-remediation
git add .
git commit -m "SECURITY: Remove hardcoded credentials and fix authentication

- Move all Supabase credentials to environment variables
- Implement proper JWT-based authentication
- Replace SHA256 with bcrypt for password hashing
- Fix RLS policies to work with Supabase Auth
- Remove anonymous storage upload permissions
- Add rate limiting and security headers
"
git push -u origin security-remediation
```

**Then:** Rotate credentials anyway (old credentials are in git history).

---

## Estimated Timeline

| Phase | Task | Time | Priority |
|-------|------|------|----------|
| 0 | Pre-remediation checklist | 15 min | CRITICAL |
| 1 | Credential security | 15 min | CRITICAL |
| 2 | Fix authentication | 60-90 min | CRITICAL |
| 3 | Fix password hashing | 30 min | HIGH |
| 4 | Fix RLS policies | 30 min | MEDIUM |
| 5 | Fix storage security | 15 min | MEDIUM |
| 6 | Additional hardening | 30 min | LOW |
| Testing | End-to-end testing | 30 min | CRITICAL |
| **TOTAL** | | **3-4 hours** | |

---

## Support Resources

### Supabase Documentation
- Auth: https://supabase.com/docs/guides/auth
- RLS: https://supabase.com/docs/guides/auth/row-level-security
- Storage: https://supabase.com/docs/guides/storage

### Security Best Practices
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Password Hashing: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- JWT Best Practices: https://tools.ietf.org/html/rfc8725

---

## SESSION PROGRESS SUMMARY

### ✅ COMPLETED:
- **Phase 1:** All credential security fixes implemented and committed
- **Analysis:** Authentication approach evaluated (recommend Option A)
- **Git:** Security fixes committed to main branch

### 🔄 IN PROGRESS:
- **Credential Rotation:** User generating new Supabase anon key
- **Vercel Config:** Waiting for new credentials to configure environment variables

### ⏳ PENDING PHASES:
- **Phase 2:** Switch to secure FastAPI backend (delete `/api` directory)
- **Phase 3:** Password hashing upgrade (SHA256 → bcrypt)  
- **Phase 4:** Fix RLS policies
- **Phase 5:** Storage security fixes
- **Phase 6:** Additional hardening

---

## Questions & Decisions Required

Before starting implementation, decide:

1. **Authentication approach:**
   - [x] Option A: Supabase Auth (recommended) - ✅ **BACKEND READY**
   - [ ] Option B: Custom JWT auth - can use Vercel serverless

2. **Existing users:**
   - [ ] Force password reset for all users
   - [ ] Implement dual password verification (SHA256 → bcrypt migration)
   - [ ] Fresh start (delete all users)

3. **Git history:**
   - [x] Standard commit (keep history) - ✅ **COMPLETED**
   - [ ] Clean history (orphan branch)

4. **Deployment timing:**
   - [ ] Deploy immediately after fixes
   - [ ] Test on staging first
   - [ ] Schedule maintenance window

---

## Post-Remediation Verification

After completing all phases:

1. **Run security scan:**
   ```bash
   # Check for remaining hardcoded secrets
   grep -r "supabase" . --exclude-dir=.git --exclude-dir=node_modules --exclude="*.md"

   # Should only find environment variable references
   ```

2. **Penetration testing:**
   - Try to forge authentication tokens
   - Attempt to access other users' data
   - Try uploading files without authentication
   - Attempt brute force login

3. **Code review:**
   - Review all changes with another developer
   - Verify environment variables are set correctly
   - Confirm no credentials in code

4. **Monitor logs:**
   - Watch for authentication failures
   - Check for unusual API access patterns
   - Monitor storage uploads

---

## Emergency Rollback Plan

If critical issues occur after deployment:

1. **Immediate:**
   ```bash
   # Rollback deployment in Vercel dashboard
   # Or: git revert and redeploy
   ```

2. **Restore database:**
   ```bash
   # Use backup from pre-remediation checklist
   ```

3. **Restore old credentials:**
   - Temporarily re-enable old anon key in Supabase
   - Set as environment variable to restore service

4. **Investigate:**
   - Review logs for what went wrong
   - Fix issues in separate branch
   - Test thoroughly before re-deploying

---

**Last Updated:** 2026-01-03
**Review Date:** After implementation
**Document Owner:** Development Team
