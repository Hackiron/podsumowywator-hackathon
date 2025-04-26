# podsumowywator2

## Setup

### Requirements

- Registered Discord bot and it's API token.
- OpenAI API key.
- FireCrawl API key.

### Install asdf

- Visit https://github.com/asdf-vm/asdf/releases and download the appropriate archive for your operating system/architecture combination.
- Extract the asdf binary in the archive into a directory on your $PATH.
- Verify asdf is on your shell's $PATH by running type -a asdf. The directory you placed the asdf binary in should be listed on the first line of the output from type. If it is not that means step #2 was not completed correctly.

### Install nodejs, python, direnv

```
asdf plugin add nodejs
asdf plugin add python
asdf plugin add direnv
asdf install
```

Enable direnv

```
direnv allow .
```

### Env

Copy `.env.example` to `.env` and fill it.

### Setup backend

See [./bbackend/README.md](./bbackend/README.md) starting from point 6.

### Setup frontend

Run

```
npm ci
```

### Development

Start backend and frontend processes separately


Backend:

```
cd bbackend && make
```

Frontend

```
npm run dev
```
