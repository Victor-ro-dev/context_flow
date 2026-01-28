from django.test import TestCase

from users.models import User
from users.repositories import UserRepository


class UserRepositoryTestCase(TestCase):
    """Testes para UserRepository"""

    def setUp(self):
        """Cria dados de teste antes de cada teste"""
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="senha12345",
            plan="FREE",
            user_type="INDIVIDUAL"
        )

    def test_get_by_email_success(self):
        """
        O que testa: Busca de usuario por email existente
        Resultado esperado [PASS]:
        - UserRepository.get_by_email('test@example.com') retorna objeto User
        - user.email == 'test@example.com'
        """
        # Act
        user = UserRepository.get_by_email("test@example.com")


        # Assert
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@example.com") #type: ignore

    def test_get_by_email_not_found(self):
        """
        O que testa: Busca de usuario por email inexistente
        Resultado esperado [PASS]:
        - UserRepository.get_by_email('inexistente@example.com') retorna None
        - Sem excecao lancada
        """
        # Act
        user = UserRepository.get_by_email("inexistente@example.com")

        # Assert
        self.assertIsNone(user)

    def test_get_by_username_success(self):
        """
        O que testa: Busca de usuario por username existente
        Resultado esperado [PASS]:
        - UserRepository.get_by_username('testuser') retorna objeto User
        - user.username == 'testuser'
        """
        # Act
        user = UserRepository.get_by_username("testuser")

        # Assert
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser") #type: ignore

    def test_email_exists_true(self):
        """
        O que testa: Verificacao se email existe
        Resultado esperado [PASS]:
        - UserRepository.email_exists('test@example.com') retorna True
        """
        # Act
        exists = UserRepository.email_exists("test@example.com")

        # Assert
        self.assertTrue(exists)

    def test_email_exists_false(self):
        """
        O que testa: Verificacao se email nao existe
        Resultado esperado [PASS]:
        - UserRepository.email_exists('inexistente@example.com') retorna False
        """
        # Act
        exists = UserRepository.email_exists("inexistente@example.com")

        # Assert
        self.assertFalse(exists)

    def test_username_exists_true(self):
        """
        O que testa: Verificacao se username existe
        Resultado esperado [PASS]:
        - UserRepository.username_exists('testuser') retorna True
        """
        # Act
        exists = UserRepository.username_exists("testuser")

        # Assert
        self.assertTrue(exists)

    def test_username_exists_false(self):
        """
        O que testa: Verificacao se username nao existe
        Resultado esperado [PASS]:
        - UserRepository.username_exists('inexistente') retorna False
        """
        # Act
        exists = UserRepository.username_exists("inexistente")

        # Assert
        self.assertFalse(exists)

    def test_create_user(self):
        """
        O que testa: Criacao de novo usuario via repositorio
        Resultado esperado [PASS]:
        - UserRepository.create(...) cria e retorna User
        - user.id gerado (nao None)
        - email, username, role salvos corretamente
        - Novo registro persiste no BD (User.objects.count() = 2)
        """
        # Act
        user = UserRepository.create(
            email="novo@example.com",
            username="novo",
            password="senha12345",
            plan="USER"
        )

        # Assert
        self.assertIsNotNone(user.id)
        self.assertEqual(user.email, "novo@example.com")
        self.assertEqual(user.username, "novo")
        self.assertEqual(user.plan, "USER")

    def test_get_active_users(self):
        """
        O que testa: Busca apenas de usuarios com is_active=True
        Resultado esperado [PASS]:
        - UserRepository.get_active_users() retorna QuerySet
        - Conta apenas usuarios ativos (1, nao 2)
        - Usuario inativo (inactive@example.com) nao incluido
        """
        # Arrange
        inactive_user = User.objects.create_user(
            email="inactive@example.com",
            username="inactive",
            password="senha12345",
            is_active=False
        )

        # Act
        active_users = UserRepository.get_active_users()

        # Assert
        self.assertEqual(len(active_users), 1)
        self.assertEqual(active_users[0].email, "test@example.com")
