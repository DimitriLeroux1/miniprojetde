
from unittest.mock import patch, MagicMock

from botocore.exceptions import EndpointConnectionError

from src.s3_client import download_file


def test_download_retry():
    fake_content = b"transaction_id,montant\nT001,1000\n"

    fake_body = MagicMock()
    fake_body.read.return_value = fake_content

    fake_client = MagicMock()

    # Première tentative : erreur réseau.
    # Deuxième tentative : réussite.
    fake_client.get_object.side_effect = [
        EndpointConnectionError(
            endpoint_url="http://localhost:9000"
        ),
        {"Body": fake_body},
    ]

    with patch(
        "src.s3_client.get_s3_client",
        return_value=fake_client
    ):
        result = download_file("transactions/test.csv")

    assert result == fake_content
    assert fake_client.get_object.call_count == 2
