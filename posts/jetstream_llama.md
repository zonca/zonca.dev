

## Install Miniforge

```bash
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
```

conda create -y -n vllm python=3.11
conda activate vllm
pip install vllm


huggingface-cli login
vllm serve "meta-llama/Llama-3.2-1B-Instruct" --max-model-len=8192 --enforce-eager

conda create -y -n vllm python=3.11
conda activate open-webui
pip install open-webui
open-webui serve


install caddy

sudo caddy reverse-proxy --from deployllama.cis230085.projects.jetstream-cloud.org --to :8080 

chat.cis230085.projects.jetstream-cloud.org {

        reverse_proxy localhost:8080
}
