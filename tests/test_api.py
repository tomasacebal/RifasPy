"""Pruebas simples de integracion para la API de rifas."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app import create_app


class RifaApiTestCase(unittest.TestCase):
    """Verifica los escenarios principales del CRUD de rifas."""

    def setUp(self) -> None:
        """Crea una app de pruebas con una base SQLite temporal.

        Returns:
            No retorna ningun valor.
        """

        self.temp_dir = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_dir.name) / "test_rifas.db"
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE_PATH": str(database_path),
            }
        )
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        """Limpia los recursos temporales usados por la prueba.

        Returns:
            No retorna ningun valor.
        """

        self.temp_dir.cleanup()

    def test_healthcheck_returns_ok(self) -> None:
        """Verifica que el healthcheck responda con estado correcto.

        Returns:
            No retorna ningun valor.
        """

        response = self.client.get("/api/v1/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"success": True, "data": {"status": "ok"}})

    def test_full_crud_flow(self) -> None:
        """Verifica el flujo feliz completo del CRUD.

        Returns:
            No retorna ningun valor.
        """

        create_response = self.client.post(
            "/api/v1/rifas",
            json={
                "numero": 10,
                "nombre": "Juan Perez",
                "telefono": "1122334455",
                "mail": "juan@example.com",
            },
        )
        created_body = create_response.get_json()

        self.assertEqual(create_response.status_code, 201)
        self.assertTrue(created_body["success"])
        self.assertEqual(created_body["data"]["numero"], 10)
        self.assertEqual(created_body["data"]["nombre"], "Juan Perez")
        self.assertTrue(created_body["data"]["timestamp"].endswith("Z"))

        list_response = self.client.get("/api/v1/rifas")
        list_body = list_response.get_json()
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_body["data"]), 1)

        get_response = self.client.get("/api/v1/rifas/10")
        get_body = get_response.get_json()
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_body["data"]["mail"], "juan@example.com")

        put_response = self.client.put(
            "/api/v1/rifas/10",
            json={
                "nombre": "Juan Actualizado",
                "telefono": "1199998888",
                "mail": "nuevo@example.com",
            },
        )
        put_body = put_response.get_json()
        self.assertEqual(put_response.status_code, 200)
        self.assertEqual(put_body["data"]["nombre"], "Juan Actualizado")
        self.assertEqual(put_body["data"]["telefono"], "1199998888")

        patch_response = self.client.patch(
            "/api/v1/rifas/10",
            json={
                "telefono": "1100001111",
            },
        )
        patch_body = patch_response.get_json()
        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(patch_body["data"]["telefono"], "1100001111")
        self.assertEqual(patch_body["data"]["mail"], "nuevo@example.com")

        delete_response = self.client.delete("/api/v1/rifas/10")
        delete_body = delete_response.get_json()
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(delete_body["data"]["numero"], 10)

        not_found_response = self.client.get("/api/v1/rifas/10")
        self.assertEqual(not_found_response.status_code, 404)

    def test_duplicate_numero_returns_400(self) -> None:
        """Verifica que no se pueda repetir el numero de una rifa.

        Returns:
            No retorna ningun valor.
        """

        self._create_sample_rifa()

        response = self.client.post(
            "/api/v1/rifas",
            json={
                "numero": 1,
                "nombre": "Duplicada",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["error"]["message"],
            "Ya existe una rifa con ese numero.",
        )

    def test_invalid_nombre_returns_400(self) -> None:
        """Verifica que `nombre` no admita null ni strings vacios.

        Returns:
            No retorna ningun valor.
        """

        empty_response = self.client.post(
            "/api/v1/rifas",
            json={
                "numero": 2,
                "nombre": "   ",
            },
        )
        null_response = self.client.post(
            "/api/v1/rifas",
            json={
                "numero": 3,
                "nombre": None,
            },
        )

        self.assertEqual(empty_response.status_code, 400)
        self.assertEqual(null_response.status_code, 400)

    def test_invalid_mail_returns_400(self) -> None:
        """Verifica que el mail tenga formato basico valido.

        Returns:
            No retorna ningun valor.
        """

        response = self.client.post(
            "/api/v1/rifas",
            json={
                "numero": 4,
                "nombre": "Ana",
                "mail": "mail-invalido",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["error"]["message"],
            "El campo 'mail' debe tener un formato valido.",
        )

    def test_missing_resource_returns_404(self) -> None:
        """Verifica que los recursos inexistentes devuelvan 404.

        Returns:
            No retorna ningun valor.
        """

        get_response = self.client.get("/api/v1/rifas/999")
        put_response = self.client.put(
            "/api/v1/rifas/999",
            json={"nombre": "Inexistente"},
        )
        patch_response = self.client.patch(
            "/api/v1/rifas/999",
            json={"nombre": "Inexistente"},
        )
        delete_response = self.client.delete("/api/v1/rifas/999")

        self.assertEqual(get_response.status_code, 404)
        self.assertEqual(put_response.status_code, 404)
        self.assertEqual(patch_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)

    def test_numero_is_immutable_in_put_and_patch(self) -> None:
        """Verifica que `numero` no pueda cambiarse desde el body.

        Returns:
            No retorna ningun valor.
        """

        self._create_sample_rifa()

        put_response = self.client.put(
            "/api/v1/rifas/1",
            json={
                "numero": 2,
                "nombre": "Cambio",
            },
        )
        patch_response = self.client.patch(
            "/api/v1/rifas/1",
            json={
                "numero": 3,
                "nombre": "Cambio parcial",
            },
        )

        self.assertEqual(put_response.status_code, 400)
        self.assertEqual(patch_response.status_code, 400)

    def test_timestamp_is_persisted(self) -> None:
        """Verifica que el timestamp se mantenga estable luego de updates.

        Returns:
            No retorna ningun valor.
        """

        create_response = self.client.post(
            "/api/v1/rifas",
            json={
                "numero": 7,
                "nombre": "Con Timestamp",
            },
        )
        created_timestamp = create_response.get_json()["data"]["timestamp"]

        update_response = self.client.patch(
            "/api/v1/rifas/7",
            json={"telefono": "123456789"},
        )
        updated_timestamp = update_response.get_json()["data"]["timestamp"]

        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(created_timestamp, updated_timestamp)
        self.assertTrue(created_timestamp.endswith("Z"))

    def _create_sample_rifa(self) -> None:
        """Crea una rifa base para reutilizar en varias pruebas.

        Returns:
            No retorna ningun valor.
        """

        response = self.client.post(
            "/api/v1/rifas",
            json={
                "numero": 1,
                "nombre": "Base",
                "telefono": "123456789",
                "mail": "base@example.com",
            },
        )
        self.assertEqual(response.status_code, 201)


if __name__ == "__main__":
    unittest.main()
