def test_register_success(client):
    """Test successful registration"""
    response = client.post('/api/v1/auth/register',
                           json={
                               'email': 'new@example.com',
                               'username': 'newuser',
                               'password': 'password123'
                           })

    assert response.status_code == 201
    data = response.get_json()
    assert 'user_id' in data
    assert 'message' in data
    assert data['message'] == 'Registration successful'


def test_register_duplicate_email(client, test_user):
    """Test registration with duplicate email"""
    response = client.post('/api/v1/auth/register', json={
        'email': 'test@example.com',  # Same as test_user
        'username': 'different',
        'password': 'password123'
    })

    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post('/api/v1/auth/login',
                           json={
                               'email': 'test@example.com',
                               'password': 'password123'
                           })

    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert 'user' in data
    assert data['user']['email'] == test_user.email


def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post('/api/v1/auth/login',
                           json={
                               'email': 'wrong@example.com',
                               'password': 'wrongpassword'
                           })

    assert response.status_code == 401
    assert 'error' in response.get_json()


def test_token_refresh(client, auth_headers):
    """Test token refresh"""
    response = client.post('/api/v1/auth/refresh', headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
