from app.config import Settings


def test_settings_can_read_config_yaml(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tmp_path.joinpath("config.yaml").write_text(
        "\n".join(
            [
                "environment: test-yaml",
                "accept_threshold: 20",
                "reject_threshold: 80",
            ]
        )
    )

    settings = Settings()

    assert settings.environment == "test-yaml"
    assert settings.accept_threshold == 20
    assert settings.reject_threshold == 80


def test_environment_variables_override_config_yaml(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("FRAUD_API_ACCEPT_THRESHOLD", "45")
    tmp_path.joinpath("config.yaml").write_text("accept_threshold: 20\n")

    settings = Settings()

    assert settings.accept_threshold == 45
