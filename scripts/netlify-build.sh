#!/usr/bin/env bash
set -euo pipefail

QUARTO_VERSION="${QUARTO_VERSION:-1.4.551}"
QUARTO_DIR=".netlify/quarto-${QUARTO_VERSION}"

install_quarto() {
  local url="https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.tar.gz"
  echo "Installing Quarto ${QUARTO_VERSION} from ${url}"
  rm -rf "${QUARTO_DIR}"
  mkdir -p "${QUARTO_DIR}"
  curl -sSL "${url}" -o /tmp/quarto.tar.gz
  tar -xzf /tmp/quarto.tar.gz -C "${QUARTO_DIR}" --strip-components=1
}

ensure_quarto() {
  if command -v quarto >/dev/null 2>&1; then
    echo "Using existing Quarto: $(quarto --version | head -n1)"
    QUARTO_BIN="$(command -v quarto)"
    export PATH="$(dirname "${QUARTO_BIN}"):${PATH}"
    return
  fi

  if [ ! -x "${QUARTO_DIR}/bin/quarto" ]; then
    install_quarto
  else
    echo "Using cached Quarto ${QUARTO_VERSION} in ${QUARTO_DIR}"
  fi

  export PATH="${PWD}/${QUARTO_DIR}/bin:${PATH}"
}

ensure_quarto
quarto --version

make render
