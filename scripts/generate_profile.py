import json
import os
import urllib.request
import urllib.parse
import html
from collections import Counter

USERNAME = "CainaHaniell"

API = "https://api.github.com"


def github_get(url):
    """Faz uma requisição para a API pública do GitHub."""
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "CainaHaniell-Profile-Stats",
        },
    )

    token = os.environ.get("GITHUB_TOKEN")

    if token:
        request.add_header("Authorization", f"Bearer {token}")

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def get_user():
    return github_get(f"{API}/users/{USERNAME}")


def get_repositories():
    repositories = []
    page = 1

    while True:
        url = (
            f"{API}/users/{USERNAME}/repos"
            f"?per_page=100&page={page}&type=owner"
        )

        data = github_get(url)

        if not data:
            break

        repositories.extend(data)

        if len(data) < 100:
            break

        page += 1

    return repositories


def get_language_statistics(repositories):
    languages = Counter()

    for repository in repositories:
        if repository["fork"]:
            continue

        languages_url = repository["languages_url"]

        try:
            data = github_get(languages_url)

            for language, bytes_count in data.items():
                languages[language] += bytes_count

        except Exception as error:
            print(f"Could not read languages: {error}")

    return languages


def get_commit_count():
    """
    Usa a busca pública do GitHub para estimar a quantidade
    de commits atribuídos ao usuário.
    """

    query = urllib.parse.quote(f"author:{USERNAME}")

    url = (
        f"{API}/search/commits"
        f"?q={query}&per_page=1"
    )

    try:
        data = github_get(url)
        return data.get("total_count", 0)
    except Exception as error:
        print(f"Could not read commits: {error}")
        return 0


def format_number(number):
    if number >= 1000000:
        return f"{number / 1000000:.1f}M"

    if number >= 1000:
        return f"{number / 1000:.1f}K"

    return str(number)


def escape(value):
    return html.escape(str(value))


def generate_analytics(user, repositories, languages, commits):
    total_stars = sum(
        repository["stargazers_count"]
        for repository in repositories
        if not repository["fork"]
    )

    total_forks = sum(
        repository["forks_count"]
        for repository in repositories
        if not repository["fork"]
    )

    public_repositories = user["public_repos"]

    top_languages = languages.most_common(5)

    language_text = " • ".join(
        f"{language} {format_number(amount)}"
        for language, amount in top_languages
    )

    if not language_text:
        language_text = "Python"

    svg = f'''<svg
        xmlns="http://www.w3.org/2000/svg"
        width="900"
        height="330"
        viewBox="0 0 900 330">

        <defs>
            <linearGradient id="bg" x1="0" x2="1">
                <stop offset="0%" stop-color="#020605"/>
                <stop offset="50%" stop-color="#071a16"/>
                <stop offset="100%" stop-color="#020605"/>
            </linearGradient>

            <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="blur"/>
                <feMerge>
                    <feMergeNode in="blur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>

        <rect
            width="900"
            height="330"
            rx="18"
            fill="url(#bg)"
            stroke="#00ff9c"
            stroke-width="1"/>

        <text
            x="40"
            y="45"
            fill="#00ff9c"
            font-family="monospace"
            font-size="21"
            font-weight="bold">
            CAINÃ HANIELL // GITHUB ANALYTICS
        </text>

        <text
            x="40"
            y="72"
            fill="#718a83"
            font-family="monospace"
            font-size="13">
            SYSTEM METRICS // LIVE PROFILE DATA
        </text>

        <line
            x1="40"
            y1="92"
            x2="860"
            y2="92"
            stroke="#00ff9c"
            opacity="0.35"/>

        <g font-family="monospace">

            <text x="55" y="130"
                fill="#718a83"
                font-size="12">
                REPOSITORIES
            </text>

            <text x="55" y="162"
                fill="#ffffff"
                font-size="28"
                font-weight="bold">
                {public_repositories}
            </text>


            <text x="250" y="130"
                fill="#718a83"
                font-size="12">
                FOLLOWERS
            </text>

            <text x="250" y="162"
                fill="#ffffff"
                font-size="28"
                font-weight="bold">
                {user["followers"]}
            </text>


            <text x="445" y="130"
                fill="#718a83"
                font-size="12">
                FOLLOWING
            </text>

            <text x="445" y="162"
                fill="#ffffff"
                font-size="28"
                font-weight="bold">
                {user["following"]}
            </text>


            <text x="640" y="130"
                fill="#718a83"
                font-size="12">
                STARS
            </text>

            <text x="640" y="162"
                fill="#ffffff"
                font-size="28"
                font-weight="bold">
                {total_stars}
            </text>


            <text x="55" y="205"
                fill="#718a83"
                font-size="12">
                COMMITS INDEXED
            </text>

            <text x="55" y="235"
                fill="#ffffff"
                font-size="24"
                font-weight="bold">
                {format_number(commits)}
            </text>


            <text x="250" y="205"
                fill="#718a83"
                font-size="12">
                FORKS
            </text>

            <text x="250" y="235"
                fill="#ffffff"
                font-size="24"
                font-weight="bold">
                {total_forks}
            </text>


            <text x="445" y="205"
                fill="#718a83"
                font-size="12">
                PRIMARY FOCUS
            </text>

            <text x="445" y="235"
                fill="#00ff9c"
                font-size="19"
                font-weight="bold">
                Python / Backend
            </text>


            <text x="55" y="278"
                fill="#718a83"
                font-size="12">
                LANGUAGES DETECTED
            </text>

            <text x="55" y="302"
                fill="#00ff9c"
                font-size="14">
                {escape(language_text)}
            </text>

        </g>

        <circle
            cx="850"
            cy="40"
            r="5"
            fill="#00ff9c"
            filter="url(#glow)"/>

    </svg>
    '''

    return svg


