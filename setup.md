# Setup

## Testing without MongoDB

Tested with `conda 25.5.1`.

To set up the environment, run the following commands:

```bash
conda create -n fw python=3.12 pip
conda activate fw
pip install -r requirements.txt
```

Copy `.env.template` to `.env` and fill in the required environment variables.

```bash
cp .env.template .env
```

Run JupyterLab, initialize the vector database, and run the smoke test by executing the cells in `chatbot.ipynb`:

```bash
jupyter lab ./Chatbot_ver2/chatbot.ipynb
```

This will take some time as it populates the vector database with documents.
