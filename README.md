# podsumowywator2

## Setup

### Install asdf

- Visit https://github.com/asdf-vm/asdf/releases and download the appropriate archive for your operating system/architecture combination.
- Extract the asdf binary in the archive into a directory on your $PATH.
- Verify asdf is on your shell's $PATH by running type -a asdf. The directory you placed the asdf binary in should be listed on the first line of the output from type. If it is not that means step #2 was not completed correctly.

### Install nodejs and python

```
asdf plugin add nodejs
asdf plugin add python
asdf install
```