# Podsumowywator Hackathon Backend

## Installing Python Environment

### 1. Install pyenv Dependencies
First, install the required system packages:
```bash
sudo apt-get update
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
libffi-dev liblzma-dev
```

### 2. Install pyenv
Install pyenv using the installer script:
```bash
curl https://pyenv.run | bash
```

### 3. Configure Shell Environment
Add the following to your `~/.bashrc`:
```bash
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
eval "$(pyenv virtualenv-init -)"
```

### 4. Apply Shell Changes
Either restart your terminal or run:
```bash
source ~/.bashrc
```

### 5. Install and Configure Python

1. Install Python 3.11:
   ```bash
   pyenv install 3.11
   ```
2. Set Python 3.11 as default:
   ```bash
   pyenv global 3.11
   ```
3. Set Python 3.11 for this project:
   ```bash
   cd bbackend  # Make sure you're in the project directory
   pyenv local 3.11
   ```
4. Verify the Python version:
   ```bash
   python --version  # Should show Python 3.11.x
   ```

### 6. Install Poetry

1. Install Poetry using the official installer:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Add Poetry to your PATH in `~/.bashrc`:
```bash
export PATH="/home/$USER/.local/bin:$PATH"
```

3. Apply the PATH changes:
```bash
source ~/.bashrc
```

4. Verify Poetry installation:
```bash
poetry --version
```

5. Initialize the project (if not already initialized):
```bash
cd bbackend  # Make sure you're in the project directory
poetry install  # Install dependencies from pyproject.toml
```
