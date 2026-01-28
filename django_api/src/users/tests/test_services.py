from unittest.mock import MagicMock, patch

from django.test import TestCase

from users.dtos import UserLoginDTO, UserRegistrationDTO
from users.exceptions import (
    InvalidCredentialsException,
    PlanNotFoundException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from users.services import AuthService


class RegisterUserServiceTestCase(TestCase):
    """Testes para AuthService.register_user()"""

    @patch("users.services.UserRepository.email_exists")
    @patch("users.services.UserRepository.username_exists")
    @patch("users.services.PlanRepository.get_by_tier")
    @patch("users.services.UserRepository.create")
    @patch("users.services.SubscriptionRepository.create")
    @patch("users.services.UsageRepository.get_or_create_period_usage")
    def test_register_user_success(
        self,
        mock_usage,
        mock_subscription,
        mock_user_create,
        mock_plan_get,
        mock_username_exists,
        mock_email_exists,
    ):
        """
        O que testa: Registro bem-sucedido isolado (com repositorios mockados)
        Resultado esperado [PASS]:
        - Validacoes: email_exists, username_exists chamadas
        - Plan buscado por tier ('FREE')
        - User, Subscription e Usage criados via repositorios
        - User retornado com email 'novo@example.com'
        """
        # Arrange
        mock_email_exists.return_value = False
        mock_username_exists.return_value = False

        mock_plan = MagicMock(id=1, tier="FREE")
        mock_plan_get.return_value = mock_plan

        mock_user = MagicMock(id="123", email="novo@example.com", username="novo")
        mock_user_create.return_value = mock_user

        dto = UserRegistrationDTO(
            email="novo@example.com",
            username="novo",
            password="senha12345",
            plan="FREE",
            user_type="INDIVIDUAL"
        )

        # Act
        user = AuthService.register_user(dto)

        # Assert
        mock_email_exists.assert_called_once_with("novo@example.com")
        mock_username_exists.assert_called_once_with("novo")
        mock_plan_get.assert_called_once_with("FREE")
        mock_user_create.assert_called_once()
        mock_subscription.assert_called_once()
        mock_usage.assert_called_once()
        self.assertEqual(user.email, "novo@example.com")

    @patch("users.services.UserRepository.email_exists")
    def test_register_user_email_already_exists(self, mock_email_exists):
        """
        O que testa: Tentativa de registrar quando email ja existe (mockado)
        Resultado esperado [FAIL]: UserAlreadyExistsException lancada
        """
        # Arrange
        mock_email_exists.return_value = True

        dto = UserRegistrationDTO(
            email="existente@example.com",
            username="novo",
            password="senha12345",
            plan="FREE",
            user_type="INDIVIDUAL"
        )

        # Act & Assert
        with self.assertRaises(UserAlreadyExistsException):
            AuthService.register_user(dto)

    @patch("users.services.UserRepository.email_exists")
    @patch("users.services.UserRepository.username_exists")
    def test_register_user_username_already_exists(self, mock_username_exists, mock_email_exists):
        """
        O que testa: Tentativa de registrar quando username ja existe (mockado)
        Resultado esperado [FAIL]: UserAlreadyExistsException lancada
        - Email check passa (False)
        - Username check falha (True) -> exception
        """
        # Arrange
        mock_email_exists.return_value = False
        mock_username_exists.return_value = True

        dto = UserRegistrationDTO(
            email="novo@example.com",
            username="existente",
            password="senha12345",
            plan="FREE",
            user_type="INDIVIDUAL"
        )

        # Act & Assert
        with self.assertRaises(UserAlreadyExistsException):
            AuthService.register_user(dto)

    @patch("users.services.UserRepository.email_exists")
    @patch("users.services.UserRepository.username_exists")
    @patch("users.services.PlanRepository.get_by_tier")
    def test_register_user_plan_not_found(self, mock_plan_get, mock_username_exists, mock_email_exists):
        """
        O que testa: Tentativa de registrar com plano invalido (PlanRepository retorna None)
        Resultado esperado [FAIL]: PlanNotFoundException lancada
        - Email/username checks passam
        - Plan lookup falha (mock_plan_get.return_value = None)
        """
        # Arrange
        mock_email_exists.return_value = False
        mock_username_exists.return_value = False
        mock_plan_get.return_value = None

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


class AuthenticateUserServiceTestCase(TestCase):
    """Testes para AuthService.authenticate_user()"""

    @patch("users.services.UserRepository.get_by_email")
    def test_authenticate_user_success(self, mock_get_by_email):
        """
        O que testa: Autenticacao bem-sucedida com repositorio mockado
        Resultado esperado [PASS]:
        - User retornado com email correto
        - check_password validou credenciais
        """
        # Arrange
        mock_user = MagicMock(
            id="123",
            email="user@example.com",
            is_active=True
        )
        mock_user.check_password.return_value = True
        mock_get_by_email.return_value = mock_user

        dto = UserLoginDTO(
            email="user@example.com",
            password="senha12345"
        )

        # Act
        user = AuthService.authenticate_user(dto)

        # Assert
        mock_get_by_email.assert_called_once_with("user@example.com")
        mock_user.check_password.assert_called_once_with("senha12345")
        self.assertEqual(user.email, "user@example.com")

    @patch("users.services.UserRepository.get_by_email")
    def test_authenticate_user_not_found(self, mock_get_by_email):
        """
        O que testa: Tentativa de autenticar com email inexistente
        Resultado esperado [FAIL]: UserNotFoundException lancada
        - UserRepository.get_by_email retorna None
        """
        # Arrange
        mock_get_by_email.return_value = None

        dto = UserLoginDTO(
            email="inexistente@example.com",
            password="senha12345"
        )

        # Act & Assert
        with self.assertRaises(UserNotFoundException):
            AuthService.authenticate_user(dto)

    @patch("users.services.UserRepository.get_by_email")
    def test_authenticate_user_wrong_password(self, mock_get_by_email):
        """
        O que testa: Tentativa de autenticar com senha incorreta
        Resultado esperado [FAIL]: InvalidCredentialsException lancada
        - User encontrado
        - check_password retorna False
        """
        # Arrange
        mock_user = MagicMock(email="user@example.com")
        mock_user.check_password.return_value = False
        mock_get_by_email.return_value = mock_user

        dto = UserLoginDTO(
            email="user@example.com",
            password="senhaerrada"
        )

        # Act & Assert
        with self.assertRaises(InvalidCredentialsException):
            AuthService.authenticate_user(dto)
