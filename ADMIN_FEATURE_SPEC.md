# Super-Admin Feature Specification
## Stock Analyzer Pro - Administrative Control Panel

**Version:** 1.0.0
**Estimated Time:** 3-4 hours
**Priority:** HIGH
**Status:** IN DEVELOPMENT

---

## 🎯 Overview

Implement a comprehensive administrative control panel for managing users, monitoring system health, and maintaining platform integrity. The admin panel provides privileged access to super-admin users for user management and system oversight.

---

## 📋 Requirements

### Functional Requirements

1. **User Management**
   - View all registered users
   - Edit user details (email, username)
   - Delete user accounts
   - Reset user passwords
   - Promote/demote admin privileges
   - View user statistics (registration date, last login, portfolio value)

2. **Access Control**
   - Role-based authentication (admin flag)
   - Protected admin routes (middleware)
   - Admin-only UI components
   - Audit logging for admin actions

3. **User Interface**
   - Admin dashboard page
   - User management table with search/filter
   - User detail modal
   - Bulk actions support
   - Responsive design

### Non-Functional Requirements

1. **Security**
   - Admin actions require re-authentication
   - All admin operations logged
   - CSRF protection
   - SQL injection prevention

2. **Performance**
   - User list pagination (50 users per page)
   - Efficient database queries
   - Caching where appropriate

3. **Usability**
   - Intuitive admin interface
   - Clear confirmation dialogs
   - Success/error notifications
   - Keyboard shortcuts

---

## 🏗️ Architecture

### Database Schema Changes

```python
# app/models/user.py
class User(db.Model):
    # ... existing fields ...
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
```

**Migration:**
```python
# migrations/versions/xxx_add_admin_field.py
def upgrade():
    op.add_column('user', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('user', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('last_login', sa.DateTime(), nullable=True))

    # Set default created_at for existing users
    op.execute("UPDATE user SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")

def downgrade():
    op.drop_column('user', 'last_login')
    op.drop_column('user', 'created_at')
    op.drop_column('user', 'is_admin')
```

### Backend Components

1. **Admin Service** (`app/services/admin_service.py`)
   - User CRUD operations
   - Statistics aggregation
   - Audit logging

2. **Admin Routes** (`app/routes/admin.py`)
   - GET `/api/admin/users` - List all users
   - GET `/api/admin/users/<id>` - Get user details
   - PUT `/api/admin/users/<id>` - Update user
   - DELETE `/api/admin/users/<id>` - Delete user
   - POST `/api/admin/users/<id>/toggle-admin` - Toggle admin status
   - GET `/api/admin/stats` - System statistics

3. **Admin Middleware** (`app/middleware/admin_required.py`)
   - Decorator: `@admin_required`
   - Validates JWT token
   - Checks `is_admin` flag
   - Returns 403 if not admin

4. **Audit Log Model** (`app/models/audit_log.py`)
   - Track all admin actions
   - Who, what, when logging

### Frontend Components

1. **Admin Page** (`templates/index.html`)
   - Admin navigation item (visible only to admins)
   - Admin dashboard layout

2. **Admin JavaScript** (`static/js/admin.js`)
   - User table rendering
   - CRUD operations
   - Search and filter
   - Pagination

3. **Admin API Client** (`static/js/api.js`)
   - Admin-specific API methods
   - Error handling

4. **Admin Styles** (`static/css/admin.css`)
   - Admin-specific UI components
   - Table styling
   - Action buttons

---

## 🎨 User Interface Design

### Admin Dashboard Layout

