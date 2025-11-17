from github import Github
import json
import os


def get_repo():
    """
    Retorna o repositório do GitHub configurado pelas variáveis de ambiente.
    """
    token = os.getenv("GITHUB_TOKEN")
    user = os.getenv("GITHUB_USER")
    repo_name = os.getenv("GITHUB_REPO")

    if not all([token, user, repo_name]):
        raise ValueError("As variáveis GITHUB_TOKEN, GITHUB_USER e GITHUB_REPO precisam estar configuradas.")

    g = Github(token)
    return g.get_user(user).get_repo(repo_name)


def salvar_dados_json(filename, data):
    """
    Cria ou atualiza um arquivo JSON no repositório GitHub.
    """
    repo = get_repo()
    path = f"data/{filename}.json"
    content = json.dumps(data, indent=4, ensure_ascii=False)

    try:
        file = repo.get_contents(path)
        repo.update_file(
            path,
            f"Atualiza {filename}.json",
            content,
            file.sha
        )
    except Exception:
        repo.create_file(
            path,
            f"Cria {filename}.json",
            content
        )


def ler_dados_json(filename):
    """
    Lê e retorna os dados de um arquivo JSON do repositório GitHub.
    Retorna uma lista vazia se o arquivo não existir.
    """
    repo = get_repo()
    path = f"data/{filename}.json"

    try:
        file = repo.get_contents(path)
        return json.loads(file.decoded_content.decode())
    except Exception:
        return []
