!curl https://ollama.ai/install.sh | sh


!wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
!tar xvzf ngrok-v3-stable-linux-amd64.tgz ngrok

!ollama pull qwen3:8b

!./ngrok authtoken 2WXjRlUnmO22B4BGVqoCh0hyNf8_byMLUNZvu6Lhg9gzb2Ca
!ollama serve & ./ngrok http 11434 --host-header="localhost:11434" --log stdout & sleep 5s && ollama run qwen3:8b