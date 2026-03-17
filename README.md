Repositório para atividades e trabalhos da disciplina de Planejamento de Movimento de Robôs do PPGEE/UFMG.

## Submodules

Este repositório utiliza submodules Git. Ao clonar, use:

```bash
git clone --recurse-submodules <url-do-repositório>
```

Ou, se já clonou sem os submodules:

```bash
git submodule init
git submodule update
```

Para atualizar o submodule para a versão mais recente:

```bash
git submodule update --remote TangentBug
```

## TangentBug

Implementação do algoritmo Tangent Bug para navegação de robôs.

Para executar:

```bash
cd TangentBug
pip install -r requirements.txt
python app.py
# Acesse http://localhost:5000
```
