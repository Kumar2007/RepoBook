# 📚 RepoBook

RepoBook is a simple, interactive CLI tool that lets you manage GitHub repository links like a digital phone book. Great for keeping track of cool projects!

## ✨ Features

- ✅ Add GitHub repos with tags and auto-generate a neat `README.md` file listing all saved repos with metadata
- 🔍 Search by tag or name
- 📜 Optional metadata fetching via GitHub API (stars, description, etc.) using `--fetch`
- ❌ Delete by index
- 💾 Saved locally in `repos.json`

## 📦 Installation

git clone https://github.com/yourusername/repobook.git
cd repobook
pip install -r requirements.txt


## Usage

 Add repos with sections
python repobook.py add https://github.com/psf/requests --fetch --tags python http --section Networking
python repobook.py add https://github.com/torvalds/linux --tags os kernel --section OperatingSystems

 List
python repobook.py list

 Search
python repobook.py search python

 Delete
python repobook.py delete 1
