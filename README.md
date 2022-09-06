# ephemeral python

Create ephemeral IPython sessions with dependencies isolated in virtual
environments.

## Challenge

Often one wants to explore a python dependency without interfering with
their current environments. The workflow is often:

```
# I don't want to mess up my current environment, so create a new one
cd /tmp
python -m venv ./venv
source ./venv/bin/activate
pip install IPython <dependencies...>
In [1]: ...
deactivate
```

Instead, after installing this package, the user can run:

```
ephemeral-python <dependencies...>
In [1]: ...
```

## Advantages

* Environments are isolated from each other, and don't interfere with
  the current environment.
* Environments are re-used if the same package list is supplied.

## Installation

`pipx install git+https//github.com/mindriot101/ephemeral-python`

vim: ft=72
