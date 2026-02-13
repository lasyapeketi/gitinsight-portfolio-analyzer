from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    data = None
    error = None

    if request.method == 'POST':
        username = request.form['username'].strip()

        if not username:
            return render_template('index.html', data=None, error="Enter a username")

        score = 0
        suggestions = []

        # USER DATA
        user_url = f"https://api.github.com/users/{username}"
        user_res = requests.get(user_url).json()

        if user_res.get("message") == "Not Found":
            return render_template('index.html', data=None, error="User not found")

        repos = user_res.get('public_repos', 0)
        followers = user_res.get('followers', 0)
        bio = user_res.get('bio')

        # REPOS
        repos_url = f"https://api.github.com/users/{username}/repos"
        repo_res = requests.get(repos_url).json()

        if not isinstance(repo_res, list):
            return render_template('index.html', data=None, error="Repo data unavailable")

        repo_data = repo_res

        # LANGUAGES
        languages = set()
        for repo in repo_data:
            if repo.get("language"):
                languages.add(repo["language"])

        # README
        readme_count = 0
        for repo in repo_data[:5]:
            repo_name = repo["name"]
            readme_url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
            r = requests.get(readme_url)
            if r.status_code == 200:
                readme_count += 1

        # ACTIVITY
        recent_active = False
        for repo in repo_data:
            if repo.get("updated_at") and "202" in repo["updated_at"]:
                recent_active = True

        # SCORING
        if repos > 5:
            score += 40
        else:
            suggestions.append("Create more repositories")

        if followers > 10:
            score += 30
        else:
            suggestions.append("Increase profile visibility")

        if bio:
            score += 30
        else:
            suggestions.append("Add a profile bio")

        if recent_active:
            score += 10
        else:
            suggestions.append("Be more active on GitHub")

        if readme_count > 0:
            score += 10
        else:
            suggestions.append("Add README files")

        # DATA FOR HTML
        data = {
            "repos": repos,
            "followers": followers,
            "score": score,
            "bio": bio,
            "languages": list(languages),
            "readmes": readme_count,
            "active": recent_active,
            "suggestions": suggestions
        }

    return render_template('index.html', data=data, error=error)

app.run(debug=True)
