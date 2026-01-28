from django.test import Client, TestCase
from django.urls import reverse

from plans.models import Plan
from users.models import User


class SignUpViewTestCase(TestCase):
    """Testes para POST /api/auth/register/"""

    def setUp(self):
        """Configura cliente HTTP e dados de teste"""
        self.client = Client()
        self.register_url = reverse("users:register")  # POST /api/auth/register/

        # Cria planos necessários
        Plan.objects.create(
            tier="FREE",
            name="Free Plan",
            plan_type=Plan.UserChoices.INDIVIDUAL,
            max_documents=10,
            max_queries=100
        )

    def test_register_view_success(self):
        """
        O que testa: POST /api/auth/register/ com dados válidos
        Resultado esperado [PASS]:
        - Status HTTP: 201 Created
        - Response contém: id, email, username, subscription, usage
        - User criado no BD
        """
        payload = {
            "email": "novo@example.com",
            "username": "novo",
            "password": "senha12345",
            "plan": "FREE",
            "user_type": "INDIVIDUAL"
        }

        response = self.client.post(
            self.register_url,
            data=payload,
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.email, "novo@example.com") #type: ignore

    def test_register_view_invalid_plan(self):
        """
        O que testa: POST /api/auth/register/ com plano inválido
        Resultado esperado [FAIL]:
        - Status HTTP: 400 Bad Request
        - Response contém erro
        - Nenhum user criado
        """
        payload = {
            "email": "novo@example.com",
            "username": "novo",
            "password": "senha12345",
            "plan": "INVALID",
            "user_type": "INDIVIDUAL"
        }

        response = self.client.post(
            self.register_url,
            data=payload,
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(User.objects.count(), 0)

    def test_register_view_duplicate_email(self):
        """
        O que testa: POST /api/auth/register/ com email duplicado
        Resultado esperado [FAIL]:
        - Status HTTP: 400 Bad Request
        - Response contém erro de email duplicado
        - Apenas 1 user no BD
        """
        # Primeiro registro
        User.objects.create_user(
            email="existente@example.com",
            username="user1",
            password="senha12345",
            plan="FREE",
            user_type="INDIVIDUAL"
        )

        payload = {
            "email": "existente@example.com",
            "username": "user2",
            "password": "senha12345",
            "plan": "FREE",
            "user_type": "INDIVIDUAL"
        }

        response = self.client.post(
            self.register_url,
            data=payload,
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(User.objects.count(), 1)

    def test_register_view_missing_fields(self):
        """
        O que testa: POST /api/auth/register/ com campos obrigatórios faltando
        Resultado esperado [FAIL]:
        - Status HTTP: 400 Bad Request
        - Response contém erros de validação
        """
        payload = {
            "email": "novo@example.com"
            # Faltam: username, password, plan_tier
        }

        response = self.client.post(
            self.register_url,
            data=payload,
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 422)


class LoginViewTestCase(TestCase):
    """Testes para POST /api/auth/login/"""

    def setUp(self):
        """Configura cliente HTTP e dados de teste"""
        self.client = Client()
        self.login_url = reverse("users:login")  # POST /api/auth/login/

        # Cria usuário de teste
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="senha12345",
            plan="FREE",
            user_type="INDIVIDUAL"
        )

    def test_login_view_success(self):
        """
        O que testa: POST /api/auth/login/ com credenciais corretas
        Resultado esperado [PASS]:
        - Status HTTP: 200 OK
        - Response contém: id, email, username
        - last_login foi atualizado
        """
        payload = {
            "email": "test@example.com",
            "password": "senha12345"
        }

        response = self.client.post(
            self.login_url,
            data=payload,
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["data"]["email"], "test@example.com")

        # Verifica last_login atualizado
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_login)

    def test_login_view_wrong_password(self):
        """
        O que testa: POST /api/auth/login/ com senha incorreta
        Resultado esperado [FAIL]:
        - Status HTTP: 400 Bad Request
        - Response contém erro de credenciais inválidas
        """
        payload = {
            "email": "test@example.com",
            "password": "senhaerrada"
        }

        response = self.client.post(
            self.login_url,
            data=payload,
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)

    def test_login_view_user_not_found(self):
        """
        O que testa: POST /api/auth/login/ com email inexistente
        Resultado esperado [FAIL]:
        - Status HTTP: 400 Bad Request
        - Response contém erro de usuário não encontrado
        """
        payload = {
            "email": "inexistente@example.com",
            "password": "senha12345"
        }

        response = self.client.post(
            self.login_url,
            data=payload,
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 404)

    def test_login_view_inactive_user(self):
        """
        O que testa: POST /api/auth/login/ com usuário inativo
        Resultado esperado [FAIL]:
        - Status HTTP: 401 Unauthorized
        - Response contém erro de usuário inativo
        """
        self.user.is_active = False
        self.user.save()

        payload = {
            "email": "test@example.com",
            "password": "senha12345"
        }

        response = self.client.post(
            self.login_url,
            data=payload,
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)

    def test_login_view_missing_fields(self):
        """
        O que testa: POST /api/auth/login/ com campos faltando
        Resultado esperado [FAIL]:
        - Status HTTP: 422 Unprocessable Entity
        - Response contém erros de validação
        """
        payload = {
            "email": "test@example.com"
            # Falta: password
        }

        response = self.client.post(
            self.login_url,
            data=payload,
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 422)
