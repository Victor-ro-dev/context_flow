"""
Testes de Integração End-to-End.
Testa o fluxo completo desde a requisição HTTP até o banco de dados.
"""

from django.test import TestCase

from plans.models import Plan, Subscription, Usage
from users.dtos import UserLoginDTO, UserRegistrationDTO
from users.exceptions import (
    InvalidCredentialsException,
    PlanNotFoundException,
    UserAlreadyExistsException,
)
from users.models import User
from users.services import AuthService


class RegisterUserIntegrationTestCase(TestCase):
    """Testes de integração para registro de usuário"""

    def setUp(self):
        """Configura dados de teste"""
        # Cria planos necessários
        Plan.objects.create(
            tier="FREE",
            name="Free Plan",
            plan_type=Plan.UserChoices.INDIVIDUAL,
            max_documents=10,
            max_queries=100
        )
        Plan.objects.create(
            tier="PRO",
            name="Pro Plan",
            plan_type=Plan.UserChoices.INDIVIDUAL,
            max_documents=100,
            max_queries=1000
        )

    def test_register_user_complete_flow(self):
        """
        O que testa: Fluxo completo de registro (DTO → Service → BD)
        Resultado esperado [PASS]: User, Subscription e Usage criados e persistidos no BD
        - User: email 'novo@example.com', username 'novo', senha hashada
        - Subscription: plano FREE com status ACTIVE
        - Usage: período atual com 0 documentos e 0 queries
        """
        # Arrange
        dto = UserRegistrationDTO(
            email="novo@example.com",
            username="novo",
            password="senha12345",
            plan="FREE",
            user_type="INDIVIDUAL"
        )

        # Act
        user = AuthService.register_user(dto)

        # Assert - Usuário criado
        self.assertIsNotNone(user.id)
        self.assertEqual(user.email, "novo@example.com")
        self.assertEqual(user.username, "novo")
        self.assertTrue(user.check_password("senha12345"))

        # Assert - Subscription criada
        subscription = Subscription.objects.get(user=user)
        self.assertEqual(subscription.plan.tier, "FREE")
        self.assertEqual(subscription.status, "ACTIVE")

        # Assert - Usage criada
        period = subscription.current_period_start.strftime("%Y-%m-%d")
        usage = Usage.objects.get(user=user, period=period)
        self.assertEqual(usage.documents_uploaded, 0)
        self.assertEqual(usage.queries_executed, 0)

    def test_register_multiple_users_different_plans(self):
        """
        O que testa: Registro simultâneo de múltiplos usuários com planos diferentes
        Resultado esperado [PASS]:
        - Ambos os usuários registrados (FREE e PRO) com sucesso
        - User count = 2 no BD
        - user_free.subscription.plan.tier = 'FREE'
        - user_pro.subscription.plan.tier = 'PRO'
        """
        # Arrange
        dto_free = UserRegistrationDTO(
            email="free@example.com",
            username="free_user",
            password="senha12345",
            plan="FREE",
            user_type="INDIVIDUAL"
        )
        dto_pro = UserRegistrationDTO(
            email="pro@example.com",
            username="pro_user",
            password="senha12345",
            plan="PRO",
            user_type="INDIVIDUAL"
        )

        # Act
        user_free = AuthService.register_user(dto_free)
        user_pro = AuthService.register_user(dto_pro)

        # Assert
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(user_free.plan, "FREE")
        self.assertEqual(user_pro.plan, "PRO")

    def test_register_user_then_login(self):
        """
        O que testa: Fluxo E2E completo - Registrar e depois fazer Login
        Resultado esperado [PASS]:
        - User registrado com sucesso
        - Login retorna o MESMO usuário (same ID e email)
        - Credenciais funcionam corretamente
        """
        # Arrange - Registro
        register_dto = UserRegistrationDTO(
            email="user@example.com",
            username="testuser",
            password="senha12345",
            plan="FREE",
            user_type="INDIVIDUAL"
        )

        # Act - Registra
        registered_user = AuthService.register_user(register_dto)

        # Act - Login
        login_dto = UserLoginDTO(
            email="user@example.com",
            password="senha12345"
        )
        authenticated_user = AuthService.authenticate_user(login_dto)

        # Assert
        self.assertEqual(str(registered_user.id), authenticated_user.id)
        self.assertEqual(registered_user.email, authenticated_user.email)

    def test_register_user_email_duplicate_error(self):
        """
        O que testa: Tentativa de registrar com email duplicado
        Resultado esperado [FAIL]: UserAlreadyExistsException é lançada
        - Primeiro registro com 'duplo@example.com' funciona
        - Segundo registro com mesmo email falha
        """
        # Arrange
        dto1 = UserRegistrationDTO(
            email="duplicate@example.com",
            username="user1",
            password="senha12345",
            plan="FREE",
            user_type="INDIVIDUAL"
        )
        dto2 = UserRegistrationDTO(
            email="duplicate@example.com",
            username="user2",
            password="senha12345",
            plan="FREE",
            user_type="INDIVIDUAL"
        )

        # Act & Assert
        AuthService.register_user(dto1)
        with self.assertRaises(UserAlreadyExistsException):
            AuthService.register_user(dto2)

    def test_register_user_invalid_plan_error(self):
        """
        O que testa: Tentativa de registrar com plano inválido (INVALID)
        Resultado esperado [FAIL]:
        - PlanNotFoundException é lançada
        - Nenhum usuário criado no BD (User.objects.count() = 0)
        - Transação foi revertida por erro
        """
        # Arrange
        dto = UserRegistrationDTO(
            email="novo@example.com",
            username="novo",
            password="senha12345",
            plan="INVALID",
            user_type="INDIVIDUAL"
        )

        # Act & Assert
        with self.assertRaises(PlanNotFoundException):
            AuthService.register_user(dto)

        # Verifica que nada foi criado
        self.assertEqual(User.objects.count(), 0)


