from unittest.mock import MagicMock, patch

from django.test import TestCase

from users.dtos import UserRegistrationDTO
from users.services import register_user


class RegisterUserServiceTestCase(TestCase):
    """ Testes Unitários para o service de resgistro de usuário. """

    # Métodos que serão mockados e chamados durante o teste
    @patch("users.services.User.objects.create_user")
    @patch("users.services.Plan.objects.get")
    @patch("users.services.Subscription.objects.create")
    @patch("users.services.Usage.objects.get_or_create")

    def test_register_user_success(
        self,
        mock_usage: MagicMock,
        mock_subscription: MagicMock,
        mock_plan: MagicMock,
        mock_create_user: MagicMock,
    ) -> None:
        """ Testa o registro bem-sucedido de um usuário. """
        # Configura os mocks

        # Dados de saída esperados
        mock_user = MagicMock(id=1, email="teste@example.com", username="testeuser")
        mock_create_user.return_value = mock_user

        # Dados de saída do plano
        mock_plan_obj = MagicMock(id=1, tier="FREE", plan_type="INDIVIDUAL")
        mock_plan.return_value = mock_plan_obj

        # Dados de entrada
        dto = UserRegistrationDTO(
            email="teste@example.com",
            username="testeuser",
            password="senha123",
            plan_tier="FREE",
        )

        # Chama o serviço
        user = register_user(dto)

        # Verifica se os métodos foram chamados corretamente como verificação de dados e também sem verificação de dados
        mock_create_user.assert_called_once_with(
            email="teste@example.com",
            username="testeuser",
            password="senha123",
            role="FREE",
        )
        mock_plan.assert_called_once_with(tier="FREE", plan_type="INDIVIDUAL")
        mock_subscription.assert_called_once()
        mock_usage.assert_called_once()
        self.assertEqual(user.email, "teste@example.com")

    @patch("users.services.Plan.objects.get")
    def test_register_user_plan_not_found(self, mock_plan: MagicMock) -> None:
        """ Testa o registro de usuário quando o plano não é encontrado. """

        # Configura o mock para lançar uma exceção que eu espero
        mock_plan.side_effect = ValueError("Plano não encontrado")

        dto = UserRegistrationDTO(
            email="teste@example.com",
            username="testeuser",
            password="senha123",
            plan_tier="INVALID", # Plano inválido -> lança exceção ValueError
        )

        with self.assertRaises(ValueError):
            register_user(dto)
