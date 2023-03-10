from requests import get
import unittest
from codecs import open
from os import path
"""para otimização de desempenho poderia-se usar import de Session e instanciar um objeto desta classe ao invés de usar
diretamente get(), assim evitaríamos um three-way-handshake a cada get feito após o primeiro"""


class User:
    """Poderia-se usar data classes para otimizar futuras alterações nesta classe.
    A definição da classe poderia ficar em outro arquivo para fins de organização, porém, sendo esta classe uma
    implementação simples, optei por deixar neste mesmo arquivo.
    O campo login poderia ser substituído pelo username fornecido para a busca, porém optei por preenchê-lo de forma
    mais padronizada neste caso."""
    def __init__(self, login: str = None, name: str = None, html_url: str = None, public_repos: int = None,
                 followers: int = None, following: int = None):
        self.login = login
        self.name = name
        self.html_url = html_url
        self.public_repos = public_repos
        self.followers = followers
        self.following = following

    def __repr__(self):
        return '%s, %s, %s, %s, %s, %s' % (self.login, self.name, self.html_url, self.public_repos, self.followers,
                                           self.following)


def get_user(username: str) -> User:
    try:
        data = get('https://api.github.com/users/%s' % username, headers={'Accept': 'application/vnd.github+json'}).json()
        return User(login=data['login'], name=data['name'], html_url=data['html_url'],
                    public_repos=data['public_repos'],
                    followers=data['followers'], following=data['following'])
    # exception nesse caso não especificada pois qualquer exception teria como resultado um usuário vazio retornado
    # em caso de maior especificação poderia-se usar vários tipos de exceptions e várias outras ações
    except:
        return User()


def get_user_repos(username: str) -> dict:
    try:
        data = get('https://api.github.com/users/%s/repos' % username,
                   headers={'Accept': 'application/vnd.github+json'}).json()
        # dict comprehension usado neste caso para facilitar o desenvolvimento
        return {repo['name']: repo['html_url'] for repo in data}
    # exception não especificada pois qualquer erro nesta função geraria este resultado assim como no caso anterior
    except:
        return {None: None}


def user_report(user: User, repos: dict) -> None:
    """poderia-se usar apenas username como parâmetro de entrada, assim chamaríamos dentro desta função as outras duas
    definidas anteriormente e previniríamos um possível report com um user usando repositórios de outro"""
    with open('%s.txt' % user.login, 'w', 'utf-8') as text_file:
        text_file.write('Nome: %s\n'
                        'Perfil: %s\n'
                        'Número de repositórios publicos: %s\n'
                        'Número de seguidores: %s\n'
                        'Número de usuários seguidos: %s\n'
                        'Repositórios:\n' % (user.name, user.html_url, user.public_repos, user.followers,
                                             user.following))
        for repo, url in repos.items():
            text_file.write('\t%s: %s\n' % (repo, url))     # \t adicionado para fins estéticos nesse caso


class TestMethods(unittest.TestCase):

    def test_user_class_has_minimal_parameters(self):
        parameters = ['name', 'html_url', 'public_repos', 'followers', 'following']
        user = get_user('ArthurLOliveira')
        for param in parameters:
            self.assertTrue(hasattr(user, param))

    def test_user_exists(self):
        user = get_user('ArthurLOliveira')
        self.assertIsNotNone(user.name)

    def test_user_url_works(self):
        user = get_user('ArthurLOliveira')
        self.assertEqual(get(user.html_url).status_code, 200)

    def test_user_repos_exist(self):
        repos = get_user_repos('ArthurLOliveira')
        self.assertNotEqual(repos, {None: None})

    def test_report_generated(self):
        username = 'ArthurLOliveira'
        user_report(get_user(username), get_user_repos(username))
        self.assertTrue(path.exists('%s.txt' % username))

    def test_report_matches_repos_owner(self):
        # assumindo que o usuário tenha pelo menos um repositório neste caso
        username = 'ArthurLOliveira'
        data = get_user(username)   # pode-se alterar este parâmetro por outro user para verificar este teste
        repos = get_user_repos(username)    # pode-se alterar este parâmetro por outro user para verificar este teste
        user_report(data, repos)
        with open('%s.txt' % username, 'r') as report:
            # existem muitas formas de se chegar à linha que inclui o primeiro repositório, optei por indice direto
            # pois a primeira parte do arquivo tem sempre o mesmo número de linhas
            self.assertEqual(username, report.readlines()[6].split('.com/')[1].split('/')[0])


if __name__ == '__main__':
    unittest.main()