```
┌──────────────────────────────────────────────────────────┐
│ Stock Analyzer Pro - Admin Dashboard                     │
├──────────────────────────────────────────────────────────┤
│ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐            │
│ │ Total  │ │ Active │ │ Admins │ │ New    │            │
│ │ Users  │ │ Today  │ │ Count  │ │ (7d)   │            │
│ │  1,234 │ │   156  │ │    3   │ │   89   │            │
│ └────────┘ └────────┘ └────────┘ └────────┘            │
├──────────────────────────────────────────────────────────┤
│ User Management                                          │
│ ┌──────────────┐ ┌──────────┐                           │
│ │ 🔍 Search... │ │ + Add    │                           │
│ └──────────────┘ └──────────┘                           │
│                                                          │
│ ┌────────────────────────────────────────────────────┐  │
│ │ ID │ Username │ Email    │ Admin │ Created │ Actions│  │
│ ├────┼──────────┼──────────┼───────┼─────────┼────────┤  │
│ │ 1  │ john_doe │ j@ex.com │  ✓    │ Jan 15  │ E D    │  │
│ │ 2  │ jane_sm  │ j@ex.com │  ✗    │ Jan 20  │ E D    │  │
│ │ 3  │ bob_wil  │ b@ex.com │  ✗    │ Feb 1   │ E D    │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│ Showing 1-50 of 1,234 users      < 1 2 3 ... 25 >       │
└──────────────────────────────────────────────────────────┘
```

### User Actions

- **View** (👁️) - View user details
- **Edit** (✏️) - Edit user information
- **Delete** (🗑️) - Delete user account
- **Toggle Admin** (👑) - Promote/demote admin

---

## 🔐 Security Considerations

### Authentication Flow

```
User Request → JWT Token → Extract User ID → Get User from DB
  ↓
Check is_admin flag → if False, return 403 Forbidden
  ↓
if True, proceed with admin action → Log to audit_log
```

### Audit Logging

All admin actions are logged:
```python
{
    "admin_id": 1,
    "admin_username": "super_admin",
    "action": "DELETE_USER",
    "target_user_id": 42,
    "target_username": "deleted_user",
    "timestamp": "2025-10-02T14:30:00Z",
    "ip_address": "192.168.1.1"
}
```

### Protection Mechanisms

1. **Re-authentication** for sensitive actions (delete user)
2. **CSRF tokens** for all admin forms
3. **Rate limiting** on admin endpoints (10 req/min)
4. **Cannot delete self** - prevent lockout
5. **Minimum 1 admin** - always keep at least one admin

---

## 📊 API Endpoints

### GET /api/admin/users
**Description:** Get paginated list of all users

**Query Parameters:**
- `page` (int, default: 1)
- `per_page` (int, default: 50, max: 100)
- `search` (string, optional) - Search username or email
- `is_admin` (boolean, optional) - Filter by admin status

**Response:**
```json
{
    "users": [
        {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "is_admin": true,
            "created_at": "2025-01-15T10:30:00Z",
            "last_login": "2025-10-02T08:00:00Z",
            "portfolio_count": 5,
            "total_portfolio_value": 15000.50
        }
    ],
    "total": 1234,
    "page": 1,
    "per_page": 50,
    "total_pages": 25
}
```

### GET /api/admin/users/<id>
**Description:** Get detailed user information

