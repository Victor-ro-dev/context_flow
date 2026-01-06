from django.test import TestCase

from plans.models import Plan, Subscription, Usage
from users.dtos import UserRegistrationDTO
from users.models import User
from users.services import register_user


class RegisterUserServiceTestCaseIntegration(TestCase):
    """ Testes de Integração para o service de registro de usuário. """

    def setUp(self) -> None:
        """ Configura os dados iniciais para os testes. """
        # Cria planos necessários para os testes
        Plan.objects.all().delete()
        Plan.objects.create(tier="FREE", plan_type=Plan.PlanChoices.INDIVIDUAL)

    def test_register_user_integration(self) -> None:
        """ Testa o registro de um usuário e a criação da assinatura e uso associados. """
        dto = UserRegistrationDTO(
            email="test@example.com",
            username="testuser",
            password="strongpassword",
            plan_tier="FREE",
        )

        user = register_user(dto)

        # Verifica se o usuário foi criado corretamente
        self.assertIsNotNone(user.id)
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("strongpassword"))

        # Verifica se a assinatura foi criada corretamente
        subscription = Subscription.objects.get(user=user)
        self.assertEqual(subscription.plan.tier, "FREE")
        self.assertEqual(subscription.status, "ACTIVE")

        # Verifica se o uso foi criado corretamente
        period = subscription.current_period_start.strftime("%Y-%m-%d")
        usage = Usage.objects.get(user=user, period=period)
        self.assertEqual(usage.documents_uploaded, 0)
        self.assertEqual(usage.queries_executed, 0)
        self.assertEqual(usage.storage_used_mb, 0)
        self.assertEqual(usage.tokens_used, 0)

    def test_register_user_invalid_plan(self) -> None:
        """ Testa o registro de um usuário com um plano inválido. """
        dto = UserRegistrationDTO(
            email="invalid@example.com",
            username="invaliduser",
            password="strongpassword",
            plan_tier="INVALID",
        )

        with self.assertRaises(ValueError):
            register_user(dto)

        # Verifica se o usuário não foi criado
        self.assertEqual(User.objects.count(), 0)
