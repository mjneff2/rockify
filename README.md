# Rockify

Rockify is a web app for getting interesting information and recommendations regarding songs within the rock genre on Spotify.

# Dev Setup

Create a virtual environment with python version >3.8. I use `conda` for this

```zsh
conda create -n rockify python=3.8
conda activate rockify
```

Install the requirements

```zsh
pip install -r requirements.txt
```
Create a config_data.py file that looks like
```python
client_id="CLIENT_ID_FROM_DEV_ACCOUNT"
client_secret="CLIENT_SECRET_FROM_DEV_ACCOUNT"
```