def generate_trophies(user, repositories, languages, commits):
    total_stars = sum(
        repository["stargazers_count"]
        for repository in repositories
        if not repository["fork"]
    )

    repository_count = user["public_repos"]
    followers = user["followers"]
    language_count = len(languages)

    trophies = [
        (
            "PYTHON JOURNEY",
            "Python repository detected",
            any(
                "python" in (repository.get("language") or "").lower()
                for repository in repositories
            ),
        ),
        (
            "REPOSITORY BUILDER",
            f"{repository_count} public repositories",
            repository_count >= 5,
        ),
        (
            "COMMIT ENGINE",
            f"{format_number(commits)} commits indexed",
            commits >= 50,
        ),
        (
            "STAR COLLECTOR",
            f"{total_stars} stars received",
            total_stars >= 1,
        ),
        (
            "COMMUNITY SIGNAL",
            f"{followers} followers",
            followers >= 10,
        ),
        (
            "MULTI-LANGUAGE",
            f"{language_count} languages detected",
            language_count >= 2,
        ),
    ]

    cards = []

    x_positions = [35, 325, 615]
    y_positions = [100, 205]

    index = 0

    for title, description, unlocked in trophies:
        x = x_positions[index % 3]
        y = y_positions[index // 3]

        if unlocked:
            border = "#00ff9c"
            title_color = "#00ff9c"
            status = "UNLOCKED"
            status_color = "#00ff9c"
        else:
            border = "#263d37"
            title_color = "#718a83"
            status = "LOCKED"
            status_color = "#465c56"

        cards.append(
            f'''
            <rect
                x="{x}"
                y="{y}"
                width="250"
                height="80"
                rx="10"
                fill="#050b09"
                stroke="{border}"
                stroke-width="1"/>

            <text
                x="{x + 18}"
                y="{y + 27}"
                fill="{title_color}"
                font-family="monospace"
                font-size="13"
                font-weight="bold">
                {escape(title)}
            </text>

            <text
                x="{x + 18}"
                y="{y + 48}"
                fill="#718a83"
                font-family="monospace"
                font-size="10">
                {escape(description)}
            </text>

            <text
                x="{x + 18}"
                y="{y + 67}"
                fill="{status_color}"
                font-family="monospace"
                font-size="9"
                font-weight="bold">
                [{status}]
            </text>
            '''
        )

        index += 1

    svg = f'''
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="900"
        height="315"
        viewBox="0 0 900 315">

        <defs>
            <linearGradient id="bg" x1="0" x2="1">
                <stop offset="0%" stop-color="#020605"/>
                <stop offset="50%" stop-color="#071a16"/>
                <stop offset="100%" stop-color="#020605"/>
            </linearGradient>
        </defs>

        <rect
            width="900"
            height="315"
            rx="18"
            fill="url(#bg)"
            stroke="#00ff9c"
            stroke-width="1"/>

        <text
            x="35"
            y="42"
            fill="#00ff9c"
            font-family="monospace"
            font-size="21"
            font-weight="bold">
            CAINÃ HANIELL // TROPHIES
        </text>

        <text
            x="35"
            y="67"
            fill="#718a83"
            font-family="monospace"
            font-size="12">
            PERSONAL ACHIEVEMENT PROTOCOL
        </text>

        {''.join(cards)}

    </svg>
    '''

    return svg


def main():
    os.makedirs("assets", exist_ok=True)

    print("Loading GitHub profile...")

    user = get_user()
    repositories = get_repositories()
    languages = get_language_statistics(repositories)
    commits = get_commit_count()

    print(f"Repositories: {user['public_repos']}")
    print(f"Followers: {user['followers']}")
    print(f"Commits indexed: {commits}")

    analytics = generate_analytics(
        user,
        repositories,
        languages,
        commits,
    )

    trophies = generate_trophies(
        user,
        repositories,
        languages,
        commits,
    )

    with open(
        "assets/github-analytics.svg",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(analytics)

    with open(
        "assets/github-trophies.svg",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(trophies)

    print("Profile SVGs generated successfully.")


if __name__ == "__main__":
    main()