**Response:**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "is_admin": true,
    "created_at": "2025-01-15T10:30:00Z",
    "last_login": "2025-10-02T08:00:00Z",
    "portfolio": {
        "positions": 5,
        "total_value": 15000.50,
        "total_invested": 12000.00,
        "total_return": 25.00
    },
    "watchlist_count": 12,
    "alerts_count": 3,
    "transactions_count": 47
}
```

### PUT /api/admin/users/<id>
**Description:** Update user information

**Request Body:**
```json
{
    "username": "new_username",
    "email": "new@example.com"
}
```

**Response:**
```json
{
    "success": true,
    "message": "User updated successfully",
    "user": { /* updated user object */ }
}
```

### DELETE /api/admin/users/<id>
**Description:** Delete user account (cascades to portfolio, watchlist, alerts)

**Response:**
```json
{
    "success": true,
    "message": "User deleted successfully",
    "deleted_user_id": 42
}
```

### POST /api/admin/users/<id>/toggle-admin
**Description:** Toggle user's admin status

**Response:**
```json
{
    "success": true,
    "message": "User promoted to admin",
    "user": {
        "id": 42,
        "username": "new_admin",
        "is_admin": true
    }
}
```

### GET /api/admin/stats
**Description:** Get system statistics

**Response:**
```json
{
    "total_users": 1234,
    "active_users_today": 156,
    "active_users_week": 542,
    "admin_count": 3,
    "new_users_week": 89,
    "total_portfolios": 987,
    "total_transactions": 5421,
    "total_watchlist_items": 3456,
    "total_alerts": 876
}
```

---

## 🧪 Testing Plan

### Unit Tests
```python
# tests/test_admin.py
def test_admin_can_view_users(admin_client):
    response = admin_client.get('/api/admin/users')
    assert response.status_code == 200
    assert 'users' in response.json

def test_non_admin_cannot_view_users(regular_client):
    response = regular_client.get('/api/admin/users')
    assert response.status_code == 403

def test_admin_can_delete_user(admin_client, sample_user):
    response = admin_client.delete(f'/api/admin/users/{sample_user.id}')
    assert response.status_code == 200
    assert User.query.get(sample_user.id) is None

def test_admin_cannot_delete_self(admin_client, admin_user):
    response = admin_client.delete(f'/api/admin/users/{admin_user.id}')
    assert response.status_code == 400
    assert 'cannot delete yourself' in response.json['error'].lower()
```

### Integration Tests
- Full user management workflow
- Admin promotion/demotion
- Search and pagination
- Cascading deletes

---

## 📝 Implementation Checklist

### Backend
- [ ] Add `is_admin`, `created_at`, `last_login` to User model
- [ ] Create database migration
- [ ] Implement AdminService class
- [ ] Create admin routes blueprint
- [ ] Implement `@admin_required` decorator
- [ ] Create AuditLog model
- [ ] Add audit logging to all admin actions
- [ ] Write unit tests for admin functionality

### Frontend
- [ ] Create admin page HTML structure
- [ ] Implement admin.js for user management
- [ ] Add admin API methods to api.js
- [ ] Create admin CSS styles
- [ ] Add admin navigation (visible only to admins)
- [ ] Implement user search and filter
- [ ] Create user edit modal
- [ ] Add delete confirmation dialog
- [ ] Implement pagination controls

### Security
- [ ] Test admin authentication
- [ ] Verify non-admins cannot access admin routes
- [ ] Test audit logging
- [ ] Verify self-deletion prevention
- [ ] Test minimum admin enforcement

---

## 🚀 Deployment

1. **Database Migration**
   ```bash
   flask db migrate -m "Add admin fields and audit log"
   flask db upgrade
   ```

2. **Create First Admin**
   ```python
   # One-time script: scripts/create_admin.py
   from app import create_app, db
   from app.models import User

   app = create_app()
   with app.app_context():
       admin = User.query.filter_by(email='admin@example.com').first()
       if admin:
           admin.is_admin = True
           db.session.commit()
           print(f"Admin created: {admin.username}")
   ```

3. **Deploy to Production**
   - Commit all changes
   - Push to GitHub
   - Render auto-deploys
   - Run migration on production database
   - Create first admin user

---

## 📊 Success Metrics

- [ ] Admin can view all users
- [ ] Admin can edit user details
- [ ] Admin can delete users (with confirmation)
- [ ] Admin can promote/demote other admins
- [ ] Non-admins receive 403 when accessing admin routes
- [ ] All admin actions are logged
- [ ] Admin UI is responsive and intuitive
- [ ] Unit tests pass (100% coverage for admin features)

---

**Document Status:** APPROVED FOR IMPLEMENTATION
**Next Step:** Begin backend implementation
**Estimated Completion:** 3-4 hours from start