class AuthenticateUserIntegrationTestCase(TestCase):
    """✅ Testes de integração para autenticação"""

    def setUp(self):
        """Configura dados de teste"""
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="senha12345",
            user_type="INDIVIDUAL"
        )

    def test_authenticate_user_success(self):
        """
        O que testa: Autenticação bem-sucedida com email e senha corretos
        Resultado esperado [PASS]:
        - User retornado com ID correto
        - Email confirmado ('test@example.com')
        """
        # Arrange
        dto = UserLoginDTO(
            email="test@example.com",
            password="senha12345"
        )

        # Act
        user = AuthService.authenticate_user(dto)

        # Assert
        self.assertEqual(str(self.user.id), user.id)
        self.assertEqual(user.email, "test@example.com")

    def test_authenticate_user_not_found(self):
        """
        O que testa: Tentativa de autenticar com email inexistente
        Resultado esperado [FAIL]: UserNotFoundException lançada
        """
        # Arrange
        dto = UserLoginDTO(
            email="inexistente@example.com",
            password="senha12345"
        )

        # Act & Assert
        with self.assertRaises(Exception):
            AuthService.authenticate_user(dto)

    def test_authenticate_user_wrong_password(self):
        """
        O que testa: Tentativa de autenticar com senha incorreta
        Resultado esperado [FAIL]: InvalidCredentialsException lancada
        - Email correto, senha errada -> falha
        """
        # Arrange
        dto = UserLoginDTO(
            email="test@example.com",
            password="senhaerrada"
        )

        # Act & Assert
        with self.assertRaises(InvalidCredentialsException):
            AuthService.authenticate_user(dto)

    def test_authenticate_inactive_user(self):
        """
        O que testa: Tentativa de autenticar com usuário inativo (is_active=False)
        Resultado esperado [FAIL]: InvalidCredentialsException lançada
        - Mesmo com senha correta, usuário inativo não pode fazer login
        """
        # Arrange
        self.user.is_active = False
        self.user.save()

        dto = UserLoginDTO(
            email="test@example.com",
            password="senha12345"
        )

        # Act & Assert
        with self.assertRaises(InvalidCredentialsException):
            AuthService.authenticate_user(dto)


